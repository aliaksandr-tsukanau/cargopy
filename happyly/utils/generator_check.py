import inspect


def is_generator(handler):
    if hasattr(handler, 'handle'):  # class-based handler
        return inspect.isgeneratorfunction(handler.handle)
    else:  # func-based handler
        return inspect.isgeneratorfunction(handler)
