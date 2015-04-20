======
pqueue
======

**pqueue** is a simple persistent (disk-based) FIFO queue for Python.

**pqueue** goals are speed and simplicity. The development was initially based
on the `Queuelib <http://github.com/scrapy/queuelib>` code.

============
Requirements
============

* Python 2.7 or Python 3.3
* no external libraries requirements

============
Installation
============

You can install **pqueue** either via Python Package Index (PyPI) or from
source.

To install using pip:

    $ pip install pqueue

To install using easy_install:

    $ easy_install pqueue

If you have downloaded a source tarball you can install it by running the
following (as root):

    # python setup.py install

==========
How to use
==========

**pqueue** provides a single FIFO queue implementation.

Here is an example usage of the FIFO queue:

    >>> from pqueue import Queue
    >>> q = Queue("tmpqueue")
    >>> q.put(b'a')
    >>> q.put(b'b')
    >>> q.put(b'c')
    >>> q.pop()
    b'a'
    >>> del q
    >>> q = Queue("tmpqueue")
    >>> q.get()
    b'b'
    >>> q.get()
    b'c'
    >>> q.get_nowait()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/usr/lib/python2.7/Queue.py", line 190, in get_nowait
        return self.get(False)
      File "/usr/lib/python2.7/Queue.py", line 165, in get
        raise Empty
    Queue.Empty
    
The Queue object is identical to Python's 'Queue' module (or 'queue' in Python
3.x), with the difference that it requires a parameter 'path' indicating where
to persist the queue data and 'chunksize' indicating how many enqueued items
should be stored per file. The same 'maxsize' parameter available on the
system wise 'Queue' has been maintained.

In other words, it works exactly as Python's Queue, with the difference any
abrupt interruption is `ACID-guaranteed <http://en.wikipedia.org/wiki/ACID>`:

    q = Queue()

    def worker():
        while True:
            item = q.get()
            do_work(item)
            q.task_done()

    for i in range(num_worker_threads):
         t = Thread(target=worker)
         t.daemon = True
         t.start()

    for item in source():
        q.put(item)

    q.join()       # block until all tasks are done

Note that pqueue *is not intended to used by multiple processes*.

=====
Tests
=====

Tests are located in **pqueue/tests** directory. They can be run using
Python's default **unittest** module with the following command:

    ./runtests.py

The output should be something like the following::

    ./runtests.py
    test_MultiThreaded (pqueue.tests.test_queue.TestSuite_PersistenceTest)
    Create consumer and producer threads, check parallelism ... ok
    test_OpenCloseOneHundred (pqueue.tests.test_queue.TestSuite_PersistenceTest)
    Write 1000 items, close, reopen checking if all items are there ... ok
    test_OpenCloseSingle (pqueue.tests.test_queue.TestSuite_PersistenceTest)
    Write 1 item, close, reopen checking if same item is there ... ok
    test_PartialWrite (pqueue.tests.test_queue.TestSuite_PersistenceTest)
    Test recovery from previous crash w/ partial write ... ok
    test_RandomReadWrite (pqueue.tests.test_queue.TestSuite_PersistenceTest)
    Test random read/write ... ok
    
    ----------------------------------------------------------------------
    Ran 5 tests in 4.615s
    
    OK

=======
License
=======

This software is licensed under the BSD License. See the LICENSE file in the
top distribution directory for the full license text.

