'''
Created on 24/08/2012

@author: xvilajosana
'''
import re

class Callback:
    '''
    \brief Representation of an callback, in the event bus.
    
    This object contains both the URI and the function to call.
    '''
    
    def  __init__(self, func, event_uri):
        '''
        \param func       The function to be called when the event is sent.
        \param event_uri  The URI of the signal (a string). Can be a regular
                          expression.
        '''
        # validate params
        assert func
        assert callable(func)
        if event_uri:
            assert isinstance(event_uri,str)
        
        # store params
        self._func           = func
        self._event_uri      = event_uri
        
        # local variables
        self._event_re       = None
        if event_uri:
            self._event_re   = re.compile(event_uri)
    
    #======================== public ==========================================
    
    def get_function(self):
        return self._func

    def get_event_uri(self):
        return self._event_uri
    
    def matches_uri(self, uri):
        assert uri
        assert isinstance(uri,str)
        
        if self._event_re is None:
            return True
        return self._event_re.match(uri)