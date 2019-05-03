import warnings
from typing import Type, Union


def will_be_removed(
    deprecated_name: str,
    use_instead: Union[str, Type],
    removing_in_version: str,
    stacklevel=2,
):
    new_class_name = (
        use_instead.__name__  # type: ignore
        if isinstance(use_instead, Type)  # type: ignore
        else use_instead
    )
    warnings.warn(
        f"Please use {new_class_name} instead, "
        f"{deprecated_name} will be removed in happyly v{removing_in_version}.",
        DeprecationWarning,
        stacklevel=stacklevel,
    )
