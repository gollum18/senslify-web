# Name: util.py
# Module: senslify.util
# Since: July 20th, 2019
# Author: Christen Ford
# Description: Implements useful utility classes and methods.


import dataclass, threading, typing

class MemoryCache:
    '''
    Implements an asynchronous cache that utilizes the Least Recently Used
    paging algorithm and two-phase locking. The public methods defined by the
    cache are thread-safe.

    The following operations require only acquiring the Read lock:
        get()
        has()

    The following operations require acquiring both the Read and Write lock:
        put()

    The above operations will block if the Read lock is currently held.

    Technically, has() does not require any locking nor should it, but its
    a compromise to ensure cache integrity. Without acquiring the Read lock,
    put() could overwrite the contents of the cache item has() finds before it
    has a chance to return to its caller, causing has() to return a false
    positive.
    '''

    # used for indexing the cache items
    _KEY = 0
    _VALUE = 1
    _AGE = 2
    _OCCUPIED = 3

    def __init__(self, size):
        self._size = size
        self._items = []
        self._rl = threading.Lock()
        self._wl = threading.Lock()
        self._init()


    def _init(self):
        for i in range(self._size):
            self._items.append([None, None, 0, False])


    def _age(self):
        '''
        Ages all items in the cache by 1.
        '''
        for i in range(self._items):
            item = self._items[i]
            if item[_OCCUPIED]:
                item[_AGE] += 1


    def _page(self):
        '''
        Pages an item from cache and returns its position.
        '''
        pos = 0
        age = self._items[0].
        for i in range(1, self._size):
            if self._items[i][_AGE] > age:
                pos = i
                age = self._items[i][_AGE]
        return pos


    def _search(self, key, items):
        '''
        Implements a binary search for determining if the cache has a key or not.
        '''
        # check if the middle item has the key we're interested in
        mid = len(items) // 2
        item = items[mid]
        if item[_OCCUPIED] and item[_KEY] == key:
            return item
        # check if the left or right halves have the key we're looking for
        left = self._search(key, items[0:mid])
        right = self._search(key, items[mid:len(items)])
        if left:
            return left
        if right:
            return right
        # return None since we didn't find what we're looking for
        return None


    def _index(self, key):
        '''
        Returns a position in the list for the key.
        '''
        return hash(key) % self._size


    async def has(self, key):
        '''
        Determines if the cache has the specified item.

        Runs in logarithmic time - O(log_2(N)).
        '''
        found = False
        # acquire the read lock
        self._rl.acquire()
        try:
            # try to see if the key is where we put it
            index = self._index(key)
            item = self._items[index]
            if item[_OCCUPIED] and item[_KEY] == key:
                found = True
            else:
                # Otherwise probe for it
                found = self._search(key, self._items) is not None
        finally:
            # release the read lock
            self._rl.release()
        return found


    async def put(self, key, value):
        '''
        Writes an item into the cache.

        The Put operation requires first acquiring the Read lock and
        then acquiring the Write lock.

        Runs in linear time - O(N + N).
        '''
        def set_item(item):
            item[_KEY] = key
            item[_VALUE] = value
            item[_AGE] = 0
            item[_OCCUPIED] = True


        self._rl.acquire()
        self._wl.acquire()
        try:
            index = self._index(key)
            if :
                not self._items[index][_OCCUPIED]:
                    set_item(self._items[index])
            else:
                # otherwise probe for a location
                pos = index + 1
                while pos != index:
                    if pos == self._size:
                        pos = 0
                    if not self._items[pos][_OCCUPIED]:
                        set_item()
                    pos += 1
                # need to page if probing was unsuccessful
                if pos == index:
                    pos = self._page()
                    set_item(self._items[pos])
        finally:
            self._age()
            # release any locks
            self._rl.release()
            self._wl.release()


    async def get(self, key):
        '''
        Gets an item from the cache.

        The Get operation only requires acquiring the Read lock.

        Runs in logarithmic time - O(log_2(N)).
        '''
        item = None
        # try to acquire the read lock
        self._rl.acquire()
        # see if the key is where we would normally put it
        try:
            index = self._index(key)
            item = self._items[index]
            if not item:
                # probe for the key since we had to dump it somewhere else
                item = self._search(key)
        finally:
            self._age()
            # release the read lock
            self._rl.release()
        # see if we found the item, note if found through search, this is redundant
        if item and item[_OCCUPIED] and item[_KEY] == key:
            item[_AGE] = 0
            return item[_VALUE]
        return None
