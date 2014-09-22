# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

class ParserException(Exception):
    
    GENERIC          = 1
    TOO_SHORT        = 2
    WRONG_LENGTH     = 3
    UNKNOWN_OPTION   = 4
    NO_KEY           = 5
    DESERIALIZE      = 6
    
    descriptions = { 
        GENERIC:        'generic parsing error',
        TOO_SHORT:      'input too short',
        WRONG_LENGTH:   'input of the wrong length',
        UNKNOWN_OPTION: 'no parser key',
        NO_KEY:         'no key',
        DESERIALIZE:    'deserialization error',
    }
    
    def __init__(self,errorCode,details=None):
        self.errorCode  = errorCode
        self.details    = details
    
    def __str__(self):
        try:
            output = self.descriptions[self.errorCode]
            if self.details:
                output += ': ' + str(self.details)
            return output
        except KeyError:
            return "Unknown error: #" + str(self.errorCode)