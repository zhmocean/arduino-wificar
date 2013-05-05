from gevent import monkey; monkey.patch_all()

from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin

import serial

class CarControlServer(BaseNamespace, BroadcastMixin):
    ser = None
    def on_cmd_send(self, msg):
        ret = self.control_cmd(msg)
        self.emit('msg_of_server', {'msg':'I recived: '+msg+' '+ret})
    
    def control_cmd(self, msg):
        self.__check_serial()
            
        try:    
            if self.ser.isOpen():
                self.ser.write(msg)
        except Exception, e:
            print e
            return 'SERVIAL_ERROR'
        
        return 'OK'

    def __check_serial(self):
        if not self.ser:
            try:
                self.ser = serial.Serial('COM8', 9600); 
            except:
                pass       
            
class Application(object):
    def __init__(self):
        self.buffer = []
        # Dummy request object to maintain state between Namespace
        # initialization.
        self.request = {
            'nicknames': [],
        }

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/')

        if not path:
            start_response('200 OK', [('Content-Type', 'text/html')])
            return ['<h1>Welcome. '
                'Try the <a href="/control.html">control</a> example.</h1>']

        if path.startswith('static/') or path == 'socketio-web.html' or path == 'websocket-web.html':
            try:
                data = open(path).read()
            except Exception:
                return not_found(start_response)

            if path.endswith(".js"):
                content_type = "text/javascript"
            elif path.endswith(".css"):
                content_type = "text/css"
            elif path.endswith(".swf"):
                content_type = "application/x-shockwave-flash"
            else:
                content_type = "text/html"

            start_response('200 OK', [('Content-Type', content_type)])
            return [data]

        if path.startswith("socket.io"):
            socketio_manage(environ, {'': CarControlServer}, self.request)
        else:
            return not_found(start_response)


def not_found(start_response):
    start_response('404 Not Found', [])
    return ['<h1>Not Found</h1>']


if __name__ == '__main__':
    print 'Listening on port 8080 and on port 843 (flash policy server)'
    SocketIOServer(('0.0.0.0', 8080), Application(),
        resource="socket.io", policy_server=True,
        policy_listener=('0.0.0.0', 10843)).serve_forever()
