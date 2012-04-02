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
		
		
	#def init
	
#class PluginInfo

class ConfigurationManager:
	
	def __init__(self,base_dir):
		
		
		self.plugins = []
		file_list=os.listdir(base_dir)
		file_list.sort()
		
		python_path="/usr/share/n4d/python-plugins/"
		bash_path="/usr/share/n4d/binary-plugins/"
		
		for file in file_list:
			#print file
			plugin=PluginInfo()
			config = ConfigParser.ConfigParser()
			config.optionxform=str
			config.read(base_dir + "/" + file)
			
			
			if config.has_section("SETUP") and config.has_option("SETUP","type"):
			
				ok=True
			
				
				try:
				
					if config.get("SETUP","type")=="python":
						plugin.type="python"
						if config.has_option("SETUP","path") and config.has_option("SETUP","class"):
							plugin.path=python_path + config.get("SETUP","path")
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
							
					if config.get("SETUP","type")=="binary":
						plugin.type="binary"
						if config.has_option("SETUP","path") and config.has_option("SETUP","class") and config.has_option("SETUP","perms"):
							plugin.path=bash_path + config.get("SETUP","path")
							plugin.bin_name=config.get("SETUP","path")
							plugin.class_name=config.get("SETUP","class")
							tmp=config.get("SETUP","perms")
							tmp=tmp.replace(' ','')
							perm_list=tmp.split(",")
							plugin.function[config.get("SETUP","path")]=perm_list
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
					
					
					if ok:
						self.plugins.append(plugin)
						
				except:
					pass
		
		
		
		#self.print_plugins()
		#print ""

	#def init

	def print_plugins(self):
		print("[==========]")
		for plugin in self.plugins:
			print("["+plugin.class_name + "]")
			print(plugin.path)
			print(plugin.function)
		print("[==========]")
	#def print plugins