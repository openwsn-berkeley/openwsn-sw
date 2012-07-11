class ParserException(Exception):
    
    def __init__(self, reason=''):
        self.value = reason

    def __str__(self) :
        return "{0}: {1}".format(self.__class__.__name__,
                                 self.value)

class UnexistingParserException(EngineException):
    pass

class OutputUnavailableException(EngineException):
    pass

class ParsingException(EngineException):
    pass

class PublishingException(EngineException):
    pass
