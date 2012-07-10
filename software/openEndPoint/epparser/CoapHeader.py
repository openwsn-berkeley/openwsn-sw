import logging
import JSONWrapper
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('CoapHeader')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class CoapHeader:

    #Version
    def getVersion(self):
        return self.__version

    def setVersion(self, version):
        self.__version = version

    #Type
    def getType(self):
        return self.__type

    def setType(self, type):
        self.__type = type

    #Option
    def getOption(self):
        return self.__option

    def setOption(self, option):
        self.__option = option

    #Code
    def getCode(self):
        return self.__code

    def setCode(self, code):
        self.__code = code
   
    #Code
    def getMID(self):
        return self.__mId

    def setMID(self, mId):
        self.__mId = mId
    
    #OptionList
    def getOptionList(self):
        return self.__optionList

    def setOptionList(self, optionList):
        self.__optionList = optionList      

#TODO check this error
#File " ..... /software/openEndPoint/bin/EpLayerdebugCli/../../epparser/CoapHeader.py", line 62, in __repr__
#return self.toJSON(self)
#TypeError: toJSON() takes exactly 1 argument (2 given)

    def toJSON(self):
        json=JSONWrapper.JSONWrapper()
        return json.json_repr(self)

    def __str__( self ):
       return self.toJSON(self)

    def __repr__( self ):
       return self.toJSON(self)
       
    
