import asyncio
from functools import partial
from unittest.mock import call

import pytest

from async_retrying import callback, retry


@pytest.mark.asyncio
async def test_smoke(event_loop):
    counter = 0

    @retry(loop=event_loop)
    async def fn():
        nonlocal counter

        counter += 1

        if counter == 1:
            raise

        return counter

    ret = await partial(fn)()

    assert ret == counter


@pytest.mark.asyncio
async def test_callback_delay(mocker, event_loop):
    mocker.patch("asyncio.sleep")
    counter = 0

    @retry(callback=partial(callback, delay=5), loop=event_loop)
    async def fn():
        nonlocal counter

        counter += 1

        if counter <= 2:
            raise RuntimeError

        return counter

    ret = await partial(fn)()

    assert ret == counter

    expected = [call(5), call(10)]

    assert asyncio.sleep.call_args_list == expected
