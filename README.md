# Python3 Asyncio Utils

## Introduction

Python3 Asyncio implements an event loop, but 

- it is in quite low level, it misses some advanced primitives
- it can only write sync code wrapped in async code helper (`run_in_executer`), not the other way around

If you try to use asyncio the basic way, you must write all your code in an async way, but that's a pain for many applications. I feel must better to write critical part in async mode while remain transparent to others sync codes.

To achieve this, here is package I wrote that provides the following primitives.

- `Group`: a `gevent.pool.Group` alike object, allows you to spawn coroutines and join them later
- `Pool`: a `gevent.poo.Pool` alike object, allows setting concurrency level
- `Yielder`: a helper to write generator with coroutines
- `OrderedYielder`: a helper to write generator with coroutines, and keep yielding order the same as spawning order


## QuickStart

Simple Group, You might find that there is no explicit event loops, it looks just like threading or gevent. 

Under the hood, a event loop is started and wait until all tasks in Group joins then stopped (to return sync value)

```py
import random
import asyncio
from aioutils import Pool, Group, Yielder, OrderedYielder

@asyncio.coroutine
def f(c):
	yield from asyncio.sleep(random.random()/10)
	return c

chars = 'abcdefg'
		
# Group Usage
g = Group()
for c in chars:
	g.spawn(f(c))
g.join()

# Pool Usage
p = Pool(2)
for c in chars:
	p.spawn(f(c))
p.join()
```

And if you need the return values, use `Yielder`

```py
def gen_func():
	y = Yielder()
	for c in chars:
		y.spawn(f(c))
	yield from b.yielding()

print(list(gen_func())		
# outputs an unordered version of ['b', 'd', 'c', 'e', 'f', 'g', a']
```

And if you want the return order to be the same as spawn order, `OrderedYielder`

```py
def gen_func():
	y = OrderedYielder()
	for c in chars:
		y.spawn(f(c))
	yield from b.yielding()

print(list(gen_func())		
# ['a', 'b', 'c', 'd', 'e', 'f', 'g']
```


## Testing

Install nosetests, coverage, then run the following

```bash
make test

# or

PYTHONPATH=. nosetests tests/
```

## More Examples

The Group and Pool are quite useful in complex asynchronous situations. 

Compare these codes below

### Simple Loop

Even in simplest case, Group can make the below code cleaner

#### asyncio version

```py
@asyncio.coroutine
def f1():
    yield from asyncio.sleep(1.0)

tasks = [asyncio.async(f1()) for _ in range(10)]
asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
```

#### with `aoipool.Group`

```py
from aiopool import Group

@asyncio.coroutine
def f1():
    yield from asyncio.sleep(1.0)

g = Group()
for _ in range(10):
    g.spawn(f1())
g.join()
```

### Nested Loops

When you have multiple levels of loops, each depends on some blocking data, your situation is worse in raw asyncio

#### a sync example
 
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

#### aysncio version


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

#### `aiopool.Group` version

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

#### `aoi.pool.Pool`, set max concurrency levels

```py
p = Pool(10)

@asyncio.coroutine
def inner_task(v1):
	for _ in range(10)
		p.spawn(f2(v1))
		
for _ in range(10):
	p.spawn(inner_task(v1))
	
p.join()
```

Looks same like `Group`, but ensures that no more than 10 tasks in the same `Pool` can be executed simultaneously.


