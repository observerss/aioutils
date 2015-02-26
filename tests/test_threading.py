#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import random
import asyncio
import threading
from aioutils import Group

def test_threading():
    """ Ensure that Pool and Group are thread-safe """
    loop = asyncio.get_event_loop()
    stopall = False
    def t():
        asyncio.set_event_loop(loop)
        g = Group()

        @asyncio.coroutine
        def f(c):
            yield from asyncio.sleep(random.random()*0.1)
            return c

        while not stopall:
            for i in range(10):
                g.spawn(f(i))

            g.join()

            time.sleep(random.random()*0.1)

    tasks = [threading.Thread(target=t) for _ in range(5)]
    for task in tasks: task.daemon = True
    for task in tasks: task.start()
    time.sleep(1.)
    stopall = True

if __name__ == '__main__':
    test_threading()
