import pytest

from async_retrying import ConditionError, retry


@pytest.mark.asyncio
async def test_timeout_is_not_none_and_not_async(event_loop):

    @retry(timeout=0.5, loop=event_loop)
    def not_coro():
        pass

    with pytest.raises(ConditionError):
        await not_coro()
