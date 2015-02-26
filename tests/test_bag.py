#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import inspect
import asyncio

from aioutils import Bag, OrderedBag, Group

def test_bag():
    chars = 'abcdefg'
    def g():
        b = Bag()
        @asyncio.coroutine
        def f(c):
            yield from asyncio.sleep(random.random()/10)
            b.put(c)
        def schedule():
            for c in chars:
                b.spawn(f(c))
            b.join()
        b.schedule(schedule)
        yield from b.yielder()

    chars2 = g()
    assert inspect.isgenerator(chars2)
    chars2 = list(chars2)
    assert set(chars) == set(chars2)


def test_orderedbag():
    chars = 'abcdefg'
    def g():
        b = OrderedBag(Group())
        @asyncio.coroutine
        def f(c):
            yield from asyncio.sleep(random.random()*0.1)
            b.put(c)
        def schedule():
            for c in chars:
                b.spawn(f(c))
            b.join()
        b.schedule(schedule)
        yield from b.yielder()

    chars2 = g()
    assert inspect.isgenerator(chars2)
    chars2 = list(chars2)
    for c1, c2 in zip(chars, chars2):
        assert c1 == c2


if __name__ == '__main__':
    test_bag()
    test_orderedbag()
