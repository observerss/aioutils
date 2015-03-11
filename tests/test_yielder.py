#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import random
import inspect
import asyncio
from aioutils import Yielder, OrderedYielder, yielding, ordered_yielding

from nose.tools import raises

@asyncio.coroutine
def f(c):
    yield from asyncio.sleep(random.random()*.1)
    return c


def test_yielder():
    def gen_func():
        y = Yielder()
        @asyncio.coroutine
        def f1(i):
            yield from asyncio.sleep(random.random()*0.1)
            for j in [random.randint(0, 10) for _ in range(i)]:
                y.spawn(f2(j))

        @asyncio.coroutine
        def f2(j):
            yield from asyncio.sleep(random.random()*0.1)
            return j + random.random()

        for i in range(5):
            y.spawn(f1(i))

        y.put(3)

        for i in range(5, 10):
            y.spawn(f1(i))

        yield from y.yielding()

    g = gen_func()
    assert inspect.isgenerator(g)
    t0 = time.time()
    gs = list(g)
    assert len(gs) == 46
    assert min(gs) > 0 and max(gs) < 11
    assert time.time() - t0 < 0.2 * 1.1


def test_ordered_yielder():
    chars = 'abcdefg'

    def gen_func():
        y = OrderedYielder()
        for c in chars[:3]:
            y.spawn(f(c))

        y.put('z')

        for c in chars[3:]:
            y.spawn(f(c))

        yield from y.yielding()

    g = gen_func()
    assert inspect.isgenerator(g)
    t0 = time.time()
    gs = list(g)
    assert ''.join(gs) == chars[:3] + 'z' + chars[3:]
    assert time.time() - t0 < 0.1 * 1.1


def test_yielding():
    chars = 'abcdefg'
    def gen_func():
        with yielding() as y:
            for c in chars:
                y.spawn(f(c))
            yield from y

    def gen_func2():
        with ordered_yielding() as y:
            for c in chars:
                y.spawn(f(c))
            yield from y

    g = gen_func()
    assert inspect.isgenerator(g)
    t0 = time.time()
    gs = list(g)
    assert set(gs) == set(chars)
    assert time.time() - t0 < 0.1 * 1.1

    assert ''.join(list(gen_func2())) == chars


def test_yielder_with_pool_size():
    chars = 'abcdefgh'
    def gen_func():
        with yielding(2) as y:
            for c in chars:
                y.spawn(f(c))
            yield from y


    # I don't know how to assert correctness, >.<
    assert set(gen_func())  == set(chars)


def test_empty_yielder():
    def gen_func():
        with yielding() as y:
            y.spawn(asyncio.sleep(0.01))
            yield from y

    assert list(gen_func()) == []


def test_two_level_ordered_yielding():
    chars = 'abcdefg'
    def gen_func():
        with ordered_yielding() as y:
            @asyncio.coroutine
            def g(i):
                for c in chars[:i]:
                    y.spawn(f(c))

            for i in range(3, 5):
                y.spawn(g(i))

            yield from y

    assert ''.join(list(gen_func())) == 'abcabcd'


def test_break_from_yielding():
    @asyncio.coroutine
    def g(c):
        yield from asyncio.sleep(random.random()*.1)
        return c
    y = Yielder()

    def gen_func():
        for c in 'abcdefg':
            y.spawn(g(c))
        yield from y.yielding()

    for x in gen_func():
        break

    assert y.counter == 0


@raises(ValueError)
def test_raise_from_yielding():
    @asyncio.coroutine
    def g(c):
        yield from asyncio.sleep(random.random()*.1)
        if random.random() < 0.2:
            raise ValueError
        return c

    def gen_func():
        with yielding(3) as y:
            for c in 'abcdefghijklmn':
                y.spawn(g(c))
            yield from y

    # test that raise will not cause problem
    for x in gen_func():
        pass


@raises(ValueError)
def test_raise_from_nested_yielding():
    yielder = Yielder()

    @asyncio.coroutine
    def worker(err_count=0):
        yield from asyncio.sleep(random.random()*.02)
        if err_count > 5:
            raise ValueError
        else:
            return (yield from worker(err_count+1))

    for i in range(10):
        yielder.spawn(worker())

    for i, ch in enumerate(yielder.yielding()):
        pass


if __name__ == '__main__':
    test_yielder()
    test_ordered_yielder()
    test_yielding()
    test_yielder_with_pool_size()
    test_empty_yielder()
    test_two_level_ordered_yielding()
    test_break_from_yielding()
    test_raise_from_yielding()
    test_raise_from_nested_yielding()
