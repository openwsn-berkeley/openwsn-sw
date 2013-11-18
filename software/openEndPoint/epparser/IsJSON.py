'''
Created on 11/07/2012

@author: xvilajosana
'''
import JSONWrapper

class IsJSON(object):
    '''
    classdocs
    '''


    def __init__(s):
        '''
        Constructor
        '''
        
    def toJSON(self):
        json=JSONWrapper.JSONWrapper()
        return json.json_repr(self)

    def __str__(self):
       return self.toJSON()