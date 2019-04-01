from attr import attrs


@attrs(auto_attribs=True, auto_exc=True)  # type: ignore
class StopPipeline(Exception):
    reason: str = ''
