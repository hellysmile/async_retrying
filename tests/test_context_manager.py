import asyncio
from functools import partial

import pytest

from async_retrying import retry

@pytest.mark.run_loop
@asyncio.coroutine
def test_context_manager(loop):
    counter = 0

    @asyncio.coroutine
    def fn():
        nonlocal counter

        counter += 1

        if counter == 1:
            raise RuntimeError

        return counter

    with retry(fn, loop=loop) as context:
        yield from context()

    ret = yield from partial(fn)()

    assert ret == counter
