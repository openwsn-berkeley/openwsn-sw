
class ParserException(Exception):
    
    GENERIC          = 1
    TOO_SHORT        = 2
    UNKNOWN_OPTION   = 3
    NO_KEY           = 4
    NOT_IMPLEMENTED  = 5
    DESERIALIZE      = 6
    
    descriptions = { 
        GENERIC:        'generic parsing error',
        TOO_SHORT:      'input too short',
        WRONG_LENGTH:   'input of the wrong length',
        UNKNOWN_OPTION: 'no parser key',
        NO_KEY:         'no key',
        NOT_IMPLEMENTED:'not implemented',
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