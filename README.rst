======
pqueue
======

**pqueue** is a simple persistent (disk-based) FIFO queue for Python.

**pqueue** goals are speed and simplicity. The development was initially based
on the `Queuelib`_ code. Entries are saved on disk using ``pickle``.

Requirements
============

* Python 2.7 or Python 3.x
* no external libraries requirements

Installation
============

You can install **pqueue** either via Python Package Index (PyPI) or from
source.

To install using pip::

    $ pip install pqueue

To install using easy_install::

    $ easy_install pqueue

If you have downloaded a source tarball you can install it by running the
following (as root)::

    # python setup.py install

How to use
==========

**pqueue** provides a single FIFO queue implementation.

Here is an example usage of the FIFO queue::

    >>> from pqueue import Queue
    >>> q = Queue("tmpqueue")
    >>> q.put(b'a')
    >>> q.put(b'b')
    >>> q.put(b'c')
    >>> q.get()
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
    
The ``Queue`` object is identical to Python's ``Queue`` module (or ``queue`` in
Python 3.x), with the difference that it requires a parameter ``path``
indicating where to persist the queue data and ``chunksize`` indicating how
many enqueued items should be stored per file. The same ``maxsize`` parameter
available on the system wise ``Queue`` has been maintained.

In other words, it works exactly as Python's ``Queue``, with the difference any
abrupt interruption is `ACID-guaranteed`_::

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

Note that pqueue *is not intended to be used by multiple processes*.

How it works?
=============

Pushed data is serialized using pickle in sequence, on chunked files named as
``qNNNNN``, with a maximum of ``chunksize`` elements, all stored on the given
``path``.

The queue is formed by a ``head`` and a ``tail``. Pushed data goes on ``head``,
pulled data goes on ``tail``.

An ``info`` file is pickled in the ``path``, having the following ``dict``:

* ``head``: a list of three integers, an index of the ``head`` file, the number
  of elements written, and the file position of the last write.
* ``tail``: a list of three integers, an index of the ``tail`` file, the number
  of elements read, and the file position of the last read.
* ``size``: number of elements in the queue.
* ``chunksize``: number of elements that should be stored in each disk queue
  file.

Both read and write operations depend on sequential transactions on disk. In
order to accomplish ACID requirements, these modifications are protected by the
Queue locks.

If, for any reason, the application stops working in the middle of a head
write, a second execution will remove any inconsistency by truncating the
partial head write.

On ``get``, the ``info`` file is not updated, only when you first call
``task_done``, and only on the first time case you have to call it
sequentially.

The ``info`` file is updated in the following way: a temporary file (using
'mkstemp') is created with the new data and then moved over the previous
``info`` file. This was designed this way as POSIX 'rename' is guaranteed to be
atomic.

In case of abrupt interruptions, one of the following conditions may happen:

* A partial write of the last pushed element may occur and in this case only
  this last element pushed will be discarded.
* An element pulled from the queue may be processing, and in this case a second
  run will consume same element again.

Tests
=====

Tests are located in **pqueue/tests** directory. They can be run using
Python's default **unittest** module with the following command::

    ./runtests.py

The output should be something like the following::

    ./runtests.py
    test_GarbageOnHead (pqueue.tests.test_queue.PersistenceTest)
    Adds garbage to the queue head and let the internal integrity ... ok
    test_MultiThreaded (pqueue.tests.test_queue.PersistenceTest)
    Create consumer and producer threads, check parallelism ... ok
    test_OpenCloseOneHundred (pqueue.tests.test_queue.PersistenceTest)
    Write 1000 items, close, reopen checking if all items are there ... ok
    test_OpenCloseSingle (pqueue.tests.test_queue.PersistenceTest)
    Write 1 item, close, reopen checking if same item is there ... ok
    test_PartialWrite (pqueue.tests.test_queue.PersistenceTest)
    Test recovery from previous crash w/ partial write ... ok
    test_RandomReadWrite (pqueue.tests.test_queue.PersistenceTest)
    Test random read/write ... ok
    
    ----------------------------------------------------------------------
    Ran 6 tests in 1.301s
    
    OK

License
=======

This software is licensed under the BSD License. See the LICENSE file in the
top distribution directory for the full license text.

Versioning
==========

This software follows `Semantic Versioning`_

.. _Queuelib: http://github.com/scrapy/queuelib
.. _ACID-guaranteed: http://en.wikipedia.org/wiki/ACID
.. _Semantic Versioning: http://semver.org/
