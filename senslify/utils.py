# Name: util.py
# Module: senslify.util
# Since: July 20th, 2019
# Author: Christen Ford
# Description: Implements useful utility classes and methods.


class Message:
    '''
    Acts as an enhanced dictionary where keys can be directly accessed using the Message.key syntax.
    '''
    def __init__(self, **kwargs):
        '''
        Creates a new Message object with the indicated Keyword arguments.
        Arguments:
            kwargs: The Keyword arguments to create the Message from.
        '''
        self.__dict__ = kwargs
        
    
    def __bool__(self):
        '''
        Implements the standard Python idiom for checking if a data structure
        contains any elements.
        
        Allows for the following expressions:
            if msg:
                foo()
            elif not msg:
                bar()
        '''
        return len(self.__dict__) > 0
    
    
    def __contains__(self, key):
        '''
        Determines if the message contains a value corresponding to the 
        indicated key.
        Arguments:
            key: The key to check.
        '''
        return key in self.__dict__
    
    
    def __len__(self):
        '''
        Determines the number of key/value pairs in the Message.
        '''
        return len(self.__dict__)
    
    
    def clear(self):
        '''
        Empties the Message of all key/value pairs.
        '''
        return self.__dict__.clear()
    
    
    def get(self, key):
        '''
        Attempts to get the value corresponding to the indicated key.
        Raises a KeyError if the key is not in the Message.
        Arguments:
            key: The key of the value to retrieve.
        '''
        if key not in self.__dict__:
            raise KeyError
        return self.__dict__.get(key)
    
    
    def items(self):
        '''
        Gets a view on the key/value pairs of the Message.
        '''
        return self.__dict__.items()
    
    
    def keys(self):
        '''
        Gets a view on the keys stored in the Message.
        '''
        return self.__dict__.keys()
    
    
    def values(self):
        '''
        Gets a view of the values stored in the Message.
        '''
        return self.__dict__.values()

