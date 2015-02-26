#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Bag and OrderedBag """
import asyncio
import collections


class Yielder(object):

    """ A Bag Rewrite

    - easier to use
    - no background threading

    Each time when an item is put, we stop the main loop(!!) and yield
    """

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.q = collections.deque()
        self.t = None
        self.counter = 0
        self.waiters = collections.deque()

    def spawn(self, coro):
        task = asyncio.async(coro)
        task.add_done_callback(self._on_completion)
        self.counter += 1
        return task

    def _on_completion(self, f):
        self.counter -= 1
        f.remove_done_callback(self._on_completion)
        result = f.result()
        if result is not None:
            self._put(result)

    def _put(self, item):
        while self.waiters and self.waiters[0].done():
            self.waiters.popleft()

        self.q.append(item)
        if self.waiters:
            waiter = self.waiters.popleft()
            waiter.set_result(None)

    def _stop_loop(self, f):
        self.loop.stop()

    def yielding(self):
        while self.counter > 0:
            waiter = asyncio.Future()
            waiter.add_done_callback(self._stop_loop)
            self.waiters.append(waiter)
            if not self.loop._running:
                self.loop.run_forever()
            yield from waiter
            while self.q:
                yield self.q.popleft()



if __name__ == '__main__':
    y = Yielder()
    import random
    @asyncio.coroutine
    def f1(i):
        yield from asyncio.sleep(random.random()*0.1)
        for j in [random.randint(0, 10) for _ in range(i)]:
            y.spawn(f2(j))

    @asyncio.coroutine
    def f2(j):
        yield from asyncio.sleep(random.random()*0.1)
        return j + random.random()

    for i in range(10):
        y.spawn(f1(i))

    for x in y.yielding():
        print(x)
