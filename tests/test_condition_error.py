import asyncio

import pytest

from async_retrying import ConditionError, retry


@pytest.mark.run_loop
@asyncio.coroutine
def test_timeout_is_not_none_and_not_async(loop):

    @retry(timeout=0.5, loop=loop)
    def not_coro():
        pass

    with pytest.raises(ConditionError):
        yield from not_coro()
