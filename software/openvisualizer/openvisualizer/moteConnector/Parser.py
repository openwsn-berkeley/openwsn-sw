# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('Parser')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

from ParserException import ParserException

class ParsingKey(object):
    
    def __init__(self,index,val,parser):
        
        assert(index is not None)
        assert(val is not None)
        assert(parser is not None)
        
        self.index      = index
        self.val        = val
        self.parser     = parser
    
    def __str__(self):
        template        = "{0}={1}"
        output          = []
        output         += [template.format("index", self.index)]
        output         += [template.format("val",   self.val)]
        output         += [template.format("parser",self.parser)]
        return ' '.join(output)

class Parser(object):
    
    def __init__(self,headerLength):
        
        # log
        log.info("create instance")
        
        # store params
        self.headerLength         = headerLength
        
        # local variables
        self.parsingKeys          = []
        self.headerParsingKeys    = []
        self.named_tuple          = {}
    
    #======================== public ==========================================
    
    def parseInput(self,input):
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug("received input={0}".format(input))
        
        # ensure input not short longer than header
        self._checkLength(input)
        
        # parse the header
        # TODO
     
        # call the next header parser
        for key in self.parsingKeys:
            if input[key.index]==key.val:
                return key.parser(input[self.headerLength:])
        
        # if you get here, no key was found
     
        raise ParserException(ParserException.NO_KEY, "type={0} (\"{1}\")".format(
            input[0],
            chr(input[0])))
    
    #======================== private =========================================
    
    def _checkLength(self,input):
        if len(input)<self.headerLength:
            raise ParserException(ParserException.TOO_SHORT)
    
    def _addSubParser(self,index=None,val=None,parser=None):
        self.parsingKeys.append(ParsingKey(index,val,parser))