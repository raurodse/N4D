import os
import os.path
import threading
import shutil
import pyinotify
import pwd

class NTicketsManager:
	
	WATCH_DIR="/tmp/.n4d/"
	
	def __init__(self):
		
		if not os.path.exists(NTicketsManager.WATCH_DIR):
			os.mkdir(NTicketsManager.WATCH_DIR)
			
		self.tickets={}
		
	#def __init__
	
	def launch_watch_monitor_thread(self):
		
		t=threading.Thread(target=self.init_watch_monitor)
		t.daemon=True
		t.start()
		
	#def launch_watch_monitor_thread
	
	def init_watch_monitor(self):
		
		class ProcessOptions(pyinotify.ProcessEvent):
			
			def __init__(self,ntm):
				
				self.ntm=ntm
			
			def process_IN_CREATE(self,event):
				
				#print(os.path.join(event.path,event.name))
				self.ntm.check_n4d_ticket(os.path.join(event.path,event.name))
				
			#def process_IN_CREATE
			
		#class ProcessOptions
		
		wm=pyinotify.WatchManager()
		notifier=pyinotify.Notifier(wm,ProcessOptions(self))
		wm.add_watch(NTicketsManager.WATCH_DIR, pyinotify.EventsCodes.ALL_FLAGS["IN_CREATE"])
		
		while True:
			notifier.process_events()
			if notifier.check_events():
				notifier.read_events()
		
		
	#def init_watch_monitor
	
	def check_n4d_ticket(self,file):
		
		print("[NTicketsManager] Checking %s ..."%(file))
		
		try:
			user=pwd.getpwuid(os.stat(file).st_uid).pw_name
			f=open(file)
			lines=f.readlines()
			f.close()
			password=lines[0].strip("\n")
			
			print user,password
			
		except Exception as e:
			print(e)
		
	#def check_n4d_ticket
	
	
#class NTicketsManager


if __name__=="__main__":
	
	ntm=NTicketsManager()
	ntm.init_watch_monitor()