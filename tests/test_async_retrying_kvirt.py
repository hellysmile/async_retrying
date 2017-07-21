from async_retrying import (
                            retry,
                            unpartial,
                            isexception,
                            RetryError,
                            callback,
                            ConditionError,
                            propagate,
                            )
import pytest
import asyncio
from functools import partial


@pytest.mark.run_loop
@asyncio.coroutine
def test_basic(loop):
    counter = 1

    @retry(loop=loop, attempts=10)
    @asyncio.coroutine
    def coro():
        nonlocal counter
        counter += 1
        if counter != 2:
            raise RuntimeError
        return counter

    ret = yield from coro()
    assert ret == 2

@pytest.mark.run_loop
@asyncio.coroutine
def test_ret_is_not_retry(loop):
    counter = 1

    @asyncio.coroutine
    def callback(attempt, exc, args, kwargs, delay=0.5, *, loop):

        yield from asyncio.sleep(attempt * delay, loop=loop)

        return 42

    @retry(loop=loop, callback=callback)
    @asyncio.coroutine
    def coro():
        nonlocal counter
        counter += 1
        if counter != 3:
            raise RuntimeError
        return counter

    ret = yield from coro()
    assert ret != retry

@pytest.mark.run_loop
@asyncio.coroutine
def test_isexception_true(loop):
    ret = isexception(RuntimeError)
    assert ret == True

@pytest.mark.run_loop
@asyncio.coroutine
def test_isexception_false(loop):
    ret = isexception(False)
    assert ret == False

@pytest.mark.run_loop
@asyncio.coroutine
def test_callback(loop):
    callback.delay = 0.5
    ret = yield from callback(3, Exception, (), {}, loop=loop)

def test_unpartial():
    def fn():
        pass

    obj = partial(partial(fn))

    assert unpartial(obj).__name__ == 'fn'

@pytest.mark.run_loop
@asyncio.coroutine
def test_loop_is_none(loop):
    counter = 1

    @retry(loop=None)
    @asyncio.coroutine
    def coro():
        nonlocal counter
        counter += 1
        if counter != 2:
            raise RuntimeError
        return counter

    ret = yield from coro()
    assert ret == 2

@pytest.mark.run_loop
@asyncio.coroutine
def test_timeout_is_not_none(loop):
    counter = 1

    @retry(loop=loop, timeout=0.5)
    @asyncio.coroutine
    def coro():
        nonlocal counter
        counter += 1
        if counter != 2:
            raise RuntimeError
        return counter

    ret = yield from coro()
    assert ret == 2

@pytest.mark.run_loop
@asyncio.coroutine
def test_timeout_is_not_none_and_not_async(loop):
    counter = 1

    @retry(timeout=0.5)
    def coro():
        nonlocal counter
        counter += 1
        if counter != 2:
            raise RuntimeError
        return counter

    with pytest.raises(ConditionError):
        yield from coro()

@pytest.mark.run_loop
@asyncio.coroutine
def test_retry_error(loop):
    counter = 1

    @retry()
    @asyncio.coroutine
    def coro():
        nonlocal counter
        counter += 1
        if counter != 5:
            raise RuntimeError
        return counter

    with pytest.raises(RetryError):
        yield from coro()


@pytest.mark.run_loop
@asyncio.coroutine
def test_loop_cls(loop):
    counter = 1

    class Obj:
        def __init__(self, *, loop):
            self._loop = loop

        @retry(cls=True, loop='_loop')
        @asyncio.coroutine
        def coro(self):
            nonlocal counter
            counter += 1
            if counter != 2:
                raise RuntimeError
            return counter
    o = Obj(loop=loop)
    yield from o.coro()

@pytest.mark.run_loop
@asyncio.coroutine
def test_loop_kwargs(loop):
    counter = 1

    @retry(kwargs=True, loop='_loop')
    @asyncio.coroutine
    def coro(*, _loop):
        nonlocal counter
        counter += 1
        if counter != 2:
            raise RuntimeError
        return counter

    yield from coro(_loop=loop)

@pytest.mark.run_loop
@asyncio.coroutine
def test_notimplemented_error(loop):
    counter = 1

    @asyncio.coroutine
    def coro():
        nonlocal counter
        counter += 1
        if counter != 5:
            raise RuntimeError
        return counter

    with pytest.raises(NotImplementedError):
        yield from retry(coro())

@pytest.mark.run_loop
@asyncio.coroutine
def test_callable_fallback(loop):
    counter = 1

    @asyncio.coroutine
    def fallback(*args, **kwargs):
        return 42

    @retry(fallback=fallback)
    @asyncio.coroutine
    def coro():
        nonlocal counter
        counter += 1
        if counter != 5:
            raise RuntimeError
        return counter

    yield from coro()

@pytest.mark.run_loop
@asyncio.coroutine
def test_fallback_is_propagate(loop):
    counter = 1

    @retry(fallback=propagate)
    @asyncio.coroutine
    def coro():
        nonlocal counter
        counter += 1
        if counter != 5:
            raise RuntimeError
        return counter

    with pytest.raises(RuntimeError):
        yield from coro()

@pytest.mark.run_loop
@asyncio.coroutine
def test_fallback_is_something_else(loop):
    counter = 1

    @retry(fallback=42)
    @asyncio.coroutine
    def coro():
        nonlocal counter
        counter += 1
        if counter != 5:
            raise RuntimeError
        return counter

    yield from coro()
