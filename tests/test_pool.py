#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import asyncio

from aioutils import Group, Pool

def test_group():
    timespan = 0.1
    @asyncio.coroutine
    def f(i):
        t0 = time.time()
        yield from asyncio.sleep(timespan)
        t = time.time() - t0
        print('finish {}, seconds={:4.2f}'.format(i, t))

    print('testing group')
    t0 = time.time()
    g = Group()
    for i in range(9):
        g.spawn(f(i))
    g.join()
    print('total time: {:4.2f}'.format(time.time() - t0))
    assert timespan < time.time() - t0 < timespan * 1.1


def test_pool():
    timespan = 0.1

    @asyncio.coroutine
    def f(i):
        t0 = time.time()
        yield from asyncio.sleep(timespan)
        t = time.time() - t0
        print('finish {}, seconds={:4.2f}'.format(i, t))

    print('testing pool')
    t0 = time.time()
    p = Pool(3)
    for i in range(9):
        p.spawn(f(i))
    p.join()
    print('total time: {:4.2f}'.format(time.time() - t0))
    assert timespan * 3 < time.time() - t0 < timespan * 3 * 1.1

if __name__ == '__main__':
    test_group()
    test_pool()
