import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('JSONWrapper')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import json

class JSONWrapper:

   def json_repr(self,obj):
      log.debug(obj)
      return json.dumps(self._serialize(obj))

#======================== private =========================================
   def _serialize(self,obj):
      """Recursively walk object's hierarchy."""
      if isinstance(obj, (bool, int, long, float, basestring)):
         log.debug(obj)
         return obj
      elif isinstance(obj, dict):
         obj = obj.copy()
         for key in obj:
            obj[key] = self._serialize(obj[key])
         log.debug(obj) 
         return obj
      elif isinstance(obj, list):
         log.debug(obj) 
         return [self._serialize(item) for item in obj]
      elif isinstance(obj, tuple):
         log.debug(obj) 
         return tuple(self._serialize([item for item in obj]))
      elif hasattr(obj, '__dict__'):
         log.debug(obj) 
         return self._serialize(obj.__dict__)
      else:
         return str(obj) # Don't know how to handle, convert to string
      
