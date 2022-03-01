from typing import overload, Callable, Union, Type, TypeVar, Any

WrappedFn = TypeVar("WrappedFn", bound=Callable)

@overload
def retry(fn: WrappedFn) -> WrappedFn:
    pass

# def retry(exn: Type[Exception]=Exception, attempts: int=5) -> Callable[[WrappedFn], WrappedFn]:
@overload
def retry(*dargs: Any, **kwargs: Any) -> Callable[[WrappedFn], WrappedFn]:
    pass

def retry(*dargs: Any, **kwargs: Any) -> Union[Callable[[WrappedFn], WrappedFn], WrappedFn]:
    if len(dargs) == 1 and callable(dargs[0]):
        return retry()(dargs[0])
    def wrap(f: WrappedFn) -> WrappedFn:
        print('yo')
        return f
    return wrap
