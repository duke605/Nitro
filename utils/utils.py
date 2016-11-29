def ignore_exception(exceptions=Exception):
    def decorator(func):
        async def new_func(*args, **kwargs):
            try:
                await func(*args, **kwargs)
            except exceptions as e:
                print('An exception occurred in function %s: %s' % (str(func), str(e)))
        return new_func
    return decorator
