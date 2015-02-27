#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Bag and OrderedBag """
import heapq
import asyncio
import functools
import collections


class Yielder(object):

    """ A Bag Rewrite

    - easier to use
    - no background threading

    Each time when an item is put, we stop the main loop(!!) and yield
    """

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.counter = 0
        self.done = collections.deque()
        self.getters = collections.deque()

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

    def put(self, item):
        self._put(item)

    def _put(self, item):
        if self.getters:
            getter = self.getters.popleft()
            getter.set_result(None)

        self.done.append(item)

    def _stop_loop(self, f):
        self.loop.stop()

    def _safe_yield_from(self, waiter):
        """ use a loop to ensure loop running when we need to yield """
        while True:
            try:
                yield from waiter
            except:
                if not self.loop._running:
                    self.loop.run_forever()
            else:
                break

    def _yielding(self):
        while self.counter > 0 or self.done:
            if self.done:
                yield self.done.popleft()
            else:
                getter = asyncio.Future()
                self.getters.append(getter)
                getter.add_done_callback(self._stop_loop)
                yield from self._safe_yield_from(getter)

    def yielding(self):
        for x in self._yielding():
            if isinstance(x, asyncio.Future):
                continue
            yield x


class OrderedYielder(Yielder):
    def __init__(self):
        super(OrderedYielder, self).__init__()
        self.done = []
        self.order = 0
        self.yield_counter = 0

    def spawn(self, coro):
        self.order += 1
        task = asyncio.async(coro)
        task.add_done_callback(
            functools.partial(self._on_completion, order=self.order))
        self.counter += 1
        return task

    def _on_completion(self, f, order):
        self.counter -= 1
        f.remove_done_callback(self._on_completion)
        result = f.result()
        if result is not None:
            self._put((order, result))

    def _put(self, item, heappush=heapq.heappush):
        order, item = item
        if self.yield_counter + 1 == order or self.counter <= 0:
            if self.getters:
                getter = self.getters.popleft()
                getter.set_result(None)

        heappush(self.done, (order, item))

    def put(self, item):
        self.order += 1
        self._put((self.order, item))

    def _yielding(self, heappop=heapq.heappop):
        self.yield_counter = 1
        while self.counter > 0 or self.done:
            if self.done:
                order, item = self.done[0]
                if self.yield_counter == order:
                    _, item = heappop(self.done)
                    yield item
                    self.yield_counter += 1
                    continue

            getter = asyncio.Future()
            self.getters.append(getter)
            getter.add_done_callback(self._stop_loop)
            yield from self._safe_yield_from(getter)


class YieldingContext(object):
    def __init__(self, ordered=False):
        if ordered:
            self.y = OrderedYielder()
        else:
            self.y = Yielder()
        self.yielding = None

    def spawn(self, coro):
        return self.y.spawn(coro)

    def __enter__(self):
        return iter(self)

    def __iter__(self):
        self.yielding = self.y.yielding()
        return self

    def __next__(self):
        return next(self.yielding)

    def __exit__(self, *args):
        pass

yielding = YieldingContext
ordered_yielding = functools.partial(YieldingContext, ordered=True)
