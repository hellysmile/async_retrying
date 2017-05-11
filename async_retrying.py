import asyncio
import copy
import inspect
import logging
from functools import wraps

import async_timeout

logger = logging.getLogger(__name__)


retry = propagate = forever = ...


class RetryError(Exception):
    pass


def iscoroutinepartial(fn):
    # http://bugs.python.org/issue23519

    parent = fn

    while fn is not None:
        parent, fn = fn, getattr(parent, 'func', None)

    return asyncio.iscoroutinefunction(parent)


def unpartial(fn):
    while hasattr(fn, 'func'):
        fn = fn.func

    return fn


def isexception(obj):
    return (
        isinstance(obj, Exception) or
        (inspect.isclass(obj) and (issubclass(obj, Exception)))
    )


@asyncio.coroutine
def callback(attempt, exc, args, kwargs, delay=None, *, loop):
    if delay is None:
        delay = callback.delay

    yield from asyncio.sleep(attempt * callback.delay, loop=loop)

    return retry


callback.delay = 0.5


def retry(
    fn=None,
    *,
    attempts=3,
    immutable=False,
    cls=False,
    kwargs=False,
    callback=callback,
    fallback=RetryError,
    timeout=None,
    retry_exceptions=(Exception,),
    fatal_exceptions=(asyncio.CancelledError,),
    loop=None  # noqa
):
    def wrapper(fn):
        @wraps(fn)
        @asyncio.coroutine
        def wrapped(*fn_args, **fn_kwargs):
            if isinstance(loop, str):
                assert cls ^ kwargs, 'choose self.loop or kwargs["loop"]'

                if cls:
                    _self = getattr(unpartial(fn), '__self__', None)

                    if _self is None:
                        assert fn_args, 'seems not unbound function'
                        _self = fn_args[0]

                    _loop = getattr(_self, loop)
                elif kwargs:
                    _loop = fn_kwargs[loop]
            elif loop is None:
                _loop = asyncio.get_event_loop()
            else:
                _loop = loop

            if (
                timeout is not None and
                asyncio.TimeoutError not in retry_exceptions
            ):
                _retry_exceptions = (asyncio.TimeoutError,) + retry_exceptions
            else:
                _retry_exceptions = retry_exceptions

            attempt = 1

            if cls:
                assert fn_args

                self, *fn_args = fn_args

                fn_args = tuple(fn_args)

            while True:
                if immutable:
                    _fn_args = copy.deepcopy(fn_args)
                    _fn_kwargs = copy.deepcopy(fn_kwargs)
                else:
                    _fn_args, _fn_kwargs = fn_args, fn_kwargs

                if cls:
                    _fn_args = (self,) + _fn_args

                try:
                    ret = fn(*_fn_args, **_fn_kwargs)

                    if timeout is None:
                        if iscoroutinepartial(fn):
                            ret = yield from ret
                    else:
                        if not iscoroutinepartial(fn):
                            raise TypeError(
                                'Can\'t set timeout for non coroutinefunction',
                            )

                        with async_timeout.timeout(timeout, loop=_loop):
                            ret = yield from ret

                    return ret
                except fatal_exceptions:
                    raise
                except _retry_exceptions as exc:
                    logger.debug(
                        'Tried attempt #{attempt} from total {attempts} for {fn}'.format(  # noqa
                            fn=repr(fn),
                            attempt=attempt,
                            attempts='infinity' if attempts is forever else attempts,  # noqa
                        ),
                        exc_info=exc,
                    )

                    if (
                        _loop.get_debug() or
                        (attempts is not forever and attempt == attempts)
                    ):
                        if fallback is propagate:
                            raise exc

                        if isexception(fallback):
                            raise fallback from exc

                        if callable(fallback):
                            ret = fallback(fn_args, fn_kwargs, loop=_loop)

                            if iscoroutinepartial(fallback):
                                ret = yield from ret
                        else:
                            ret = fallback

                        return ret

                    attempt += 1

                    ret = callback(
                        attempt, exc, fn_args, fn_kwargs, loop=_loop,
                    )

                    if iscoroutinepartial(callback):
                        ret = yield from ret

                    if ret is not retry:
                        return ret

        return wrapped

    if fn is None:
        return wrapper

    if callable(fn):
        return wrapper(fn)

    raise NotImplementedError
