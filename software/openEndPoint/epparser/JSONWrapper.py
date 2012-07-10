import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('JSONWrapper')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import json

class JSONWrapper():

   def json_repr(obj):
      return json.dumps(__serialize(obj))

#======================== private =========================================
   def __serialize(obj):
      """Recursively walk object's hierarchy."""
      if isinstance(obj, (bool, int, long, float, basestring)):
         return obj
      elif isinstance(obj, dict):
	 obj = obj.copy()
         for key in obj:
            obj[key] = __serialize(obj[key])
            return obj
      elif isinstance(obj, list):
         return [__serialize(item) for item in obj]
      elif isinstance(obj, tuple):
         return tuple(__serialize([item for item in obj]))
      elif hasattr(obj, '__dict__'):
         return __serialize(obj.__dict__)
      else:
         return repr(obj) # Don't know how to handle, convert to string
	  

