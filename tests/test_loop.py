import pytest
import asyncio

from async_retrying import retry, RetryError


@pytest.mark.run_loop
@asyncio.coroutine
def test_immutable_with_kwargs(loop):

    @retry(loop='_loop', immutable=True, kwargs=True)
    @asyncio.coroutine
    def coro(*, _loop):
        raise RuntimeError

    with pytest.raises(RetryError):
        yield from coro(_loop=loop)
