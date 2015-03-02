#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Bag and OrderedBag

This is old implementation for yielding helper
You should use Yielder and OrderedYielder instead
"""
import time
import queue
import inspect
import asyncio
import functools
import threading

from .pool import Group


class Bag(object):

    """ Create generator function with coroutines

    A Bag is just a Group, a queue, and a background thread running event loop.
    Coroutines are spawned in a schedule method, and enqueues result to the
    queue, main thread then yield items from queue.

    Usage::

    def gen_func():
        b = Bag()
        @asyncio.coroutine
        def coro(arg):
            ...
            b.put(...)

        def schedule():
            ...
            for ...:
                b.spawn(coro(arg))
            ...
            b.join()

        b.schedule(schedule)
        yield from b.yielder()
    """

    def __init__(self, group=None):
        if group is not None:
            self.g = group
            self.loop = self.g.loop
        else:
            try:
                self.loop = asyncio.get_event_loop()
                if self.loop.is_running():
                    raise NotImplementedError("Cannot use aioutils in "
                                            "asynchroneous environment")
            except:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            self.g = Group(loop=self.loop)
        self.q = queue.Queue()
        self.t = None

    def spawn(self, coro):
        return self.g.spawn(coro)

    def join(self):
        return self.g.join()

    def put(self, item):
        self.q.put(item)

    def schedule(self, schedule):
        def schedule_wrapper(loop):
            asyncio.set_event_loop(loop)
            schedule()

        self.t = threading.Thread(target=schedule_wrapper, args=(self.loop,))
        self.t.start()

    def yielder(self):
        while (self.t and self.t.is_alive()) or (self.q.qsize() > 0):
            try:
                yield self.q.get_nowait()
            except:
                time.sleep(0.1)


class OrderedBag(Bag):

    """ A Bag that ensures ordering """

    def __init__(self, *args):
        super(OrderedBag, self).__init__(*args)
        self.q = queue.PriorityQueue()
        self.order = 0

    def spawn(self, coro):
        self.order += 1

        def _coro_wrapper(order):
            yield from coro
        return self.g.spawn(functools.partial(_coro_wrapper, self.order)())

    def put(self, item):
        order = self._get_coro_order()
        self.q.put((order, item))

    def _get_coro_order(self):
        """ Get the coro (and its order) of self """
        stack = inspect.stack()
        for frame, module, line, function, context, index in stack:
            if function == '_coro_wrapper':
                return frame.f_locals['order']

    def yielder(self):
        next_order = 1
        while (self.t and self.t.is_alive()) or (self.q.qsize() > 0):
            try:
                # peek item, the smallest of heap
                order, item = self.q.queue[0]
                if order != next_order:
                    time.sleep(0.03)
                else:
                    order, item = self.q.get_nowait()
                    next_order += 1
                    yield item
            except IndexError:
                time.sleep(0.03)
