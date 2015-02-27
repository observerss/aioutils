# Python3 Asyncio Utils

## Introduction

Python3 Asyncio implements an event loop, but 

- it is quite low level, it misses some advanced primitives
- it can only write sync code wrapped in async code helper (`run_in_executer`), not the other way around

Specifically, to use asyncio, you must write all your code in an async way, write wrappers for all blocking code, and execute them all in a loop

That's quite obfuscated for many applications. It is much easier to write critical part in async mode while remain transparent to others sync codes.

To achieve this, here is package I wrote that provides the following primitives.

- `Group`: a `gevent.pool.Group` alike object, allows you to spawn coroutines and join them later
- `Pool`: a `gevent.poo.Pool` alike object, allows setting concurrency level
- `Yielder`: a helper to write generator with coroutines
- `OrderedYielder`: a helper to write generator with coroutines, and keep yielding order the same as spawning order


## QuickStart

### Group

Simple `Group` Usage.

```py
import random
import asyncio
from aioutils import Pool, Group, Yielder, OrderedYielder, yielding, ordered_yielding

@asyncio.coroutine
def f(c):
	yield from asyncio.sleep(random.random()/10)
	return c

chars = 'abcdefg'
		
g = Group()
for c in chars:
	g.spawn(f(c))
g.join()
```

You might find that there is no explicit event loop, it looks just like threading or gevent. 

Under the hood, an event loop starts and runs until all tasks in group joins, 
then the event loop stops, allows synced calls from outside.

The event pool may start later again by other method or in orther thread, it is completely thread safe.

### Pool

Sometimes, you want to limit the maximum level of concurrency, you can use `Pool` instead.

```py
p = Pool(2)
for c in chars:
	p.spawn(f(c))
p.join()
```

The only differences between `Pool` and `Group` is that a `Pool` initializes with a integer as the limiting concurrency.

### Yielder

If the return value of the spawned coroutines matters to you, use `Yielder`

```py
def gen_func():
	y = Yielder()
	for c in chars:
		y.spawn(f(c))
	yield from y.yielding()

print(list(gen_func())		
# outputs an unordered version of ['b', 'd', 'c', 'e', 'f', 'g', 'a']
```

Note that **`Yielder` only captures results that returns something**, i.e. if you spawn a coroutine that doesn't return anything, or returns `None`, `Yielder` will not yield that value.

You can also use `y.put` method to explicitly declare what items to be yielded.

Under the hood, `Yielder` runs an event loop until the first non-None-return corotuine completed, then stops the loop and yield. This process is repeated until all spawned coroutines are done.

You can also use a context manager `yielding`

```py
def gen_func2():
	with yielding() as y:
		for c in chars:
			y.spawn(f(c))
		yield from y
			
print(list(gen_func2())
# outputs an unordered version of ['b', 'd', 'c', 'e', 'f', 'g', 'a']
```

The `Yielder` and `yielding` are both thread safe.

### Sequential "yield from"s

When using `yielding`, you'd better avoid using sequential "yield from"s when possible, the problem code is as follows

```py
@asyncio.coroutine
def f()
    t1 = yield from f1()
    t2 = yield from f2()
    y.put(t1 + t2)
```

This code alone is ok, but if you use it in a loop, spawning thousands of async tasks of "f", then the event loop need to wait for all f1s complete before it can schedule f2. Thus the yielding processing won't yield anything, it will block until all "f1"s done and some "f2"s done too.

If there're no dependecies between "f1" and "f2", the following modification works just fine

```py
@asyncio.coroutine
def f()
    t1 = asyncio.async(f1())
    t2 = asyncio.async(f2())
    yield from asyncio.wait([t1, t2])
    y.put(t1.result() + t2.result())
```

If f2's argument depends on f1's result, you'd better do "yield from f2()" directly inside f1.

This coding preference holds true for raw asyncio, too.

### OrderedYielder

If you want the return order to be the same as spawn order, `OrderedYielder`

```py
def gen_func():
	y = OrderedYielder()
	for c in chars:
		y.spawn(f(c))
	yield from y.yielding()

print(list(gen_func())		
# ['a', 'b', 'c', 'd', 'e', 'f', 'g']
```

And also there is `ordered_yielding` works just like `yielding`

### Examples

see [test cases](tests) for example usages.


## Testing

Install nosetests, coverage, then run the following

```bash
make test

# or

PYTHONPATH=. nosetests tests/
```

## More Examples

The Group is quite useful in complex asynchronous situations. 

Compare these codes below

### Simple Loop

Even in simplest case, Group can make the below code cleaner

#### 1. using `asyncio`

```py
@asyncio.coroutine
def f1():
    yield from asyncio.sleep(1.0)

tasks = [asyncio.async(f1()) for _ in range(10)]
asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
```

#### 2. using `Group`

```py
from aioutils import Group

g = Group()
for _ in range(10):
    g.spawn(f1())
g.join()
```

### Nested Loops

When you have multiple levels of loops, each depends on some blocking data, your situation is worse in raw asyncio

#### 1. a sync example
 
```py
def f1():
	time.sleep(0.1)
	return random.random()
	
def f2(v1):
	time.sleep(0.1)
	return random.random()
	
for _ in range(10):
	v1 = f1()
	for _ in range(10):
		f2(v1)
```	

Now we need to wait `f1` 10 times, plus `f2` 100 times, it takes 11 seconds to finish.

But the optimal time for this problem is only 0.2 seconds, that is

- let all `f1`s runs and return, 0.1 seconds, 
- then let all `f2`s run and return, another 0.1 seconds.

Let's try to write them in aysncio.

#### 2. using `aysncio`


##### make f1 and f2 coroutine

```py
@asyncio.coroutine
def f1():
	yield from asyncio.sleep(0.1)
	return random.random()
	
@asyncio.coroutine
def f2(v1):
	yield from asyncio.sleep(0.1)
	return random.random() + v1
```	

##### asyncio, make the second loop coroutine 

```
tasks = []

@asyncio.coroutine
def inner_task(v1):
	for _ in range(10):
		yield from f2(v1)
		
for _ in range(10):
	tasks.append(asyncio.async(inner_task))
	
asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
```


But this only parallels on the first loop, not the seconds one.

We need to create two levels of tasks, level1 tasks just runs and generates level2 tasks, then we wait on all level2 tasks.

##### asyncio, with 2 task levels

```py
level1 = []
level2 = []

@asyncio.coroutine
def inner_task(v1):
	for _ in range(10)
		level2.append(asyncio.async(f2(v1)))
		
for _ in range(10):
	level1.append(asyncio.async(inner_task))
	
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(level1))
loop.run_until_complete(asyncio.wait(level2))
```

We must keep two levels of tasks, otherwise `asyncio.wait` will panic when you try to add new async tasks when level1 tasks got resolved.

This implementation is not only ugly, and also hard to manage, what if you have 3, 4, or unknown level of tasks?

#### 3. using `Group`

```py
g = Group()

@asyncio.coroutine
def inner_task(v1):
	for _ in range(10)
		g.spawn(f2(v1))
		
for _ in range(10):
	g.spawn(inner_task(v1))
	
g.join()
```

Which is (I think) easier to understand and use.


