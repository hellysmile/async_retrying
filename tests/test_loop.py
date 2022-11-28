import asyncio

import pytest

from async_retrying import RetryError, retry


@pytest.mark.asyncio
async def test_immutable_with_kwargs(event_loop):
    @retry(loop="_loop", immutable=True, kwargs=True, fatal_exceptions=KeyError)
    async def coro(a, *, _loop):
        a.pop("a")
        raise RuntimeError

    with pytest.raises(RetryError):
        await coro(a={"a": "a"}, _loop=event_loop)
