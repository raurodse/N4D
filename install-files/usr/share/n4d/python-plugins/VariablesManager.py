import json
import os.path
import os
import time
import xmlrpclib
import socket
import netifaces
import re
import importlib
import sys

class VariablesManager:

	VARIABLES_FILE="/var/lib/n4d/variables"
	VARIABLES_DIR="/var/lib/n4d/variables-dir/"
	LOCK_FILE="/tmp/.llxvarlock"
	INBOX="/var/lib/n4d/variables-inbox/"
	TRASH="/var/lib/n4d/variables-trash/"
	CUSTOM_INSTALLATION_DIR="/usr/share/n4d/variablesmanager-funcs/"
	LOG="/var/log/n4d/variables-manager"
	
	def __init__(self):
		
		self.variables={}
		self.variables_ok=False
		if os.path.exists(VariablesManager.LOCK_FILE):
			os.remove(VariablesManager.LOCK_FILE)
			
			
		if os.path.exists(VariablesManager.VARIABLES_FILE):
			self.variables_ok,ret=self.load_json(VariablesManager.VARIABLES_FILE)
			try:
				os.remove(VariablesManager.VARIABLES_FILE)
			except:
				pass
		else:
			self.variables_ok,ret=self.load_json(None)
			
		if self.variables_ok:
			#print "\nVARIABLES FILE"
			#print "=============================="
			#self.listvars()
			self.read_inbox(False)
			#print "\nAFTER INBOX"
			#print "=============================="
			#print self.listvars(True)
			self.empty_trash(False)
			#print "\nAFTER TRASH"
			#print "=============================="
			#print self.listvars(True)
			self.add_volatile_info()
			self.write_file()
		else:
			print("[VariablesManager] Loading variables failed because: " + str(ret))

		
	#def __init__
	
	# DO NOT TOUCH THIS
	
	def startup(self,options):
		pass
		
	# DONE ============
	
	
	def log(self,txt):
		
		try:
			f=open(VariablesManager.LOG,"a")
			txt=str(txt)
			f.write(txt+"\n")
			f.close()
		except Exception as e:
			pass
		
	#def log
	
	def listvars(self,extra_info=False,custom_dic=None):
		ret=""
		
		try:
		
			if custom_dic==None:
				custom_dic=self.variables
			for variable in custom_dic:
				value=self.get_variable(variable)
				if value==None:
					continue
				ret+=variable+ "='" + str(value).encode("utf-8") + "';\n"
				if extra_info:
					ret+= "\tDescription: " + self.variables[variable][u"description"] + "\n"
					ret+="\tUsed by:\n"
					for depend in self.variables[variable][u"packages"]:
						ret+= "\t\t" + depend.encode("utf-8") + "\n"
			
			return ret.strip("\n")
		except Exception as e:
			return str(e)
					
	#def listvars
	
	def calculate_variable(self,value):
		pattern="_@START@_.*?_@END@_"
		variables=[]
		
		ret=re.findall(pattern,value)
		
		print "hola",ret
		
		for item in ret:
			tmp=item.replace("_@START@_","")
			tmp=tmp.replace("_@END@_","")
			variables.append(tmp)
		
		for var in variables:
			value=value.replace("_@START@_"+var+"_@END@_",self.get_variable(var))
			
		return value
		
		
		
	#def remove_calculated_chars
	
	def add_volatile_info(self):
		
		for item in self.variables:
		
			if not self.variables[item].has_key("volatile"):
				self.variables[item]["volatile"]=False
			
		
		
	#def add_volatile_info

	
	def showvars(self,var_list,extra_info=False):
		
		ret=""
		
		for var in var_list:
			ret+=var+"='"
			if self.variables.has_key(var):
				try:
					ret+=self.variables[var][u'value'].encode("utf-8")+"';\n"
				except Exception as e:
					#it's probably something old showvars couldn't have stored anyway
					ret+="';\n"
				if extra_info:
					ret+= "\tDescription: " + self.variables[var][u"description"] + "\n"
					ret+="\tUsed by:\n"
					for depend in self.variables[var][u"packages"]:
						ret+= "\t\t" + depend.encode("utf-8") + "\n"
			else:
				ret+="'\n"
						
		return ret.strip("\n")
					
		
		
	#def  showvars
	
	def get_variables(self):

		return self.variables
		
	#def get_variables
		
	
	def load_json(self, file=None):

		self.variables={}
		
		if file!=None:
		
			try:
				
				f=open(file,"r")
				data=json.load(f)
				f.close()
				self.variables=data
				
				#return [True,""]
				
			except Exception as e:
				print(str(e))
				#return [False,e.message]
				
		for file in os.listdir(VariablesManager.VARIABLES_DIR):
			try:
				sys.stdout.write("\t[VariablesManager] Loading " + file + " ... ")
				f=open(VariablesManager.VARIABLES_DIR+file)	
				data=json.load(f)
				f.close()
				self.variables[file]=data[file]
				print("OK")
			except Exception as e:
				print("FAILED ["+str(e)+"]")
				
		return [True,""]
		
	#def load_json
	
	def read_inbox(self, force_write=False):
		
		'''
			value
			function
			description
			packages
		'''
		
		if self.variables_ok:
		
			if os.path.exists(VariablesManager.INBOX):
				
				for file in os.listdir(VariablesManager.INBOX):
					file_path=VariablesManager.INBOX+file
					print "[VariablesManager] Adding " + file_path + " info..."
					try:
						f=open(file_path,"r")
						data=json.load(f)
						f.close()
						
						for item in data:
							if self.variables.has_key(item):
								for key in data[item].keys():
									if not self.variables[item].has_key(unicode(key)):
										self.variables[item][unicode(key)] = data[item][key]
								if data[item].has_key(unicode('function')):
									self.variables[item][unicode('function')] = data[item][u'function']
								for depend in data[item][u'packages']:
									if depend not in self.variables[item][u'packages']:
										self.variables[item][u'packages'].append(depend)
								#if self.variables[item][u'value']==None or self.variables[item][u'value']=="":
								#	self.variables[item][u'value']=data[item][u'values']
							else:
								self.variables[item]=data[item]

					
					except Exception as e:
						print e
						#return [False,e.message]
					os.remove(file_path)
				
				if force_write:
					try:	
						self.add_volatile_info()
						self.write_file()
					except Exception as e:
						print(e)
						
		
		return [True,""]
				
		
			
			
		'''
		
		if os.path.exists(VariablesManager.INBOX):
			
			for file in os.listdir(VariablesManager.INBOX):
				file_path=VariablesManager.INBOX+file
				
				try:
					execfile(file_path)
					os.remove(file_path)
				except Exception as e:
					self.log(file_path + ": " + str(e))
			
		'''
		
	#def read_inbox
	
	def empty_trash(self,force_write=False):
		
		
		if self.variables_ok:
		
			for file in os.listdir(VariablesManager.TRASH):
				file_path=VariablesManager.TRASH+file
				#print "[VariablesManager] Removing " + file_path + " info..."
				try:
					f=open(file_path,"r")
					data=json.load(f)
					f.close()
					
					for item in data:
						if self.variables.has_key(item):
							if data[item][u'packages'][0] in self.variables[item][u'packages']:
								count=0
								for depend in self.variables[item][u'packages']:
									if depend==data[item][u'packages'][0]:
										self.variables[item][u'packages'].pop(count)
										if len(self.variables[item][u'packages'])==0:
											self.variables.pop(item)
										break
									else:
										count+=1
							
					#os.remove(file_path)
					
					
				except Exception as e:
					print e
					pass
					#return [False,e.message]
				os.remove(file_path)
			
			if force_write:
				try:	
					self.write_file()
				except Exception as e:
					print(e)
				
		return [True,'']
			
		
	#def empty_trash
	
	def get_ip(self):
		
		for item in netifaces.interfaces():
			tmp=netifaces.ifaddresses(item)
			if tmp.has_key(netifaces.AF_INET):
				if tmp[netifaces.AF_INET][0].has_key("broadcast") and tmp[netifaces.AF_INET][0]["broadcast"]=="10.0.2.255":
					return tmp[netifaces.AF_INET][0]["addr"]
		return None
		
	#def get_ip

	def get_variable_list(self,variable_list,store=False,full_info=False):
		
		ret={}
		for item in variable_list:
			try:
				ret[item]=self.get_variable(item,store,full_info)
				#if ret[item]==None:
				#	ret[item]=""
			except Exception as e:
				print e

		return ret
		
	#def get_variable_list
	

	def get_variable(self,name,store=False,full_info=False):
	
		if name in self.variables and self.variables[name].has_key("function"):
			try:
				if not full_info:
					if (type(self.variables[name][u"value"])==type("") or  type(self.variables[name][u"value"])==type(u"")) and self.variables[name][u"value"].find("_@START@_")!=-1:
						#print "I have to ask for " + name + " which has value: " + self.variables[name][u'value']
						value=self.calculate_variable(self.variables[name][u"value"])
					else:
						value=self.variables[name][u"value"]
					#return str(value.encode("utf-8")
					if type(value)==type(u""):
						try:
							ret=value.encode("utf-8")
							return ret
						except:
							return value
					else:
						return value
				else:
					variable=self.variables[name].copy()
					variable["remote"]=False
					if variable[u"value"].find("_@START@_")!=-1:
						variable["original_value"]=variable[u"value"]
						variable[u"value"]=self.calculate_variable(self.variables[name][u"value"])
						variable["calculated"]=True
					return variable
			except:
				return None
		else:
			if self.variables.has_key("REMOTE_VARIABLES_SERVER") and self.variables["REMOTE_VARIABLES_SERVER"][u"value"]!="" and self.variables["REMOTE_VARIABLES_SERVER"][u"value"]!=None:

				server_ip=socket.gethostbyname(self.variables["REMOTE_VARIABLES_SERVER"][u"value"])
				if self.get_ip()!=server_ip:
					for count in range(0,3):
						try:

							server=xmlrpclib.ServerProxy("https://"+server_ip+":9779",allow_none=True)

							var=server.get_variable("","VariablesManager",name,store,True)

							if var==None:
								return None
							if var!="" and store:

								self.add_variable(name,var[u"value"],var[u"function"],var[u"description"],var[u"packages"],False)
								return self.get_variable(name,store,full_info)
							else:
								if full_info:
									var["remote"]=True
									return var
								else:
									return var["value"]
								
						except Exception as e:
							time.sleep(1)
					
					return None
				else:
					return None
			else:
				
				return None
			
	#def get_variable

	
	def set_variable(self,name,value,depends=[]):

		if name in self.variables:
			if type(value)==type(""):
				self.variables[name][u"value"]=unicode(value).encode("utf-8")
			else:
				self.variables[name][u"value"]=value

			if len(depends)>0:
				for depend in depends:
					self.variables[unicode(name).encode("utf-8")][u"packages"].append(depend)
					
			self.write_file()
			return [True,""]
		else:
			return [False,"Variable not found. Use add_variable"]
		
		
	#def set_variable
	
	def add_variable(self,name,value,function,description,depends,volatile=False):

		if name not in self.variables:
			dic={}
			if type(value)==type(""):
				dic[u"value"]=unicode(value).encode("utf-8")
			else:
				dic[u"value"]=value
			dic[u"function"]=function
			dic[u"description"]=unicode(description).encode("utf-8")
			if type(depends)==type(""):
				dic[u"packages"]=[unicode(depends).encode("utf-8")]
			elif type(depends)==type([]):
				dic[u"packages"]=depends
			else:
				dic[u"packages"]=[]
			dic["volatile"]=volatile
			self.variables[unicode(name)]=dic
			if not volatile:
				self.write_file()
			return [True,""]
		else:
			return [False,"Variable already exists. Use set_variable"]
		
	def write_file(self,fname=None):
		
		'''
		
		try:
			while os.path.exists(VariablesManager.LOCK_FILE):
				time.sleep(2)
			f=open(VariablesManager.LOCK_FILE,"w")
			f.close()
			tmp={}
			for item in self.variables:
				if self.variables[item].has_key("volatile") and self.variables[item]["volatile"]==False:
					tmp[item]=self.variables[item]

			if fname==None:
				f=open(VariablesManager.VARIABLES_FILE,"w")
			else:
				f=open(fname,"w")
				
			data=unicode(json.dumps(tmp,indent=4,encoding="utf-8",ensure_ascii=False)).encode("utf-8")
			f.write(data)
			f.close()
			os.remove(VariablesManager.LOCK_FILE)
			return True
			
		except Exception as e:
			os.remove(VariablesManager.LOCK_FILE)
			print(e)
			return False
			
		'''
		
		try:
			while os.path.exists(VariablesManager.LOCK_FILE):
				time.sleep(2)
				
			f=open(VariablesManager.LOCK_FILE,"w")
			f.close()
			tmp_vars={}
			for item in self.variables:
				if self.variables[item].has_key("volatile") and self.variables[item]["volatile"]==False:
					tmp_vars[item]=self.variables[item]
					
			for item in tmp_vars:
				tmp={}
				tmp[item]=tmp_vars[item]
				f=open(VariablesManager.VARIABLES_DIR+item,"w")
				data=unicode(json.dumps(tmp,indent=4,encoding="utf-8",ensure_ascii=False)).encode("utf-8")
				f.write(data)
				f.close()
				
			os.remove(VariablesManager.LOCK_FILE)
			return True
				
			
		except Exception as e:
			os.remove(VariablesManager.LOCK_FILE)
			print (e)
			return False
		
			
		
	#def write_file
	
	def init_variable(self,variable,args={},force=False,full_info=False):

		try:
			funct=self.variables[variable]["function"]
			mod_name=funct[:funct.rfind(".")]
			funct_name=funct[funct.rfind(".")+1:]
			funct_name=funct_name.replace("(","")
			funct_name=funct_name.replace(")","")
			mod=importlib.import_module(mod_name)
			ret=getattr(mod,funct_name)(args)
			ok,exc=self.set_variable(variable,ret)
			if ok:
				return (True,ret)
			else:
				return (False,ret)
		except Exception as e:
			return (False,e)
		
		
	#def init_variable
	
	
#class VariablesManager


if __name__=="__main__":
	
	vm=VariablesManager()
	
	print vm.listvars()
	print vm.init_variable("name_center")
	args={}
	args["iface"]="eth0"
	print vm.init_variable("SERVER_IP",args)
	print vm.write_file()
	#print vm.get_variable("VARIABLE2",full_info=True)
	#print vm.get_variable("VARIABLE3",full_info=True)
	#print vm.showvars(var_list)
	
	
		
		
		
	
	
	
