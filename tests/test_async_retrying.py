import asyncio
from functools import partial

import pytest

from async_retrying import retry


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
