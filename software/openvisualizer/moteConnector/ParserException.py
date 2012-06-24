
class ParserException(Exception):
    
    GENERIC          = 1
    
    descriptions = { 
        GENERIC:     'generic parsing error', 
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