## History

### 2015.03.05

0.3.8 release

- when GeneratorExit cancel all pending tasks
- yielder related status cleanups

### 2015.03.02

0.3.4-0.3.7 release

- create new event loop if using in a thread
- fix semaphore order so that loop must exist
- add test to test this behaviour
- cleanup _safe_yield_from that are not needed anymore
- use is_running (how can I not using that!!)

### 2015.02.28

0.3.3 release

- fixed Pool's potential thread unsafe problem
- fixed Yielder hangs when no items to yield
- add pool size argument to yielder family

### 2015.02.27

0.3.2 release

- typo fix

0.3.1 release

- add put method for manually yield items

0.3.0 release

- add Yielder and OrderedYielder to replace Bag and OrderedBag
- fix thread safe problem #2 in Yielder and Group mixed usage

### 2015.02.26

0.2.1 release

- fix thread unsafe problem

### 2015.02.26

0.2.0 release

- add Bag and OrderedBag
- rename to "aioutils"

### 2015.02.25

0.1.2 release

- fix some release problems

0.1.1 release

- basic group and pool implemenation


### 2015.02.23

ideas, prototypes
