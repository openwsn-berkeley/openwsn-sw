'''
Created on 24/08/2012

@author: xvilajosana
'''
class Event:
    '''
    \brief Representation of an event, in the event bus.
    
    Events are used to queue them up when emitted synchronously.
    '''
    def __init__(self, uri, args, minNumReceivers=None, maxNumReceivers=None):
        '''
        \brief Initializer.
        
        \param uri  The URI of the signal (a string). Can be a regular
                    expression.
        \param args Any arguments to be passed to the listeners.
        '''
        self._uri                 = uri
        self._args                = args
        self._minNumReceivers     = minNumReceivers
        self._maxNumReceivers     = maxNumReceivers

    def get_uri(self):
        return self._uri

    def get_args(self):
        return self._args
    
    def get_minNumReceivers(self):
        return self._minNumReceivers
    
    def get_maxNumReceivers(self):
        return self._maxNumReceivers
    
    def __str__(self):
        returnVal  = []
        returnVal += ['uri={0}'.format(self._uri)]
        returnVal += ['args={0}'.format(self._args)]
        returnVal += ['minNumReceivers={0}'.format(self._minNumReceivers)]
        returnVal += ['maxNumReceivers={0}'.format(self._maxNumReceivers)]
        return ' '.join(returnVal)