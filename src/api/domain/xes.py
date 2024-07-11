import xml.etree.ElementTree as ET
from xml.dom import minidom


class Attribute:
    """
    An Attribute object.

    Set the type, key, and value of the attribute and
    add this attribute to a trace or the log.
    """

    def __init__(
        self,
        type: str = "not set",
        key: str = "not set",
        value: str = "not set",
    ) -> None:
        self.type = type
        self.key = key
        self.value = value

        self.xml = ET.Element(self.type)
        self.xml.set("key", key)
        if self.type.lower() not in ("list", "container"):
            self.xml.set("value", value)

    def nest_attribute(self, attribute: "Attribute") -> None:
        self.xml.append(attribute.xml)

    def __str__(self) -> str:
        result: str = ET.dump(self.xml)  # type: ignore[func-returns-value]
        return result


class Extension:
    """
    An Extension
    Used for the Log.
    """

    def __init__(
        self,
        name: str = "not set",
        prefix: str = "not set",
        uri: str = "not set",
    ) -> None:
        self.name = name
        self.prefix = prefix
        self.uri = uri

        self.xml = ET.Element("extension")
        self.xml.set("name", name)
        self.xml.set("prefix", prefix)
        self.xml.set("uri", uri)

    def __str__(self) -> str:
        result: str = ET.dump(self.xml)  # type: ignore[func-returns-value]
        return result


class Classifier:
    """
    Classifier.
    Used by the Log. Should be the main attributes of events you want to classify by.
    """

    def __init__(
        self,
        name: str = "not set",
        keys: str = "not set",
    ) -> None:
        self.name = name
        self.keys = keys

        self.xml = ET.Element("classifier")
        self.xml.set("name", name)
        self.xml.set("keys", keys)

    def __str__(self) -> str:
        result: str = ET.dump(self.xml)  # type: ignore[func-returns-value]
        return result


class Event:
    """An event class. Add attributes to an event."""

    def __init__(self) -> None:
        self.xml = ET.Element("event")
        self.attributes: list[Attribute] = []

    def add_attribute(self, attr: Attribute) -> "Event":
        self.attributes.append(attr)
        return self

    def build_event(self) -> None:
        for attribute in self.attributes:
            self.xml.append(attribute.xml)

    def __str__(self) -> str:
        result: str = ET.dump(self.xml)  # type: ignore[func-returns-value]
        return result


class Trace:
    """
    An aggregator of events.
    """

    def __init__(self) -> None:
        self.xml = ET.Element("trace")
        self.events: list[Event] = []
        self.attributes: list[Attribute] = []

    def add_attribute(self, attr: Attribute) -> None:
        self.attributes.append(attr)

    def add_event(self, event: Event) -> None:
        self.events.append(event)

    def build_trace(self) -> None:
        for attribute in self.attributes:
            self.xml.append(attribute.xml)
        for event in self.events:
            self.xml.append(event.xml)

    def __str__(self) -> str:
        result: str = ET.dump(self.xml)  # type: ignore[func-returns-value]
        return result


class XES:
    """An XES log class for adding traces to."""

    def __init__(self) -> None:
        self.log = ET.Element("log")
        self.log.set("xes.version", "2.0")
        self.log.set("xes.features", "arbitraty-depth")

        self.attributes: list[Attribute] = []
        self.traces: list[Trace] = []
        self.extensions: list[Extension] = []
        self.classifiers: list[Classifier] = []
        self.global_event_attributes: list[Event] = []
        self.global_trace_attributes: list[Trace] = []
        self.use_default_extensions = True

    def add_global_event_attribute(self, attr: Attribute) -> None:
        self.global_event_attributes.append(attr)

    def add_global_trace_attributes(self, attr: Attribute) -> None:
        self.global_trace_attributes.append(attr)

    def add_attribute(self, attr: Attribute) -> None:
        if isinstance(attr, Attribute):
            self.attributes.append(attr)

    def add_trace(self, trace: Trace) -> None:
        if isinstance(trace, Trace):
            self.traces.append(trace)

    def add_extension(self, extension: Extension) -> None:
        if isinstance(extension, Extension):
            self.extensions.append(extension)

    def add_default_extensions(self) -> None:
        self.extensions = [
            Extension(
                name="Time",
                prefix="time",
                uri="http://www.xes-standard.org/time.xesext",
            ),
            Extension(
                name="Lifecycle",
                prefix="lifecycle",
                uri="http://www.xes-standard.org/lifecycle.xesext",
            ),
            Extension(
                name="Concept",
                prefix="concept",
                uri="http://www.xes-standard.org/concept.xesext",
            ),
        ]

    def build_log(self) -> None:
        if len(self.classifiers) == 0:
            print("XES Warning! Classifiers not set. \n")

        if self.use_default_extensions:
            self.add_default_extensions()

        for extension in self.extensions:
            self.log.append(extension.xml)

        if global_trace := self.global_trace_attributes:
            trace_element = ET.SubElement(self.log, "global")
            trace_element.set("scope", "trace")
            for trace in global_trace:
                trace_element.append(trace.xml)

        if global_events := self.global_event_attributes:
            event_element = ET.SubElement(self.log, "global")
            event_element.set("scope", "event")
            for evnt in global_events:
                event_element.append(evnt.xml)

        for classifier in self.classifiers:
            self.log.append(classifier.xml)

        for attr in self.attributes:
            self.log.append(attr.xml)

        log_data = ET.SubElement(self.log, "string")
        log_data.set("key", "concept:name")
        log_data.set("value", "XES Event Log")

        for trace in self.traces:
            for event in trace.events:
                event.build_event()
            trace.build_trace()
            self.log.append(trace.xml)

    def __str__(self) -> str:
        self.build_log()
        stuff = minidom.parseString(ET.tostring(self.log, "UTF-8", method="xml"))

        return stuff.toprettyxml("  ")
