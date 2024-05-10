from api.domain import xes
import csv
from collections import defaultdict
from dateutil import parser



traces = defaultdict(list)
xes_tracker = xes.XES()

delimiter = ","
xes_tracker.use_default_extensions = True
xes_tracker.classifiers = [
    xes.Classifier(name="Event Name", keys="concept:name"),
    xes.Classifier(name="(Event Name AND Lifecycle transition)", keys="concept:name lifecycle:transition"),
]
mapping = {
    "concept:id": ("IdeNucleoCEG", ""),
    "concept:name": ("Activity_Name", ""),
    "time:timestamp": ("Timestamp", ""),
    "lifecycle:transition": ("lifecycle:transition", "complete"),
}
case_column = mapping.pop("concept:id")[0]
with open("usina-unpivot.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=delimiter)
    for row in reader:
        event_data = {}
        case_id = row.pop(case_column)
        for key, (to_key, default) in mapping.items():
            event_data[key] = row.pop(to_key, default)
        for k, v in row.items():
            if v:
                event_data[k] = v
        traces[case_id].append(event_data)

for trace_id in traces.keys():
    t = xes.Trace()
    t.attributes = [xes.Attribute(type="string", key="concept:name", value=trace_id)]
    for event in traces.get(trace_id):
        e = xes.Event()
        date = parser.parse(event.pop("time:timestamp"))
        e.attributes = [
            xes.Attribute(type="string", key="concept:name", value=event.pop("concept:name")),
            xes.Attribute(type="date", key="time:timestamp", value=date.isoformat()),
            *[xes.Attribute(type="string", key=k, value=v) for k, v in event.items()]
        ]
        t.add_event(e)
    xes_tracker.add_trace(t)
with open("example.xes", "w", encoding="utf-8") as f:
    f.write(str(xes_tracker))