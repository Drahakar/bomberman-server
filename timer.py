import asyncio
from contextlib import suppress

class Periodic:
    def __init__(self, func, time):
        self.func = func
        self.time = time
        self.is_started = False
        self._task = None

    @asyncio.coroutine
    def start(self):
        if not self.is_started:
            self.is_started = True
            # Start task to call func periodically:
            self._task = asyncio.ensure_future(self._run())

    @asyncio.coroutine
    def stop(self):
        if self.is_started:
            self.is_started = False
            # Stop task and await it stopped:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                yield from self._task

    @asyncio.coroutine
    def _run(self):
        while True:
            yield from asyncio.sleep(self.time)
            self.func()
