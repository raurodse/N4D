import socket
import threading
import os
import shutil
import multiprocessing
import ssl

class SocketManager:
	
	def __init__(self):
		
		self.socket_list={}
		self.port=9805
		
	#def __init__
	
	def request_socket(self,owner,restricted,path=None):
		
		if not restricted:
			print "[SocketManager] Creating not restricted socket..."
			socket_instance=SocketInstance(self.port,owner)
		else:
			print "[SocketManager] Creating restricted socket..."
			socket_instance=RestrictedSocketInstance(self.port,owner,path)
		self.socket_list[self.port]=socket_instance
		self.port+=1
				
		return self.port-1
		
	#def  request_socket
	
	def start_socket(self,port):
		
		try:
			t=threading.Thread(target=self.socket_list[port].start)
			t.daemon=True
			t.start()
			return True
			
		except Exception as e:
			
			print e
			return False
		
	#def start_socket

	def close_socket(self,port):
		
		try:
			self.socket_list[port].close()
		except:
			pass
			
		return True
		
	#def close_socket

#class SocketManager



class SocketInstance:
	
	def __init__(self,port,owner):
		
		self.owner=owner
		self.port=port
		self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind(("",port))
		self.socket_connection=[]
		self.address=[]
		self.status=0
		
	#def init
		
	def start(self):
		
		self.status=1
		self.socket.listen(1)
		while True:
			print "[SocketInstance:" + self.owner + "] Listening on port " + str(self.port) + "..."
			sc,address=self.socket.accept()
			#connstream=ssl.wrap_socket(sc,server_side=True,certfile="/etc/n4d/cert/n4dcert.pem",keyfile="/etc/n4d/cert/n4dkey.pem")
			connstream=sc
			self.socket_connection.append(connstream)
			self.address.append(address)
			t=threading.Thread(target=self.client_thread,args=(connstream,address))
			t.daemon=True
			t.start()
			
	#def start
		    

	def client_thread(self,sc,addr):

		first_message=True
		while True:
			data=sc.recv(1024)
			if first_message:
				
				header=data[data.find("[N4D-HEADER-BEGIN]")+len("[N4D-HEADER-BEGIN]"):data.find("[N4D-HEADER-END]")]
				count=0
				splitted_header=header.split(";")
				file_path=None
				file_perm=None
				for item in splitted_header:
					key,value=item.split("=")
					if key=="file_path":
						file_path=value
					if key=="file_perm":
						file_perm=value
					

				if file_path==None:
					break
				
				file=open(file_path,"wb")
				file.write(data[data.find("[N4D-HEADER-END]")+len("[N4D-HEADER-END]"):])
				first_message=False
				
			else:
				
				if len(data)>0:
					file.write(data)
				
				else:
					
					file.close()
					if file_perm!=None:
						self.chmod(file_path,file_perm)
					sc.close()
					
					break
		
		
	#def client_thread


	def chmod(self,file,mode):
		prevmask = os.umask(0)
		try:
			os.chmod(file,int(mode))
			os.umask(prevmask)
			return True
		except Exception as e:
			print e
			os.umask(prevmask)
			return False
	#def chmod
	
#class SocketInstace


class RestrictedSocketInstance(SocketInstance):
	
	def __init__(self,port,owner,path):
		
		SocketInstance.__init__(self,port,owner)
		self.path=path
		
	#def init
		
	def generate_file_name(self,from_user,file_name,path,queue,to_user=None):
		
		done=False
		counter=1
		
		original_path=path
		original_file_name=file_name
		file_name="["+from_user+"]_"+file_name
		
		
		if to_user!=None:
			user_uid=pwd.getpwnam(to_user)[2]
			user_gid=pwd.getpwnam(to_user)[3]
			os.setregid(0, user_gid)
			os.setreuid(0, user_uid)

		while not done:
			
			if os.path.exists(path+file_name) or os.path.exists(path+"."+file_name):
				tmp_list=original_file_name.split(".")
				tmp_list[0]=tmp_list[0]+"_("+str(counter)+")"
				file_name=".".join(tmp_list)
				file_name="["+from_user+"]_"+file_name
				counter+=1
			else:
				done=True
		
		f=open(path+"."+file_name,'w')
		f.close()	
		queue.put(file_name)
		
	#def generate_file_name


	def client_thread(self,sc,addr):

		first_message=True
		while True:
			data=sc.recv(1024)
			if first_message:
				
				header=data[data.find("[N4D-HEADER-BEGIN]")+len("[N4D-HEADER-BEGIN]"):data.find("[N4D-HEADER-END]")]
				from_user=header.split(";")[0].split("=")[1]
				file_name=header.split(";")[1].split("=")[1]
				queue=multiprocessing.Queue()
				p=multiprocessing.Process(target=self.generate_file_name,args=(from_user,file_name,self.path,queue,self.owner))
				p.start()
				p.join()
				fname=queue.get()
				file=open("/home/"+self.owner+"/."+fname,"wb")
				file.write(data[data.find("[N4D-HEADER-END]")+len("[N4D-HEADER-END]"):])
				first_message=False
				
			else:
				
				if len(data)>0:
					file.write(data)
				
				else:
					
					file.close()
					sc.close()
					p=multiprocessing.Process(target=self.move_file,args=("/home/"+self.owner+"/."+fname,self.path+fname.strip("."),self.owner))
					p.start()
					p.join()
					
					break
				
	#def client_thread

	def move_file(self,orig,dest,owner):
		
		user_uid=pwd.getpwnam(owner)[2]
		user_gid=pwd.getpwnam(owner)[3]
		os.chown(orig,user_uid,user_gid)
		os.setregid(0,user_gid)
		os.setreuid(0,user_uid)
		shutil.move(orig,dest)
		tmp=dest.split("/")
		tmp_file="." + tmp[len(tmp)-1]
		tmp_file_path="/".join(tmp[:len(tmp)-1]) + "/" + tmp_file
		os.remove(tmp_file_path)

	#def move_file

#def RestrictedSocketInstance
