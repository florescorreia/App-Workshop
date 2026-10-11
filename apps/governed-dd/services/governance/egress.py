"""Tenant CONNECT proxy: exact configured provider hosts on TLS port 443 only."""
import os,select,socket,socketserver
ALLOWED=set(filter(None,os.environ.get('PROVIDER_HOSTS','').split(',')))
class Handler(socketserver.StreamRequestHandler):
 def handle(self):
  line=self.rfile.readline(4096).decode('ascii','strict').strip().split()
  if len(line)!=3 or line[0]!='CONNECT':self.wfile.write(b'HTTP/1.1 403 Forbidden\r\n\r\n');return
  host,sep,port=line[1].rpartition(':')
  if not sep or port!='443' or host not in ALLOWED:self.wfile.write(b'HTTP/1.1 403 Forbidden\r\n\r\n');return
  total=0
  while True:
   header=self.rfile.readline(4096);total+=len(header)
   if total>16384:return
   if header in (b'\r\n',b'\n',b''):break
  try:remote=socket.create_connection((host,443),timeout=30)
  except OSError:self.wfile.write(b'HTTP/1.1 502 Bad Gateway\r\n\r\n');return
  with remote:
   self.wfile.write(b'HTTP/1.1 200 Connection Established\r\n\r\n');self.wfile.flush()
   while True:
    readable,_,_=select.select([remote,self.connection],[],[],60)
    if not readable:return
    for source in readable:
     data=source.recv(65536)
     if not data:return
     (self.connection if source is remote else remote).sendall(data)
class Server(socketserver.ThreadingTCPServer):allow_reuse_address=True;daemon_threads=True
Server(('0.0.0.0',8888),Handler).serve_forever()
