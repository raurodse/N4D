# -*- coding: utf-8 -*-
import ConfigParser
import os


class PluginInfo:
	
	def __init__(self):
		
		self.path=None
		self.type=None
		#PYTHON TYPE
		self.class_name=None
		self.function={}
		#BASH TYPE
		self.bin_name=None
		self.args=None
		#REMOTE TYPE
		self.remoteip=None
		self.order=None
		self.functionremote=[]
		self.standalone=True
		self.user_secured_functions=[]
		self.ip_secured_functions=[]
		self.secure_order=[(self.user_secured_functions,"user"),(self.ip_secured_functions,"client_address")]
		
	#def init
	
#class PluginInfo

class ConfigurationManager:
	
	def __init__(self,base_dir):
		
		base_dir+="/"
		self.plugins = []
		file_list=os.listdir(base_dir)
		file_list.sort()
		
		self.python_path="/usr/share/n4d/python-plugins/"
		self.bash_path="/usr/share/n4d/binary-plugins/"
		self.perl_path="/usr/share/n4d/perl-plugins/"		
		
		for file in file_list:
			#print file
			plugin=self.load_plugin(base_dir+file)
			if plugin!=None:
				self.plugins.append(plugin)
		
		#self.print_plugins()
		#print ""
		
		
	#def init
	
	def load_plugin(self,file):

		plugin=PluginInfo()
		config = ConfigParser.ConfigParser()
		config.optionxform=str
		config.read(file)
			
		
		if config.has_section("SETUP") and config.has_option("SETUP","type"):
		
			ok=True
			
				
			try:
			
				if config.get("SETUP","type")=="python":
					plugin.type="python"
					if config.has_option("SETUP","path") and config.has_option("SETUP","class"):
						plugin.path=self.python_path + config.get("SETUP","path")
						plugin.class_name=config.get("SETUP","class")
						if config.has_section("METHODS"):
							options=config.options("METHODS")
							for option in options:
								tmp=config.get("METHODS",option)
								tmp=tmp.replace(' ','')
								perm_list=tmp.split(",")
								
								if option.find("(")==0:
									first=option.find("(")+1
									last=option.find(")")
									secure_options=option[first:last].split(",")
									option=option[last+1:]
										
									if "us" in secure_options:
										plugin.user_secured_functions.append(option)
									if "ip" in secure_options:
										plugin.ip_secured_functions.append(option)
											
									
										
								plugin.function[option]=perm_list
						else:
							ok=False
					else:
						ok=False
						
				if config.get("SETUP","type")=="binary":
					plugin.type="binary"
					if config.has_option("SETUP","path") and config.has_option("SETUP","class"):
						plugin.path=self.bash_path + config.get("SETUP","path")
						plugin.bin_name=config.get("SETUP","path")
						plugin.class_name=config.get("SETUP","class")
							
														
						if config.has_section("METHODS"):
							plugin.standalone=False
							options=config.options("METHODS")
							for option in options:
								tmp=config.get("METHODS",option)
								tmp=tmp.replace(' ','')
								perm_list=tmp.split(",")
								plugin.function[option]=perm_list
						else:
							if config.has_option("SETUP","perms"):
								tmp=config.get("SETUP","perms")
								tmp=tmp.replace(' ','')
								perm_list=tmp.split(",")
								plugin.standalone=True
								plugin.function[config.get("SETUP","path")]=perm_list
							else:
								ok=False
							
					else:
						
						ok=False
					
				if config.get("SETUP","type")=="remote":
					plugin.type="remote"
					if config.has_option("SETUP","remoteip") and config.has_option("SETUP","order"):
						plugin.remoteip=config.get("SETUP","remoteip")
						plugin.order=config.get("SETUP","order")
						plugin.functionremote=config.options("METHODS")
					else:
						ok=False
					
				if config.get("SETUP","type")=="perl":
					plugin.type="perl"
					if config.has_option("SETUP","path") and config.has_option("SETUP","class"):
						plugin.path=self.perl_path + config.get("SETUP","path")
						plugin.class_name=config.get("SETUP","class")
						if config.has_section("METHODS"):
							options=config.options("METHODS")
							for option in options:
								tmp=config.get("METHODS",option)
								tmp=tmp.replace(' ','')
								perm_list=tmp.split(",")
								plugin.function[option]=perm_list
						else:
							ok=False
					else:
						ok=False

				if ok:
					return plugin
				else:
					return None

						
			except Exception as e:
				print e
				return None
		
	#def load_plugin

	def print_plugins(self):
		 
		print "[==========]"
		
		for plugin in self.plugins:
			print "["+plugin.class_name + "]"
			print plugin.path
			print plugin.function
			
		print "[==========]"
		
	#def print plugins

	
#

if __name__=="__main__":
	
	cm=ConfigurationManager("/etc/lliurex-navel")


