# -*- coding: utf-8 -*-

import syslog
import os
import os.path
import imp
import subprocess
import unicodedata
import xmlrpclib
from n4d.config.configurationmanager import *
from n4d.auth.pam import *
import random
import string
import glib
import time
import threading


class SystemProcess:
	
	def __init__(self):
		
		self.process_list=[]
		self.get_process_list()

	#def init 
	
	def get_process_list(self):
		
		self.process_list=[]
		
		p=subprocess.Popen(["ps","aux"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output=p.communicate()[0]
		lst=output.split("\n")
		lst.pop(0)
		
		for item in lst:
			processed_line=item.split(" ")
			tmp_list=[]
			
			if len(processed_line) >= 10:
				for object in processed_line:
					if object!="":
						tmp_list.append(object)
				processed_line=tmp_list
				
				process={}
				process["user"]=processed_line[0]
				process["pid"]=processed_line[1]
				process["cpu"]=processed_line[2]
				process["mem"]=processed_line[3]
				process["vsz"]=processed_line[4]
				process["rss"]=processed_line[5]
				process["tty"]=processed_line[6]
				process["stat"]=processed_line[7]
				process["start"]=processed_line[8]
				process["time"]=processed_line[9]
				cmd=""
				for string in processed_line[10:]:
					if cmd!="":
						cmd+=" "
					cmd+=string
					
				process["command"]=cmd.split(" ")[0]
				self.process_list.append(process)
		
	#def get_process_list
	
	
	def get_user_process_list(self,user):
		
		ret_list=[]
		
		for process in self.process_list:
			if process["user"]==user:
				ret_list.append(process)
				
		return ret_list
		
	#def get_user_process_list
	
	def find_process(self,filter):
		self.get_process_list()
		ret_list=[]
		for process in self.process_list:
			if filter in process["command"]:
				ret_list.append(process)
				
				
		if len(ret_list)>0:
			return ret_list
		else:
			return None
		
	#def find_process
	
	
#class SystemProcess






AUTHENTICATION_ERROR=0
NOT_ALLOWED=1
METHOD_NOT_FOUND=2
RUN=3
roottry = 0

filerootpass = "/etc/n4d/key"

CUSTOM_VARIABLES_PATH="/usr/share/n4d/xmlrpc-server/custom-variables/"
CUSTOM_DISPATCH_LOGIC="/usr/share/n4d/xmlrpc-server/custom-remote-dispatch-logic.py"


configuration_path="/etc/n4d/conf.d"
class_skel="/usr/share/n4d/xmlrpc-server/class_skel.py"

ONE_SHOT_PATH="/etc/n4d/one-shot/"

objects={}



def clear_credentials():
	
	print("Clearing credentials...")
	credentials={}
	return True
	
#def clear_credentials


def generate_rootpasswd():
	f = open(filerootpass,'w')
	generatepassword ="".join(random.sample(string.letters+string.digits, 50))
	f.write(generatepassword+"\n")
	f.close()
	prevmask = os.umask(0)
	os.chmod(filerootpass,0400)
	os.chown(filerootpass,0,0)
	os.umask(prevmask)
	readpass = generatepassword
	return readpass



# ONE SHOTS

def one_shot():
	
	cs=SystemProcess()

	one_shot_list=os.listdir(ONE_SHOT_PATH)

	wait=True

	if len(one_shot_list)>0:
		

		while(wait):
			processes=cs.find_process("dpkg")
			if processes==None:
				wait=False

			time.sleep(2)
			

		for item in one_shot_list:
			print (item)
			p=subprocess.Popen(ONE_SHOT_PATH+item)
			p.wait()
			os.remove(ONE_SHOT_PATH+item)
			

t=threading.Thread(target=one_shot)
t.daemon=True
t.start()




# CUSTOM VARIABLES

list=os.listdir(CUSTOM_VARIABLES_PATH)
for file in list:
	if file.find(".py")!=-1:
		if file.find(".pyc")==-1:
			execfile(CUSTOM_VARIABLES_PATH+file)
			

# IMPORTING CLASSES

cm=ConfigurationManager(configuration_path)
remotefunctions = []
for plugin in cm.plugins:
	
	if plugin.type=="python" and plugin.path!=None and os.path.exists(plugin.path):
		execfile(plugin.path)
		s=globals()[plugin.class_name]()
		objects[plugin.class_name]=s

	if plugin.type=="binary" and plugin.path!=None and os.path.exists(plugin.path):
		f=open(class_skel,'r')
		lines=f.readlines()
		code="".join(lines)
		code=code.replace("%CLASSNAME%",plugin.class_name)
		code=code.replace("%METHOD%",plugin.bin_name)
		code=code.replace("%BINARY%",plugin.path)
		exec(code)
		s=globals()[plugin.class_name]()
		objects[plugin.class_name]=s

	if plugin.type=="remote":
		server = {}
		server["ip"] = plugin.remoteip
		server["order"] = int(plugin.order)
		server["function"] = plugin.functionremote
		remotefunctions.append(server)
		
			


# OLD FUNCTION LIST

teachers_func_list=[]
students_func_list=[]
admin_func_list=[]
others_func_list=[]

for plugin in cm.plugins:
	for func in plugin.function:
			
		if "teachers" in plugin.function[func]:
			teachers_func_list.append(func)
			
		if "students" in plugin.function[func]:
			students_func_list.append(func)
			
		if "admin" in plugin.function[func]:
			admin_func_list.append(func)
			
		if "others" in plugin.function[func]:
			others_func_list.append(func)


f = open(filerootpass)
master_password = f.readline().strip('\n')
f.close()


def get_methods():
	
	ret=""
	
	for plugin in cm.plugins:
		for method in plugin.function:
			groups=""
			for group in plugin.function[method]:
				groups+=group + " "
			
			ret+="[" + plugin.class_name + "] " + method + " : " + groups + "\n"
		if plugin.type=="remote":
			for method in plugin.functionremote:
				ret+="(r:" + plugin.remoteip + ")["+ method[1:method.find(")")]+"] " + method[method.find(")")+1:] + "\n"
			
	return ret	
	
#def get_methods

n4d_id_list={}

def get_next_n4d_id():
	
	sorted_list=sorted(n4d_id_list)
	try:
		last=sorted_list[len(n4d_id_list)-1]
		last+=1
	except:
		last=0
		
	return last
	
#def get_next_n4d_id

def add_n4d_id(function,user,password):
	
	dic={}
	dic["method"]=function
	dic["user"]=user
	dic["password"]=password
	
	id=get_next_n4d_id()
	n4d_id_list[id]=dic
	
	return id
	
#def add n4d id






class Core:
	
	
	debug=True
	roottry=0
	

	if os.path.exists(CUSTOM_DISPATCH_LOGIC):
		execfile(CUSTOM_DISPATCH_LOGIC)
	else:
		def custom_remote_dispatch_logic(self):
			return True

	def __init__(self):
		global master_password
		self.master_password=master_password
		self.credentials={}
		self.run=True
		import threading
		t=threading.Thread(target=self.clear_credentials,args=())
		t.daemon=True
		t.start()
		
	def init_daemon(self):
		
		glib.timeout_add(5000,self.clear_credentials)
		import gobject
		gtk.main()
	
		
	def clear_credentials(self):
		while True:
			print("[CREDENTIALS CACHE] CLEARING CACHE")
			self.credentials={}
			import time
			time.sleep(200)


	def dprint(self,data):
		if Core.debug:
			print(data)
	
	def _dispatch(self,method,params):
		
		if method=="get_methods":
			return get_methods()
		try:
			user,password,remote_user,remote_password=params[0]
		except:
			try:
				user,password=params[0]
				remote_user=user
				remote_password=password
			except:
				if params[0] == "":
					user="anonymous"
					password=""
				else:
					user=""
					password=params[0]
				remote_user=user
				remote_password=params[0]
		class_name=params[1]
		new_params=params[2:]

		
		ret=self.custom_remote_dispatch_logic()
		

		if ret:
			order = -1
			found = False
			remoteip = ""
			for x in remotefunctions:
				if "("+class_name+")"+method in x["function"]:
					if order < x["order"]:
						order = x["order"]
						remoteip = x["ip"]
						found = True
			if found:
				try:
					server = xmlrpclib.ServerProxy("https://"+remoteip+":9779")
					remote_params=[]
					if user == "anonymous":
						remote_params.append("")
					elif user == "":
						remote_params.append(password)
					else:
						remote_params.append((remote_user,remote_password))					
					remote_params.append(class_name)
					for param in new_params:
						remote_params.append(param)
					add_n4d_id(method,user,password)
					return getattr(server,method)(*remote_params)
				except:
					return "false :error connecting to server"	


		
		self.dprint("")
		self.dprint("[" + user + "] " + "Execution of method [" + method + "] from class " + class_name)
		self.dprint("")

		ret=self.validate_function(params[0],class_name,method)

		if ret ==RUN:
			
			add_n4d_id(method,user,password)
			return getattr(objects[class_name],method)(*new_params)
			
		if ret==METHOD_NOT_FOUND:
			
			return "FUNCTION NOT SUPPORTED"
			
		if ret==AUTHENTICATION_ERROR:
			
			return "USER AUTHENTICATION ERROR"
			
		if ret==NOT_ALLOWED:
			
			return "METHOD NOT ALLOWED FOR YOUR GROUPS"
			
	
	#def dispatch

	
	
	def validate_function(self,user_password,class_name,method):
		userandpassword = True
		validate=True
		try:
			user,password = user_password
			
		except:
			
			if user_password!="":
				password = user_password
				
				
				
				if password == self.master_password:
					
					return RUN
				else:
					Core.roottry += 1
					if Core.roottry > 5 :
						Core.roottry = 0
						self.master_password=generate_rootpasswd()
						global master_password
						master_password=self.master_password
					return AUTHENTICATION_ERROR
			else:
				user="anonymous"
				validate=False
				grouplist=[]
				grouplist.append("anonymous")
				user_found=True
		
		lets_pam=True
			
		if validate:
			if user in self.credentials:
				try:
					if self.credentials[user] == password:
						print("[CREDENTIALS CACHE] FOUND")
						user_found=True
						paux = subprocess.Popen(["groups",user],stdout = subprocess.PIPE,stderr = subprocess.PIPE)
						cnaux = paux.stdout.readline().replace("\n","")
						grouplist = cnaux.split(":")[1].lstrip().split(" ")
						grouplist.append('*')
						grouplist.append('anonymous')						
						user_found=True
						lets_pam=False
				except:
					pass
				
			if lets_pam:
					
				aux = PamValidate()
				if aux.authentication(user,password):
					paux = subprocess.Popen(["groups",user],stdout = subprocess.PIPE,stderr = subprocess.PIPE)
					cnaux = paux.stdout.readline().replace("\n","")
					grouplist = cnaux.split(":")[1].lstrip().split(" ")
					grouplist.append('*')
					grouplist.append('anonymous')					
					user_found=True
					self.credentials[user]=password
				else:
					user_found=False

		
		if user_found:
		
			for plugin in cm.plugins:
				for m in plugin.function:
					if m==method and plugin.class_name==class_name:
						self.dprint("This function can be executed by: %s"%plugin.function[m])
						for group in grouplist:
							if group in plugin.function[m]:
								return RUN
							
						return NOT_ALLOWED	
						
				
			return METHOD_NOT_FOUND
			
		else:
			return AUTHENTICATION_ERROR # USER NOT FOUND
			
		
		
	#def validate_function
					

	
#class core

if __name__=="__main__":
	core=Core()
	
	
