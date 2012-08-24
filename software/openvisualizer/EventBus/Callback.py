'''
Created on 24/08/2012

@author: xvilajosana
'''
import re

class Callback:
    def  __init__(self, func, event_uri = None):
        """
        @type  func: function
        @param func: The function to be called when the event is sent.
        @type  event_uri: string
        @param event_uri: The URI of the signal. Might be a regular expression.
        """
        assert func is not None
        self.__func      = func
        self.__event_uri = event_uri
        self.__event_re  = None
        if event_uri is not None:
            self.__event_re  = re.compile(event_uri)

    def get_function(self):
        return self.__func

    def get_event_uri(self):
        return self.__event_uri

    def matches_uri(self, uri):
        assert uri is not None
        if self.__event_re is None:
            return True
        return self.__event_re.match(uri)