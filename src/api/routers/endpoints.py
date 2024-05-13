"""
Base router.
"""

import base64
import io
import logging
import uuid
from collections import defaultdict

import aiocsv
import aiofiles
import fastapi
import fastapi_injector
from dateutil import parser

from api import ports
from api.domain import xes

from . import schemas

router = fastapi.APIRouter()

logger = logging.getLogger(__name__)


@router.get("/healthz")
def healthz() -> fastapi.Response:
    """
    Health check to see if it's able to receive more transactions.
    """
    return fastapi.Response(status_code=200, content="OK")


@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: uuid.UUID,
    tasks: ports.MemoryStorage = fastapi_injector.Injected(ports.MemoryStorage),
) -> fastapi.Response:
    task = tasks.get(task_id)
    if task is None:
        return fastapi.responses.JSONResponse(
            status_code=404, content={"status": "not_found"}
        )
    return fastapi.responses.JSONResponse(status_code=200, content=task)


@router.post("/signed")
async def generate_signed_url(
    body: schemas.GetSignedUrl = fastapi.Body(...),
    storage: ports.Storage = fastapi_injector.Injected(ports.Storage),
) -> dict[str, str]:
    path = f"raw/{body.file_name}"
    signed_url = await storage.generate_signed_url(path, body.mimetype)
    return {
        "url": signed_url,
    }


@router.post("/convert")
async def convert(
    publisher: ports.MessagePublisher = fastapi_injector.Injected(
        ports.MessagePublisher
    ),
    tasks: ports.MemoryStorage = fastapi_injector.Injected(ports.MemoryStorage),
    body: schemas.ConvertXES = fastapi.Body(...),
) -> schemas.ConvertXESResponse:
    task_id = uuid.uuid4()
    await publisher.publish(
        schemas.ConvertAsyncTask(
            task_id=task_id,
            url=body.file,
            email_address=body.email_address,
            keys=body.keys,
            delimiter=body.delimiter,
        )
    )
    tasks.set(task_id, {"status": "processing"})
    return schemas.ConvertXESResponse(
        task_id=task_id,
        status="processing",
    )


@router.post("/_pubsub")
async def async_convert(
    pubsub_body: schemas.PubsubRequest = fastapi.Body(...),
    tasks: ports.MemoryStorage = fastapi_injector.Injected(ports.MemoryStorage),
    storage: ports.Storage = fastapi_injector.Injected(ports.Storage),
) -> fastapi.Response:
    """
    Convert the file to a different format.
    """
    body = schemas.AsyncTaskRequest.parse_raw(
        base64.b64decode(pubsub_body.message.data.decode("utf-8"))
    )
    file_data = body.url
    _, file_name = file_data.rsplit("/", 1)
    file_stripped = (
        file_data.replace("https://", "")
        .replace("http://", "")
        .replace("storage.googleapis.com/", "")
        .replace("storage.cloud.google.com/", "")
    )
    file_path = await storage.download(f"gs://{file_stripped}", file_name)
    traces = defaultdict(list)
    xes_tracker = xes.XES()

    xes_tracker.use_default_extensions = True
    xes_tracker.classifiers = [
        xes.Classifier(name="Event Name", keys="concept:name"),
        xes.Classifier(
            name="(Event Name AND Lifecycle transition)",
            keys="concept:name lifecycle:transition",
        ),
    ]
    mapping = body.keys
    case_column = mapping.pop("concept:id")
    async with aiofiles.open(file_path, encoding="utf-8") as f:
        reader = aiocsv.AsyncDictReader(f, delimiter=body.delimiter)
        async for row in reader:
            event_data = {}
            case_id = row.pop(case_column)
            for key, to_key in mapping.items():
                event_data[key] = row.pop(to_key)
            for k, v in row.items():
                event_data[k] = v
            traces[case_id].append(event_data)
    for trace_id in traces:
        t = xes.Trace()
        t.attributes = [
            xes.Attribute(type="string", key="concept:name", value=trace_id)
        ]
        event: dict[str, str]
        for event in traces[trace_id]:
            e = xes.Event()
            date = parser.parse(event.pop("time:timestamp"))
            e.attributes = [
                xes.Attribute(
                    type="string", key="concept:name", value=event.pop("concept:name")
                ),
                xes.Attribute(
                    type="date", key="time:timestamp", value=date.isoformat()
                ),
                *[
                    xes.Attribute(type="string", key=k, value=v)
                    for k, v in event.items()
                ],
            ]
            t.add_event(e)
        xes_tracker.add_trace(t)
    with io.BytesIO() as xes_file:
        xes_file.write(str(xes_tracker).encode("utf-8"))
        upload_name = f"{file_name.rsplit('.')[0]}.xes"
        await storage.upload_by_text(
            upload_name, xes_file.getvalue(), content_type="application/xml+xes"
        )
    url = await storage.generate_signed_url(
        upload_name, mimetype="application/xml+xes", method="GET"
    )
    tasks.set(body.task_id, {"status": "done", "url": url})
    return fastapi.Response(status_code=200)
