import logging


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('CoapHeader')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import IsJSON

class CoapHeader(IsJSON.IsJSON):

    #Version
    def getVersion(self):
        return self._version

    def setVersion(self, version):
        self._version = version

    #Type
    def getType(self):
        return self._type

    def setType(self, type):
        self._type = type

    #Option
    def getOption(self):
        return self._option

    def setOption(self, option):
        self._option = option

    #Code
    def getCode(self):
        return self._code

    def setCode(self, code):
        self._code = code
   
    #Code
    def getMID(self):
        return self._mId

    def setMID(self, mId):
        self._mId = mId
    
    #OptionList
    def getOptionList(self):
        return self._optionList

    def setOptionList(self, optionList):
        self._optionList = optionList      

    

       
    
