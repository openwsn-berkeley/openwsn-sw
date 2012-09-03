'''
Created on 24/08/2012

@author: xvilajosana
'''
class Event:
    '''
    \brief Representation of an event, in the event bus.
    
    Events are used to queue them up when emitted synchronously.
    '''
    def __init__(self, uri, args):
        '''
        \brief Initializer.
        
        \param uri  The URI of the signal (a string). Can be a regular
                    expression.
        \param args Any arguments to be passed to the listeners.
        '''
        self._uri       = uri
        self._args      = args

    def get_uri(self):
        return self._uri

    def get_args(self):
        return self._args