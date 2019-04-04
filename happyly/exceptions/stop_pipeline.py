from attr import attrs


@attrs(auto_attribs=True, auto_exc=True)  # type: ignore
class StopPipeline(Exception):
    """
    This exception should be raised to stop a pipeline.
    After raising it, :meth:`Executor.on_stopped` will be called.
    """

    reason: str = ''
