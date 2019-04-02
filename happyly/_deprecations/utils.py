import warnings


def will_be_removed(
    deprecated_name: str, use_instead, removing_in_version: str, stacklevel=2
):
    warnings.warn(
        f"Please use {use_instead.__name__} instead, "
        f"{deprecated_name} will be removed in happyly v{removing_in_version}.",
        DeprecationWarning,
        stacklevel=stacklevel,
    )
