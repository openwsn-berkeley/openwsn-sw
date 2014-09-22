import web

openWebApp_moteState_handlers = None

class moteState(object):
    def GET(self,stateName):
        try:
            jsonToReturn = openWebApp_moteState_handlers[0].getStateElem(stateName)
            web.header('Content-Type', 'text/json')
            return jsonToReturn
        except ValueError:
            raise web.notfound()

class index(object):
    def GET(self):
        return "Hello, World!"

class OpenWebApp(web.application):
    
    urls = (
        '/',               'index',
        '/moteState/(.*)', 'moteState',
    )
    
    def __init__(self, moteState_handlers):
        global openWebApp_moteState_handlers
        
        openWebApp_moteState_handlers = moteState_handlers
        
        # initialize parent class
        web.application.__init__(self,self.urls,globals())

###############################################################################

if __name__=='__main__':
    webapp = OpenWebApp()
    webapp.run()