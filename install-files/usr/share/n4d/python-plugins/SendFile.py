import os
import socket 
import ssl
import shutil
import random
import time

from xmlrpclib import *

class SendFile:
	
	def send_file_to_ip(self,ip,remote_auth,local_file,remote_file,file_perm):
		
		try:
			
			server = ServerProxy ("https://"+ip+":9779")
			try:
				user,password=remote_auth
				user_info=(user,password)
			except:
				# Master Key
				user_info=remote_auth
				
			#request_socket(self,owner,restricted,path=None)
			
			port=server.request_socket(user_info,"SocketManager",str(random.random()),False)
			
			#if it's not an integer
			if type(port)!=type(1):
				return (False, "Could not request socket: " + port)
				
			ret=server.start_socket(user_info,"SocketManager",port)
			time.sleep(0.5)

			local_file=local_file.encode("utf-8")
			remote_file=remote_file.encode("utf-8")
			
			
			f=open(local_file,"rb")
			ssl_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#ssl_socket=ssl.wrap_socket(s)
			ssl_socket.connect((ip,port))
			rfile=ssl_socket.makefile('wb')
			rfile.write("[N4D-HEADER-BEGIN]file_path="+remote_file+";file_perm="+str(file_perm)+"[N4D-HEADER-END]")
			shutil.copyfileobj(f,rfile)
			sz = os.fstat(f.fileno())[6]
			#ssl_socket.connect((ip,port))
			#ssl_socket.sendall("[N4D-HEADER-BEGIN]file_path="+remote_file+";file_perm="+str(file_perm)+"[N4D-HEADER-END]"+rfile.read())
			ret_value=True
			rfile.close()
			ssl_socket.close()
			f.close()		
			server.close_socket(user_info,"SocketManager",port)
			
			return (True,"Success")
			
		except Exception as e:
			print e
			return(False,"Could not connect to " + ip + " because " + str(e))
		
		
	#def send_file
	
	
	
	
#class SendFile