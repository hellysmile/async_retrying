async_retrying
==============

:info: Simple retrying for asyncio

.. image:: https://img.shields.io/travis/wikibusiness/async_retrying.svg
    :target: https://travis-ci.org/wikibusiness/async_retrying

.. image:: https://img.shields.io/pypi/v/async_retrying.svg
    :target: https://pypi.python.org/pypi/async_retrying

Installation
------------

.. code-block:: shell

    pip install async_retrying

Usage
-----

.. code-block:: python

    import asyncio

    from async_retrying import retry

    counter = 0

    @retry
    @asyncio.coroutine
    def fn():
        global counter

        counter += 1

        if counter == 1:
            raise RuntimeError

    @asyncio.coroutine
    def main():
        yield from fn()

    loop = asyncio.get_event_loop()

    loop.run_until_complete(main())

    assert counter == 2

    loop.close()


Python 3.3+ is required
