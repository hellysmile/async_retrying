import asyncio

from functools import partial

import pytest

from async_retrying import callback, retry


@pytest.mark.run_loop
@asyncio.coroutine
def test_smoke(loop):
    counter = 0

    @retry(loop=loop)
    @asyncio.coroutine
    def fn():
        nonlocal counter

        counter += 1

        if counter == 1:
            raise RuntimeError

        return counter

    ret = yield from partial(fn)()

    assert ret == counter


@pytest.mark.run_loop
@asyncio.coroutine
def test_callback_delay(mocker, loop):
    mocker.patch('asyncio.sleep')
    counter = 0

    @retry(callback=partial(callback, delay=5), loop=loop)
    @asyncio.coroutine
    def fn():
        nonlocal counter

        counter += 1

        if counter <= 2:
            raise RuntimeError

        return counter

    ret = yield from partial(fn)()

    assert ret == counter

    expected = [
        ((5,), {'loop': loop}),
        ((10,), {'loop': loop}),
    ]

    assert asyncio.sleep.call_args_list == expected
