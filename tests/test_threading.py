#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import random
import asyncio
import threading
from aioutils import Group, Yielder

@asyncio.coroutine
def f(c):
    yield from asyncio.sleep(random.random()*0.02)
    return c


def test_group_threading():
    """ Ensure that Pool and Group are thread-safe """
    loop = asyncio.get_event_loop()
    stopall = False
    def t():
        asyncio.set_event_loop(loop)

        while not stopall:
            g = Group()
            for i in range(5):
                g.spawn(f(i))

            g.join()

            time.sleep(random.random()*0.02)

    tasks = [threading.Thread(target=t) for _ in range(5)]
    for task in tasks: task.daemon = True
    for task in tasks: task.start()
    time.sleep(0.2)
    stopall = True
    for task in tasks: task.join()
    assert asyncio.Task.all_tasks() == set(), asyncio.Task.all_tasks()


def test_yielder_threading():
    """ Ensure Yielder are thread safe """
    stopall = False
    loop = asyncio.get_event_loop()
    chars = 'abcdefg'

    def gen_func():
        y = Yielder()

        for c in chars:
            y.spawn(f(c))

        yield from y.yielding()

    def t():
        asyncio.set_event_loop(loop)
        while not stopall:
            chars2 = list(gen_func())
            assert set(chars2) == set(chars)

            time.sleep(random.random()*0.02)

    tasks = [threading.Thread(target=t) for _ in range(5)]
    for task in tasks: task.daemon = True
    for task in tasks: task.start()
    time.sleep(0.2)
    stopall = True
    for task in tasks: task.join()
    assert asyncio.Task.all_tasks() == set(), asyncio.Task.all_tasks()


def test_mixed():
    """ Ensure mixed usage are thread safe """
    loop = asyncio.get_event_loop()
    chars = 'abcdefg'
    stopall = False

    def f1():
        y = Yielder()
        for c in chars:
            y.spawn(f(c))

        return list(y.yielding())

    def f2():
        g = Group()
        for c in chars:
            g.spawn(f(c))

        g.join()

    def t():
        asyncio.set_event_loop(loop)
        while not stopall:
            f = random.choice([f1, f2])
            r = f()
            if f == f1:
                assert set(r) == set(chars)
            time.sleep(random.random()*0.02)

    tasks = [threading.Thread(target=t) for _ in range(5)]
    for task in tasks: task.daemon = True
    for task in tasks: task.start()
    time.sleep(0.2)
    stopall = True
    for task in tasks: task.join()
    assert asyncio.Task.all_tasks() == set(), asyncio.Task.all_tasks()


if __name__ == '__main__':
    test_group_threading()
    test_yielder_threading()
    test_mixed()
