# -*- coding: utf-8 -*-
import subprocess

class %CLASSNAME%:
	
	def %METHOD%(self,*params):
		
		popen_list=[]
		popen_list.append("%BINARY%")
		
		for param in params:
			popen_list.append(str(param))
		
		output = subprocess.Popen(popen_list, stdout=subprocess.PIPE).communicate()[0]
		
		return output
