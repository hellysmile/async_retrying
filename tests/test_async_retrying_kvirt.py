import asyncio
from functools import partial

import pytest

from async_retrying import (RetryError, callback, isexception, propagate,
                            retry, unpartial)


@pytest.mark.run_loop
@asyncio.coroutine
def test_attempts(loop):
    counter = 1

    @retry(loop=loop, attempts=5)
    @asyncio.coroutine
    def coro():
        nonlocal counter
        counter += 1
        if counter != 6:
            raise RuntimeError
        return counter

    ret = yield from coro()
    assert ret == 6


@pytest.mark.run_loop
@asyncio.coroutine
def test_ret_is_not_retry(loop):

    @asyncio.coroutine
    def callback(attempt, exc, args, kwargs, delay=0.5, *, loop):
        return 42

    @retry(loop=loop, callback=callback)
    @asyncio.coroutine
    def coro():
        raise RuntimeError

    ret = yield from coro()
    assert ret == 42


@pytest.mark.run_loop
@asyncio.coroutine
def test_isexception_true(loop):
    ret = isexception(RuntimeError)
    assert ret == True


@pytest.mark.run_loop
@asyncio.coroutine
def test_isexception_false(loop):
    ret = isexception(42)
    assert ret == False


@pytest.mark.run_loop
@asyncio.coroutine
def test_callback(loop):
    callback.delay = 0.5
    ret = yield from callback(3, Exception, (), {}, loop=loop)
    assert ret.__name__ == 'retry'


def test_unpartial():
    def fn():
        pass

    obj = partial(partial(fn))

    assert unpartial(obj).__name__ == 'fn'


@pytest.mark.run_loop
@asyncio.coroutine
def test_loop_is_none(loop):

    @retry(loop=None)
    @asyncio.coroutine
    def coro():
        raise RuntimeError

    with pytest.raises(RetryError):
        yield from coro()


@pytest.mark.run_loop
@asyncio.coroutine
def test_timeout_is_not_none(loop):

    @retry(loop=loop, timeout=0.5)
    @asyncio.coroutine
    def coro():
        yield from asyncio.sleep(1)

    with pytest.raises(RetryError):
        yield from coro()


@pytest.mark.run_loop
@asyncio.coroutine
def test_retry_error(loop):

    @retry
    @asyncio.coroutine
    def coro():
        raise RuntimeError

    with pytest.raises(RetryError):
        yield from coro()


@pytest.mark.run_loop
@asyncio.coroutine
def test_loop_cls(loop):

    class Obj:
        def __init__(self, *, loop):
            self._loop = loop

        @retry(cls=True, loop='_loop')
        @asyncio.coroutine
        def coro(self):
            raise RuntimeError

    o = Obj(loop=loop)
    with pytest.raises(RetryError):
        yield from o.coro()


@pytest.mark.run_loop
@asyncio.coroutine
def test_loop_kwargs(loop):

    @retry(kwargs=True, loop='_loop')
    @asyncio.coroutine
    def coro(*, _loop):
        raise RuntimeError
    with pytest.raises(RetryError):
        yield from coro(_loop=loop)


@pytest.mark.run_loop
@asyncio.coroutine
def test_notimplemented_error(loop):

    @asyncio.coroutine
    def coro():
        pass

    with pytest.raises(NotImplementedError):
        yield from retry(coro())


@pytest.mark.run_loop
@asyncio.coroutine
def test_callable_fallback(loop):

    @asyncio.coroutine
    def fallback(*args, **kwargs):
        return 42

    @retry(fallback=fallback)
    @asyncio.coroutine
    def coro():
        raise RuntimeError

    ret = yield from coro()
    assert ret == 42


@pytest.mark.run_loop
@asyncio.coroutine
def test_fallback_is_propagate(loop):

    @retry(fallback=propagate)
    @asyncio.coroutine
    def coro():
        raise RuntimeError

    with pytest.raises(RuntimeError):
        yield from coro()


@pytest.mark.run_loop
@asyncio.coroutine
def test_fallback_is_something_else(loop):

    @retry(fallback=42)
    @asyncio.coroutine
    def coro():
        raise RuntimeError

    ret = yield from coro()
    assert ret == 42


@pytest.mark.run_loop
@asyncio.coroutine
def test_callable_fn(loop):
    counter = 1

    @retry
    @asyncio.coroutine
    def coro():
        nonlocal counter
        counter += 1
        if counter != 4:
            raise RuntimeError
        return counter

    ret = yield from coro()
    assert ret == 4


@pytest.mark.run_loop
@asyncio.coroutine
def test_cancelled_error(loop):

    @retry
    @asyncio.coroutine
    def coro():
        yield from asyncio.sleep(1, loop=loop)

    with pytest.raises(asyncio.CancelledError):
        task = asyncio.ensure_future(coro())
        yield from asyncio.sleep(0.1, loop=loop)
        task.cancel()
        yield from task
