'''
Created on 24/08/2012

@author: xvilajosana
'''
class Event:
    """
    Events are used only internally by the event bus, to queue them up
    when emitted synchronously.
    """
    def __init__(self, uri, args):
        """
        @type  uri: string
        @param uri: The URI of the signal. Can be a regular expression.
        @type  args: object
        @param args: Any arguments that are passed to the listeners.
        """
        self.__uri  = uri
        self.__args = args

    def get_uri(self):
        return self.__uri

    def get_args(self):
        return self.__args