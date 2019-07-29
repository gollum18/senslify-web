# Name: test.py
# Since: July 29th, 2019
# Author: Christen Ford
# Description: Implements unittests for testing the classes defined in the 
#   senslify.utils Module.

import unittest

from senslify.utils import MemoryCache, Message


class TestCacheMethods(unittest.TestCase):
    '''
    Defines methods for testing the MemoryCache class.
    '''

    def setUp(self):
        '''
        Setsup the testing harness before each test.
        '''
        self.cache = MemoryCache(32)
    
    
    def tearDown(self):
        '''
        Tearsdown the testing harness after each test.
        '''
        self.cache = None
    

class TestMessageMethods(unittest.TestCase):
    '''
    Defines methods for testing the Message class.
    '''
    
    def setUp(self):
        '''
        Setsup the testing harness before each test.
        '''
        self.msg = Message(a=0, b=1, c=2)
        
    
    def tearDown(self):
        '''
        Tearsdown the testing harness after each test.
        '''
        self.msg = None
        
    
    def test_clear(self):
        '''
        Tests the Message.clear() functionality.
        '''
        assert self.msg
        self.msg.clear()
        assert not self.msg
        
        
    def test_contains(self):
        '''
        Tests the contains functionality of the Message.
        '''
        assert 'a' in self.msg
        assert 'b' in self.msg
        assert 'c' in self.msg
    
    
    def test_get(self):
        '''
        Tests the Message.get() functionality.
        '''
        assert self.msg.get('a') == 0
        assert self.msg.get('b') == 1
        assert self.msg.get('c') == 2
    
    
    def test_items(self):
        '''
        Tests the Message.items() functionality.
        '''
        items = self.msg.items()
    
    
    def test_keys(self):
        '''
        Tests the Message.keys() functionality.
        '''
        keys = list(self.msg.keys())
        assert len(keys) == 3
        assert keys[0] == 'a'
        assert keys[1] == 'b'
        assert keys[2] == 'c'
        
        
    def test_len(self):
        '''
        Tests that len(Message) returns the proper value.
        '''
        assert len(self.msg) == 3
    
    
    def test_values(self):
        '''
        Tests that the list returned by Message.values() matches up.
        '''
        values = list(self.msg.values())
        assert len(values) == 3
        assert values[0] == 0
        assert values[1] == 1
        assert values[2] == 2
        
        
def test():
    unittest.main()
    

if __name__ == '__main__':
    test()

