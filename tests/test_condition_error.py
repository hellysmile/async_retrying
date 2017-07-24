from async_retrying import ConditionError, retry

import pytest
import asyncio


@pytest.mark.run_loop
@asyncio.coroutine
def test_timeout_is_not_none_and_not_async(loop):

    @retry(timeout=0.5)
    def coro():
        pass

    with pytest.raises(ConditionError):
        yield from coro()
