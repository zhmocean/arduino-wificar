import socket
import struct
import hashlib
import threading,random
import base64
import time
import serial
import sys

connectionlist = {}

class WebSocket(threading.Thread):
        
    def __init__(self,conn,remote, path="/"):
        threading.Thread.__init__(self)
        self.conn = conn
        self.remote = remote
        self.path = path
        self.index = 0
        self.buffer = ""
        self.socketVersion = ""
        
    def run(self):
        print 'Socket%s Start!' % self.index
        headers = {}
        self.handshaken = False

        while True:
            time.sleep(0.01)
            if not self.handshaken:
                print 'Socket%s Start Handshaken with %s!' % (self.index,self.remote)
                self.buffer += self.conn.recv(1024)
                print self.buffer
                if self.buffer.find('\r\n\r\n') != -1:
                    header, data = self.buffer.split('\r\n\r\n', 1)
                    for line in header.split("\r\n")[1:]:
                        key, value = line.split(": ", 1)
                        headers[key] = value

                    headers["Location"] = "ws://%s%s" %(headers["Host"], self.path)
                    if headers.has_key("Sec-WebSocket-Version"):
                        self.socketVersion = headers["Sec-WebSocket-Version"]
						
                    if self.socketVersion == "13":
                        key = headers["Sec-WebSocket-Key"]
                        token = base64.encodestring(hashlib.sha1(key +"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest())
                        handshake = '\
HTTP/1.1 101 Switching Protocols\r\n\
Upgrade: websocket\r\n\
Connection: Upgrade\r\n\
WebSocket-Origin: %s\r\n\
WebSocket-Location: %s\r\n\
Sec-WebSocket-Accept: %s\r\n\
'%(headers['Origin'], headers['Location'],token)          
                    else:
                        key1 = headers["Sec-WebSocket-Key1"]
                        key2 = headers["Sec-WebSocket-Key2"]
                        if len(data) < 8:
                            data += self.conn.recv(8-len(data))
                        key3 = data[:8]
                        self.buffer = data[8:]
                        token = self.generate_token(key1, key2, key3)
                    
                        handshake = '\
HTTP/1.1 101 Web Socket Protocol Handshake\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Origin: %s\r\n\
Sec-WebSocket-Location: %s\r\n\r\n\
' %(headers['Origin'], headers['Location']) +token

                    print "sent response:"
                    print handshake
                    self.conn.send(handshake)
                    self.handshaken = True
                    print 'Socket%s Handshaken with %s success!' % (self.index,self.remote)
            else:
                if self.socketVersion == "13":
                    try:
                        data_head = self.conn.recv(1)
						
                        if repr(data_head)=='':
                            print "client closed"
                            self.onClose()
                            return
							
                        if len(data_head) ==0:
                            continue
                        print "aasdfsa:"+data_head+str(len(data_head))
                        
                        header = struct.unpack("B",data_head)[0]
                        opcode = header & 0b00001111
                        print "sign %d"%(opcode,)
                        
                        if opcode==8:
                            print "client closed"
                            self.onClose()
                            return
                        
                        data_length = self.conn.recv(1)
                        data_lengths= struct.unpack("B",data_length)
                        data_length = data_lengths[0]& 0b01111111
                        masking = data_lengths[0] >> 7
						
                        if data_length<=125:
                            payloadLength = data_length
                        elif data_length==126:
                            payloadLength = struct.unpack("H",self.conn.recv(2))[0]
                        elif data_length==127:
                            payloadLength = struct.unpack("Q",self.conn.recv(8))[0]
                        print "String length:%d"%(data_length,)
						
                        if masking==1:
                            maskingKey = self.conn.recv(4)
                            self.maskingKey = maskingKey
							
                        data = self.conn.recv(payloadLength)
                        if masking==1:
                            i = 0
                            true_data = ''
                            for d in data:
                                true_data += chr(ord(d) ^ ord(maskingKey[i%4]))
                                i += 1
                            self.onData(true_data)
                        else:
                            self.onData(data)
							
                    except Exception,e:
                        print e
                        self.onClose()
                        return        
                
                    
                else:
                    data = self.conn.recv(64)
                    if not data:
                        continue

                    self.buffer += data
                    if self.buffer.find("\xFF")!=-1:
                        s = self.buffer.split("\xFF")[0][1:]
    
                        print 'Socket%s Got msg:%s from %s!' % (self.index,s,self.remote)
                        ret = self.control_cmd(s)
                        self.buffer = ""
                        self.conn.send('\x00 I received:'+s +" R:"+ret+"\xFF")

    
    def generate_token(self, key1, key2, key3):
        num1 = int("".join([digit for digit in list(key1) if digit.isdigit()]))
        spaces1 = len([char for char in list(key1) if char == " "])
        num2 = int("".join([digit for digit in list(key2) if digit.isdigit()]))
        spaces2 = len([char for char in list(key2) if char == " "])

        combined = struct.pack(">II", num1/spaces1, num2/spaces2) + key3
        return hashlib.md5(combined).digest()
    
    def close(self):
        self.conn.close()    

    def control_cmd(self, msg):
        try:    
            if ser.isOpen():
                ser.write(msg)
        except Exception, e:
            print e
            return 'SERVIAL_ERROR'
        
        return 'OK'
 
        
    def onData(self,text) :
        msg = "i received: "+text
        print msg
        
        ret = self.control_cmd(msg)
        self.sendData(msg +" R:"+ret)
        
    
    def onClose(self):
        self.conn.close()
        
    def packData(self,text):
        return text
    
    def sendData(self,text) :
        
        text = self.packData(text)
        print "will send: "+text

        self.conn.send(struct.pack("!B",0x81))

        length = len(text)
        
        if length<=125:
            self.conn.send(struct.pack("!B",length))
            
        elif length<=65536:
            self.conn.send(struct.pack("!B",126))
            self.conn.send(struct.pack("!H",length))
        else:
            self.conn.send(struct.pack("!B",127))
            self.conn.send(struct.pack("!Q",length))

        self.conn.send(struct.pack("!%ds"%(length,),text))

class WebSocketServer(object):
    def __init__(self):
        self.socket = None
        self.webSocket = None
        
    def begin(self, com):
        print 'WebSocketServer Start!'
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("0.0.0.0",1234))
        self.socket.listen(50)
        
        global ser
        ser = serial.Serial(com, 9600); 
        
        while True:
            time.sleep(1)
			
            connection, address = self.socket.accept()
            webSocket = WebSocket(connection,address)
            webSocket.start()
            
if __name__ == "__main__":
    server = WebSocketServer()
    com = 'COM8'
    if len(sys.argv) > 1:
        com = sys.argv[1]
    server.begin(com)
            