# -*- coding: utf-8 -*-

import syslog
import os
import os.path
import imp
import subprocess
import unicodedata
import xmlrpclib
from ConfigurationManager import *
from ClassPam import *
import random
import string
import glib
import time
import threading
import datetime
import time
import netifaces
import traceback
import grp
import pwd
import sys

threading._DummyThread._Thread__stop = lambda x: 42

LOG_FILE="/var/log/n4d/error_log"
CUSTOM_LOCAL_DISPATCH_DIR="/usr/share/n4d/xmlrpc-server/custom-local-dispatch/"
N4D_ID=random.random()
ONE_SHOT_LOG="/tmp/n4d-oneshot.log"
N4D_TOKEN="/tmp/.n4d_pid"

AUTHENTICATION_ERROR=0
NOT_ALLOWED=1
METHOD_NOT_FOUND=2
CLASS_NOT_FOUND=2.1
RUN=3
UNSECURE_METHOD=4

roottry = 0
filerootpass = "/etc/n4d/key"

CUSTOM_VARIABLES_PATH="/usr/share/n4d/xmlrpc-server/custom-variables/"
POST_INIT_CUSTOM_VARIABLES_PATH="/usr/share/n4d/xmlrpc-server/post-init-custom-variables/"
CUSTOM_DISPATCH_LOGIC="/usr/share/n4d/xmlrpc-server/custom-remote-dispatch-logic.py"


configuration_path="/etc/n4d/conf.d"
#class_skel="/usr/share/n4d/xmlrpc-server/class_skel.py"
perl_class_skel="/usr/share/n4d/xmlrpc-server/perl_support/class_skel.py"
perl_function_skel="/usr/share/n4d/xmlrpc-server/perl_support/function_skel.py"
ONE_SHOT_PATH="/etc/n4d/one-shot/"

objects={}



class_skel="import subprocess\nclass %CLASSNAME%:\n"
method_skel="\tdef %METHOD%(self,*params):\n\t\tpopen_list=[]\n\t\tpopen_list.append('%BINARY%')\n\t\tfor param in params:\n\t\t\tpopen_list.append(str(param))\n\t\tprint('[BINARY-PLUGIN] Before execution...')\n\t\toutput = subprocess.Popen(popen_list, stdout=subprocess.PIPE).communicate()[0]\n\t\tprint('[BINARY-PLUGIN] Execution returns ' + str(output))\n\t\treturn output\n\n"




class n4dlog(object):
	
	def __init__(self,f):
		
		self.f=f
	
	def __get__(self,obj,type=None):
		
		return self.__class__(self.f.__get__(obj,type))

	def __call__(self,*args,**kw):
		
		try:
			return self.f(*args,**kw)
		except Exception as e:
			mode="w"
			if os.path.exists(LOG_FILE):
				mode="a"
				
			f=open(LOG_FILE,mode)
			f.write("\n")
			f.write(traceback.format_exc())
			f.close()
			raise e
			
				
		
#def call
	
#class n4dlog

class ServiceManager:
	
	path="/etc/n4d/controlled-startups.d/"

	def __init__(self):
		
		self.enabled_services=[]
		self.get_list()
		
		
	def get_list(self):
		self.enabled_services=[]
		for item in os.listdir(ServiceManager.path):
			if os.path.isfile(ServiceManager.path+item):
				self.enabled_services.append(item)
		
	#def init
	
	
#class ServiceManager
	

	
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



print("\n[CORE] Starting N4D ...")



def clear_credentials():
	
	print "Clearing credentials..."
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

		print("[ONE-SHOT] Executing one-shots...")

		while(wait):
			processes=cs.find_process("dpkg")
			if processes==None:
				wait=False

			time.sleep(2)
			
		if len(one_shot_list) > 0:
			f=open(ONE_SHOT_LOG,"w")
		for item in one_shot_list:
			print("\t" + str(item) + "...")
			'''
			p=subprocess.Popen(ONE_SHOT_PATH+item)
			p.wait()
			'''
			ret=os.system(ONE_SHOT_PATH+item)
			if ret==0:
				f.write(item +" OK\n")
			else:
				f.write(item +" FAILED WITH EXIT STATUS " + str(ret) + "\n")
			try:
				os.remove(ONE_SHOT_PATH+item)
			except:
				pass
			

t=threading.Thread(target=one_shot)
t.daemon=True
t.start()


# CUSTOM VARIABLES

print("[CORE] Loading custom variables ... ")
flist=os.listdir(CUSTOM_VARIABLES_PATH)

for file in flist:
	if file.endswith(".py"):
		path=CUSTOM_VARIABLES_PATH+file
		sys.stdout.write("\t " + path + " ... ")
		try:
			execfile(path)
			print("OK")
		except Exception as e:
			print("FAILED")
			sys.stdout.write("\t\t[!] ")
			print(e)
			
	

# IMPORTING CLASSES

cm=ConfigurationManager(configuration_path)
remotefunctions = []

def load_plugin(plugin):
	
	global class_skel
	global method_skel
	global objects
	
	if plugin.class_name!="VariablesManager":
		sys.stdout.write( "\t["+plugin.class_name+"] " + plugin.path + " ... " )
	else:
		print( "\t["+plugin.class_name+"] " + plugin.path + " ... " )
	
	if plugin.type=="python" and plugin.path!=None and os.path.exists(plugin.path):
		try:
			
			execfile(plugin.path,globals())
			s=globals()[plugin.class_name]()
			objects[plugin.class_name]=s
			if plugin.class_name!="VariablesManager":
				print("OK")
		except Exception as e:
			print("FAILED")
			sys.stdout.write("\t\t[!] ")
			print(e)
			

	if plugin.type=="binary" and plugin.path!=None and os.path.exists(plugin.path):
		
		
		code=class_skel
		code=code.replace("%CLASSNAME%",plugin.class_name)
		
		
		for method in plugin.function:
			
			tmp=method_skel
			if len(plugin.function)>=1 and plugin.standalone==False:
				tmp=tmp.replace("popen_list.append('%BINARY%')","popen_list.append('%BINARY%')\n\t\tpopen_list.append('%METHOD%')")
			tmp=tmp.replace("%METHOD%",method)
			tmp=tmp.replace("%METHOD%",plugin.bin_name)
			tmp=tmp.replace("%BINARY%",plugin.path)
				
			code+=tmp		
		
		#print code
		try:
			exec(code,globals())
			s=globals()[plugin.class_name]()
			objects[plugin.class_name]=s
			print("OK")
		except Exception as e:
			print("FAILED")
			sys.stdout.write("\t\t[!] ")
			print(e)
		

	if plugin.type=="perl" and plugin.path!=None and os.path.exists(plugin.path):
		cf = open(perl_class_skel,'r')
		ff = open(perl_function_skel,'r')
		lines = cf.readlines()
		code = "".join(lines)
		code = code.replace("%CLASSNAME%",plugin.class_name)
		cf.close()
		lines = ff.readlines()
		function_template = "".join(lines)
		ff.close()
		for aux_func in plugin.function.keys():
			a = function_template
			a = a.replace("%CLASSNAME%",plugin.class_name)
			a = a.replace("%METHOD%",aux_func)
			code += a
		try:
			exec(code,globals())
			s=globals()[plugin.class_name]()
			objects[plugin.class_name]=s
		except Exception as e:
			print("FAILED")
			sys.stdout.write("\t\t[!] ")
			print(e)

	if plugin.type=="remote":
		server = {}
		server["ip"] = plugin.remoteip
		server["order"] = int(plugin.order)
		server["function"] = plugin.functionremote
		remotefunctions.append(server)	
	
	
#def load_plugin
		

# CUSTOM VARIABLES

print("[CORE] Loading post init custom variables ... ")
flist=os.listdir(POST_INIT_CUSTOM_VARIABLES_PATH)

for file in flist:
	if file.endswith(".py"):
		path=POST_INIT_CUSTOM_VARIABLES_PATH+file
		sys.stdout.write("\t " + path + " ... ")
		try:
			execfile(path)
			print("OK")
		except Exception as e:
			print("FAILED")
			sys.stdout("\t\t[!] ")
			print(e)
			

def load_external_module(code,plugin_conf):
	global cm
	global objects
	try:
		exec(code)
		s=locals()[plugin_conf.class_name]()
		objects[plugin_conf.class_name]=s
		cm.plugins.append(plugin_conf)
		return (True,)
	except Exception as e:
		return (False,e)
	

def load_module_by_conf_file(etc_file):
	
	global cm
	global objects
	print ("[CORE] Loading module by conf file " + etc_file + " ...")
	try:
		plugin=cm.load_plugin(etc_file)
		if plugin!=None:
			load_plugin(plugin)
			count=0
			for item in cm.plugins:
				if item.class_name==plugin.class_name:
					cm.plugins.pop(count)
					break
				count+=1
			cm.plugins.append(plugin)
			startup_launcher(objects)
			return (True,True)
	except Exception as e:
		print(e)
		return (False,e)
	
#load_module_by_file

def load_new_modules(path=configuration_path):
	
	global cm
	global objects
	
	file_list=os.listdir(path)
	print("[CORE] Loading new modules...")
	for file in file_list:
		file_path=path+"/"+file
		try:
			plugin=cm.load_plugin(file_path)
		except:
			plugin=None

		if plugin!=None:
			if plugin.class_name not in objects:
				try:
					print("\t[*] Loading " + plugin.class_name +" ...")
					load_plugin(plugin)
					cm.plugins.append(plugin)
					#return (True,plugin.class_name)
				except Exception as e:
					print(e)
					#return(False,e)
			else:
				print("\t[!] " + plugin.class_name + " already loaded. Skipping...")
				
	
	return True
	
	
#def load_new_modules

def unload_module(conf_file):

	global cm
	global objects
	plugin=cm.load_plugin(conf_file)

	if plugin==None:
		print("[CORE] Unable to unload " + conf_file)
		return "Unable to load " + conf_file
	
	count=0
	for item in cm.plugins:
		if plugin.class_name==item.class_name:
			cm.plugins.pop(count)
			
			break
		count+=1
	
	objects.pop(plugin.class_name)
	print("[CORE] Removing " + plugin.class_name + " ...")
	return True
	
	
	
#def unload_module


# installed plugins loading

print("[CORE] Loading installed plugins...")
for plugin in cm.plugins:
	load_plugin(plugin)
	
#


sm=ServiceManager()

# STARTUP

N4DLOGSTARTUP = '/var/log/n4d/startup'

executed_objects = []

def startup_launcher(objects_list):
	print("[CORE] Executing startups ... ")
	global executed_objects
	withstartup = []
	next_objects = []
	filelog = open(N4DLOGSTARTUP,'a')
	sm.get_list()
	for x in objects_list.keys():
		try:
			if x in executed_objects:
				continue
			callable(getattr(objects_list[x],'startup'))
			options={}
			# FILTER CODE GOES HERE
			if x in sm.enabled_services:
				options["controlled"]=True
			else:
				options["controlled"]=False
			#
			
			#FIRST BOOT CODE GOES HERE
			options["boot"]=False
			if not os.path.exists(N4D_TOKEN):
				options["boot"]=True
				
			withstartup.append((objects_list[x],options))
			
		except Exception as e:
			pass
	change = True
	while change:
		change = False
		for x in range(len(withstartup)-1,-1,-1):
			if ( not hasattr(withstartup[x][0],'predepends') or len( set(withstartup[x][0].predepends) - set(executed_objects)) <= 0 ) \
			and ( not hasattr(withstartup[x][0],'next_to') or len( set(withstartup[x][0].next_to) - set(next_objects)) <= 0):
				try:
					print("\t[STARTUP] Executing " +  withstartup[x][0].__class__.__name__ + " with options " +  str(withstartup[x][1]) + " ...")
					withstartup[x][0].startup(withstartup[x][1])
					executed_objects.append(withstartup[x][0].__class__.__name__)
				except Exception as e:
					filelog.write( "[ "+datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S") + " ] Class " + withstartup[x][0].__class__.__name__ + " had an error on startup method because " + str(e) + "\n")
				next_objects.append(withstartup[x][0].__class__.__name__)
				withstartup.pop(x)
				change = True
	for x in withstartup:
		filelog.write("[ "+datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S") + " ] Class " +x.__class__.__name__+" can't be executed. Check if depends exists or had an error when launching startup method\n")
	filelog.close()

	f=open(N4D_TOKEN,"w")
	f.write(str(os.getpid()))
	f.close()

	
	
#def startup_launcher




p=threading.Thread(target=startup_launcher,args=(objects,))
p.daemon=True
p.start()


#  APT LAUNCHER

N4DLOGAPT='/var/log/n4d/apt'

def apt_launcher():
	sm.get_list()
	f=open(N4DLOGAPT,"a")
	f.write("["+datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S")+"] Executing n4d-apt...\n")
	for plugin in sorted(objects.keys()):
	
		try:
			if hasattr(objects[plugin],"apt") and callable(getattr(objects[plugin],"apt")) and plugin not in sm.enabled_services:
				f.write("["+datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S") + "] Executing " + objects[plugin].__class__.__name__ + " ...\t")
				objects[plugin].apt()
				f.write("OK\n")
		except:
			f.write("FAILED [!]\n")
			
	f.write("["+datetime.datetime.today().strftime("%d/%m/%y %H:%M:%S") + "] n4d-apt done\n")
	f.close()
	
	return True
	
#def apt_launcher





	
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


def get_methods(params):
	
	ret=""
	filter_class = []
	if len(params) > 0 :
		filter_class = params[0]
		
	processed=[]
	for i in range(len(cm.plugins)-1,-1,-1):
		plugin=cm.plugins[i]
		if plugin.class_name not in processed:
			processed.append(plugin.class_name)
			for method in plugin.function:
				groups=""
				for group in plugin.function[method]:
					groups+=group + " "
				if len(filter_class) == 0 or plugin.class_name in filter_class: 
					ret+="[" + plugin.class_name + "] " + method + " : " + groups + "\n"
			if plugin.type=="remote":
				for method in plugin.functionremote:
					if len(filter_class) == 0 or plugin.class_name in filter_class :
						ret+="(r:" + plugin.remoteip + ")["+ method[1:method.find(")")]+"] " + method[method.find(")")+1:] + "\n"
	return ret	
	
#def get_methods


def get_sorted_methods():
	
	ret={}
	
	for plugin in cm.plugins:
		methods=[]
		for method in plugin.function:
			methods.append(method)
		ret[plugin.class_name]=methods
		
	return ret
	
	
#def get_sorted_methods


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


def get_ip(dev):
	'''
	Returns ip value from a certain network interface. It returns None on failure.
	ex:
		get_ip("eth0")
	'''	
	try:
		info=get_device_info(dev)
		return info["ip"]
	except Exception as e:
		print e
		return None
	
#def get_ip



def get_net_size(netmask):
	'''
	Calculates bitmask from netmask
	ex:
		get_broadcast("eth0")
	'''
	netmask=netmask.split(".")
	binary_str = ''
	for octet in netmask:
		binary_str += bin(int(octet))[2:].zfill(8)
	return str(len(binary_str.rstrip('0')))

#def get_net_size

def get_device_info(dev):
	'''
	Returns a dictionary with the information of a certain network interface.
	ex:
		get_device_info("eth0")
	'''	
	dic={}
	for item in netifaces.interfaces():
		if item==dev:
			info=netifaces.ifaddresses(item)
			dic["name"]=item
			if info.has_key(netifaces.AF_LINK):
				if info[netifaces.AF_LINK][0].has_key("addr"):
					dic["mac"]=info[netifaces.AF_LINK][0]["addr"]
				else:
					dic["mac"]=""
			if info.has_key(netifaces.AF_INET):
				if info[netifaces.AF_INET][0].has_key("broadcast"):
					dic["broadcast"]=info[netifaces.AF_INET][0]["broadcast"]
				else:
					dic["broadcast"]=""
				if info[netifaces.AF_INET][0].has_key("netmask"):
					dic["netmask"]=info[netifaces.AF_INET][0]["netmask"]
					dic["bitmask"]=get_net_size(dic["netmask"])
				else:
					dic["bitmask"]=""
					dic["netmask"]=""
				if info[netifaces.AF_INET][0].has_key("addr"):
					dic["ip"]=info[netifaces.AF_INET][0]["addr"]
				else:
					dic["ip"]=""
			
	return dic
	
#def get_device_info

def get_all_ips():
	
	ret=set()
	ret.add("127.0.0.1")
	for item in netifaces.interfaces():
		
			ret.add(get_device_info(item)["ip"])
		
	return list(ret)
	
#def get_all_ips


def validate_user(user,password):
	
	pv= PamValidate()
	if pv.authentication(user,password):
		
		groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
		gid = pwd.getpwnam(user).pw_gid
		groups.append(grp.getgrgid(gid).gr_name)		
		
		return (True,groups)
	else:
		return (False,[])
	
#def validate_user


class Core:
	'''N4D Core'''	
	
	debug=True
	roottry=0

	skynet="https://anubis:9779"
	learn=False
	store_lessons=False
	

	if os.path.exists(CUSTOM_DISPATCH_LOGIC):
		execfile(CUSTOM_DISPATCH_LOGIC)
	else:
		def custom_remote_dispatch_logic(self):
			return True

	def __init__(self):

		global master_password
		global objects
		global cm
		self.cm=cm
		self.objects=objects
		self.master_password=master_password
		self.credentials={}
		self.run=True
		import threading
		t=threading.Thread(target=self.clear_credentials,args=())
		t.daemon=True
		t.start()
		
	def launch_triggers(self):
		
		for item in self.objects:
			print self.objects[item]
		
	#def launch_triggers
		
	def init_daemon(self):
		
		glib.timeout_add(5000,self.clear_credentials)
		import gobject
		gtk.main()
	
		
	def clear_credentials(self):
		while True:
			time.sleep(10)
		self.grace_time=0
		while True:
			time.sleep(self.grace_time)
			print "[CREDENTIALS CACHE] CLEARING CACHE"
			self.credentials={}
			self.grace_time=0
			
			time.sleep(200)


	def dprint(self,data):
		if Core.debug:
			print data
			
	def get_all_ips(self):
		return get_all_ips()
	
	@n4dlog
	def _dispatch(self,method,params):


		client_address=params[0]
		params=params[1:]
		
		if method=="register_credentials":

			print "registering credentials..."

			if client_address in get_all_ips():
				#home
				try:
					if len(params)==2:
						if params[0]==self.master_password:
							try:
								tmp_user,tmp_pass=params[1]
							except:
								return(False,"Second parameter must be a tuple containing user and password")
								
							self.credentials[tmp_user]=tmp_pass
							self.grace_time=60
							return(True,"Credentials registered")
							
							
						else:
							return(False,"Key authentication error")
					else:
						return(False,"Invalid arguments for register_credentials(n4d_key,(user,password))")
						
				except Exception as e:
					return (False,str(e))
			else:
				#away
				print("client is not at home")
				'''
				try:
					if type(params[0])==type(("","")):
						tmp_user,tmp_pass=params[0]
						aux = PamValidate()
						if aux.authentication(tmp_user,tmp_pass):
							self.credentials[tmp_user]=tmp_pass
							self.grace_time=60
							return(True,"Credentials registered")
						else:
							
							
					else:
						return(False,"First parameter must be a tuple containing user and password")
						
				except Exception as e:
					return(False,str(e))
				'''
				return(False,"Function not supported remotely")
		
		if method=="get_methods":
			return get_methods(params)
		if method=="get_sorted_methods":
			try:
				return get_sorted_methods()
			except Exception as e:
				print e
				return "ERROR CONNECTING TO SKYNET"
				
		if method=="get_n4d_id":
			return str(N4D_ID)
			
		if method=="get_ip":
			try:
				ret=get_ip(params[0])
			except:
				ret=""
			return ret
		
		if method=="apt":
			if params[0]==self.master_password:
				return (True,apt_launcher())
			else:
				return (False,"AUTHENTICATION ERROR")
		
		if method=="load_module":
			if params[0]==self.master_password:
				try:
					return load_module_by_conf_file(params[1])
				except Exception as e:
					return (False,e)
					
			else:
				return (False,"AUTHENTICATION ERROR")
					
		if method=="load_new_modules":
			if params[0]==self.master_password:
				try:
					if len(params)==1:
						return (True,load_new_modules())
					if len(params)>1:
						if type(params[1])==type(""):
							return (True,load_new_modules(params[1]))
						else:
							return (False,"Second parameter must be a system path")
				except Exception as e:
					return (False,e)
			else:
				return (False,"AUTHENTICATION ERROR")
					
		if method=="unload_module":

			if params[0]==self.master_password:
				try:
					if len(params)>1:
						if type(params[1])==type(""):
							return (True,unload_module(params[1]))
						else:
							return (False,"Second parameter must be a system path")
				except Exception as e:
					return (False,e)
			else:
				return (False,"AUTHENTICATION ERROR")
				
		if method=="get_service_list":
			global sm
			ret={}
			sm.get_list()
			ret["enabled"]=sm.enabled_services
			ret["disabled"]=[]
			for item in objects:
				if item not in sm.enabled_services:
					ret["disabled"].append(item)
					
			return ret
			
		if method=="is_controlled_startup":
			try:
				global sm
				ret={}
				sm.get_list()
				ret["enabled"]=sm.enabled_services

				if params[0] not in ret["enabled"]:
					return False
				else:
					return True
			except:
				return False

				
			
		if method=="validate_user":
			try:
				return validate_user(params[0],params[1])
			except Exception as e:
				print(e)
				return False
				

		user=None
		
		try:
			user,password,remote_user,remote_password=params[0]
		except:
			try:
				user,password=params[0]
				remote_user=user
				remote_password=password

			except:
				try:
					if params[0] == "":
						user="anonymous"
						password=""
					else:
						user="root"
						password=params[0]
					remote_user=user
			
					remote_password=params[0]
				except Exception as e:
					return "FUNCTION NOT SUPPORTED"
		try:
			class_name=params[1]
			new_params=params[2:]
		except:
			return "FUNCTION NOT SUPPORTED"

		
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
		self.dprint("[" + user + "@"+client_address+"] " + "Execution of method [" + method + "] from class " + class_name)
		#self.dprint("")

		ret=self.validate_function(params[0],class_name,method,new_params,client_address)

		try:
			ret,new_params=ret
		except:
			pass


		if ret ==RUN:
			
			add_n4d_id(method,user,password)
			try:
				ret=getattr(objects[class_name],method)(*new_params)
				return ret
			except Exception as e:
				return {"status":False,"msg":"Exception captured by core: " + str(e),"function":method,"class_name":class_name,"parameters":new_params}
			
		if ret==METHOD_NOT_FOUND:
			
			return "FUNCTION NOT SUPPORTED"
			
		if ret==AUTHENTICATION_ERROR:
			list_users = []
			for x in pwd.getpwall():
				if x.pw_uid >= 1000 :
					list_users.append(x[0])
			if user in list_users:
				return "USER AND/OR PASSWORD ERROR"
			return "USER DOES NOT EXIST"
			
		if ret==NOT_ALLOWED:
			
			return "METHOD NOT ALLOWED FOR YOUR GROUPS"
			
		if ret==UNSECURE_METHOD:
			
			return "METHOD IS BEING CALLED IN AN UNSECURED WAY. USER PARAMETER MUST MATCH USER CLIENT INFO"
			
		if ret==CLASS_NOT_FOUND:
			
			return "CLASS NOT FOUND"
	
	#def dispatch

	
	
	def validate_function(self,user_password,class_name,method,new_params,client_address=None):
		userandpassword = True
		validate=True
		user_found=False
		try:
			user,password = user_password
			
		except:

			if user_password!="":
				password = user_password
				user="root"
				
				if password == self.master_password:
					user_found=True
					validate=False
					grouplist=["root"]
					
					'''
					if class_name in objects:
						for plugin in cm.plugins:
							if plugin.class_name==class_name:
								if method in plugin.function:
									user_found=True
							
						return METHOD_NOT_FOUND
						
					else:
						return CLASS_NOT_FOUND
					'''

				else:
					user_found=False
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
						
				
				except Exception as e:
					#print(e)
					pass
				
				
			if "NTicketManager" in objects:
				print("[NTicketManager] PLUGIN AVAILABLE. CHECKING USER...")
				if user in objects["NTicketManager"].tickets:
					if objects["NTicketManager"].tickets[user]["password"]==password and objects["NTicketManager"].tickets[user]["date"] + objects["NTicketManager"].ALIVE_TIME >= time.time():
						print("[NTicketManager] USER VALIDATION OK")
						user_found=True
						paux = subprocess.Popen(["groups",user],stdout = subprocess.PIPE,stderr = subprocess.PIPE)
						cnaux = paux.stdout.readline().replace("\n","")
						grouplist = cnaux.split(":")[1].lstrip().split(" ")
						grouplist.append('*')
						grouplist.append('anonymous')						
						user_found=True
						lets_pam=False
					else:
						print("[NTicketManager] USER VALIDATION ERROR. LEAVING IT TO PAM")
				else:
					print("[NTicketManager] USER NOT FOUND")
			if lets_pam and not user_found:
					
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
						self.dprint("\tThis function can be executed by: %s"%plugin.function[m])
						for group in grouplist:
							if group in plugin.function[m] or group=="root":

								count=0
								tmp=list(new_params)
								
								if len(tmp)>0:
									for item in plugin.secure_order:
										secure_type,variable_name=item
										if len(secure_type)>0:
											if m in secure_type:
												tmp[count]=locals()[variable_name]
											
											count+=1
								new_params=tuple(tmp)
								return (RUN,new_params)
							
						return NOT_ALLOWED	
						
			
			if Core.learn:
				
				print "trying skynet:" + Core.skynet
				server = xmlrpclib.ServerProxy(Core.skynet)
				
				lessons=server.get_sorted_methods()
				print lessons
				for lesson in lessons:
					print lesson,"=?",class_name
					if lesson == class_name:
						print 3
						for chapter in lessons[class_name]:
							print "!",chapter,"=?", method
							if chapter == method:
								print 4
								data=server.get_lesson("","LessonManager",lesson)
								print 5
								print data
								if data!=False:
									plugin_info,code=data
									print "Trying to learn..."
									
									plug=PluginInfo()
									
									plug.path=plugin_info["path"]
									plug.type=plugin_info["type"]
									plug.class_name=plugin_info["class_name"]
									plug.function=plugin_info["function"]
									plug.bin_name=plugin_info["bin_name"]
									plug.args=plugin_info["args"]
									
									load_external_module(code,plug)
									
									print "Now I know " + plug.class_name
									
									return self.validate_function(user_password,class_name,method,new_params)
									
			
			return METHOD_NOT_FOUND
			
		else:
			return AUTHENTICATION_ERROR # USER NOT FOUND
			
		
		
	#def validate_function
					

	
#class core

if __name__=="__main__":
	core=Core()
	
	
