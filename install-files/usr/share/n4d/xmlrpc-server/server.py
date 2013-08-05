#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, 'C.UTF-8')

"""
 *******************************************************************************
 * 
 * $Id: SecureDocXMLRPCServer.py 4 2008-06-04 18:44:13Z yingera $
 * $URL: https://xxxxxx/repos/utils/trunk/tools/SVNRPCServer.py $
 *
 * $Date: 2008-06-04 13:44:13 -0500 (Wed, 04 Jun 2008) $
 * $Author: yingera $
 *
 * Authors: Laszlo Nagy, Andrew Yinger
 *
 * Description: Threaded, Documenting SecureDocXMLRPCServer.py - over HTTPS.
 *
 *  requires pyOpenSSL: http://sourceforge.net/project/showfiles.php?group_id=31249
 *   ...and open SSL certs installed.
 *
 * Based on this article: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81549
 *
 *******************************************************************************
"""

import SocketServer
import BaseHTTPServer
import SimpleHTTPServer
import SimpleXMLRPCServer
import imp


import fcntl
import time
import random
import base64
import socket, os
from OpenSSL import SSL
from threading import Event, currentThread, Thread, Condition
from thread import start_new_thread as start
from DocXMLRPCServer import DocXMLRPCServer, DocXMLRPCRequestHandler

import xmlrpclib
import threading
threading._DummyThread._Thread__stop = lambda x: 42

#locale.resetlocale()

# static stuff

'''
DEFAULTKEYFILE='/etc/lliurex-secrets/pki/n4d/n4d.key'	# Replace with your PEM formatted key file
DEFAULTCERTFILE='/etc/lliurex-secrets/certs/n4d/n4d'  # Replace with your PEM formatted certificate file
'''

DEFAULTKEYFILE='/etc/n4d/cert/n4dkey.pem'	# Replace with your PEM formatted key file
DEFAULTCERTFILE='/etc/n4d/cert/n4dcert.pem'  # Replace with your PEM formatted certificate file

TRIGGER_BLOCK=False


class SecureDocXMLRpcRequestHandler(DocXMLRPCRequestHandler):
	"""Secure Doc XML-RPC request handler class.
	It it very similar to DocXMLRPCRequestHandler but it uses HTTPS for transporting XML data.
	"""
	def setup(self):
		self.connection = self.request
		self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
		self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)

	def address_string(self):
		"getting 'FQDN' from host seems to stall on some ip addresses, so... just (quickly!) return raw host address"
		host, port = self.client_address
		#return socket.getfqdn(host)
		return host

	def do_POST(self):
		"""Handles the HTTPS POST request.
		It was copied out from SimpleXMLRPCServer.py and modified to shutdown the socket cleanly.
		"""
		try:
			# get arguments
			data = self.rfile.read(int(self.headers["content-length"]))
			# In previous versions of SimpleXMLRPCServer, _dispatch
			# could be overridden in this class, instead of in
			# SimpleXMLRPCDispatcher. To maintain backwards compatibility,
			# check to see if a subclass implements _dispatch and dispatch
			# using that method if present.
			addr,num=self.client_address
			response = self.server._marshaled_dispatch(data, getattr(self, '_dispatch', None),client_address=addr)
			
			
		except: # This should only happen if the module is buggy
			# internal error, report as HTTP server error
			self.send_response(500)
			self.end_headers()
		else:
			# got a valid XML RPC response
			self.send_response(200)
			self.send_header("Content-type", "text/xml")
			self.send_header("Content-length", str(len(response)))
			self.end_headers()
			self.wfile.write(response)

			# shut down the connection
			self.wfile.flush()
			'''
			global TRIGGER_BLOCK
			while(TRIGGER_BLOCK):
				print "waiting for trigger_block to be unlocked..."
				time.sleep(int(5*random.random()))
			TRIGGER_BLOCK=True
			print "done with response. Sleeping..."
			time.sleep(5)
			print "done sleeping."
			TRIGGER_BLOCK=False
			'''
			self.connection.shutdown() # Modified here!

	def do_GET(self):
		"""Handles the HTTP GET request.

		Interpret all HTTP GET requests as requests for server
		documentation.
		"""
		# Check that the path is legal

		if not self.is_rpc_path_valid():
			self.report_404()
			return
		
		
		#print self.path
		#response = self.server.generate_html_documentation()
		
		header="<html><body>"
		foot="</body></html>"
		
		response=header
		
		for plugin in l.cm.plugins:
			response+="<b>["+plugin.type+":"+plugin.class_name+"]</b><br>"
			for method in plugin.function:
				try:
					#server.register_function(getattr(l.objects[plugin.class_name],method))
					args=getattr(l.objects[plugin.class_name],method).func_code.co_varnames[:getattr(l.objects[plugin.class_name],method).func_code.co_argcount]
					response+="<pre>      " + method+str(args).replace("'self',","")+" , " + str(getattr(l.objects[plugin.class_name],method).__doc__) + "</pre>"
				except:
					pass
		
		response+=foot
		

		
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.send_header("Content-length", str(len(response)))
		self.end_headers()
		self.wfile.write(response)

		# shut down the connection
		self.wfile.flush()
		self.connection.shutdown() # Modified here!

	def report_404 (self):
		# Report a 404 error
		self.send_response(404)
		response = 'No such page'
		self.send_header("Content-type", "text/plain")
		self.send_header("Content-length", str(len(response)))
		self.end_headers()
		self.wfile.write(response)
		# shut down the connection
		self.wfile.flush()
		self.connection.shutdown() # Modified here!



class CustomThreadingMixIn:
	"""Mix-in class to handle each request in a new thread."""
	# Decides how threads will act upon termination of the main process
	daemon_threads = True

	def process_request_thread(self, request, client_address):
		"""Same as in BaseServer but as a thread.
		In addition, exception handling is done here.
		"""
		try:
			self.finish_request(request, client_address)
			self.close_request(request)
		except (socket.error, SSL.SysCallError), why:
			print 'socket.error finishing request from "%s"; Error: %s' % (client_address, str(why))
			self.close_request(request)
		except:
			self.handle_error(request, client_address)
			self.close_request(request)

	def process_request(self, request, client_address):
		"""Start a new thread to process the request."""
		t = Thread(target = self.process_request_thread, args = (request, client_address))
		if self.daemon_threads:
			t.setDaemon(1)
		t.start()



class SecureDocXMLRPCServer(CustomThreadingMixIn, DocXMLRPCServer):
	def __init__(self, registerInstance, server_address, keyFile=DEFAULTKEYFILE, certFile=DEFAULTCERTFILE, logRequests=True):
		"""Secure Documenting XML-RPC server.
		It it very similar to DocXMLRPCServer but it uses HTTPS for transporting XML data.
		"""
		DocXMLRPCServer.__init__(self, server_address, SecureDocXMLRpcRequestHandler, logRequests,True)
		self.logRequests = logRequests

		# stuff for doc server
		try: self.set_server_title(registerInstance.title)
		except AttributeError: self.set_server_title('N4D Documentation page')
		try: self.set_server_name(registerInstance.name)
		except AttributeError: self.set_server_name('N4D')
		#for plugin in registerInstace
		if registerInstance.__doc__: self.set_server_documentation(registerInstance.__doc__)
		else: self.set_server_documentation('default documentation')
		
		
		#self.register_introspection_functions()
		
		# init stuff, handle different versions:
		try:
			SimpleXMLRPCServer.SimpleXMLRPCDispatcher.__init__(self,allow_none=True)
		except TypeError:
			# An exception is raised in Python 2.5 as the prototype of the __init__
			# method has changed and now has 3 arguments (self, allow_none, encoding)
			SimpleXMLRPCServer.SimpleXMLRPCDispatcher.__init__(self, allow_none=True, encoding=None)
		SocketServer.BaseServer.__init__(self, server_address, SecureDocXMLRpcRequestHandler)
		self.register_instance(registerInstance) # for some reason, have to register instance down here!

		# SSL socket stuff
		ctx = SSL.Context(SSL.SSLv23_METHOD)
		ctx.use_privatekey_file(keyFile)
		ctx.use_certificate_file(certFile)
		self.socket = SSL.Connection(ctx, socket.socket(self.address_family, self.socket_type))
		
		old = fcntl.fcntl(self.socket.fileno(), fcntl.F_GETFD)	
		fcntl.fcntl(self.socket.fileno(), fcntl.F_SETFD, old | fcntl.FD_CLOEXEC)	
		
		self.server_bind()
		self.server_activate()

		# requests count and condition, to allow for keyboard quit via CTL-C
		self.requests = 0
		self.rCondition = Condition()


	def startup(self):
		'run until quit signaled from keyboard...'
		print '[SERVER] Starting; Press CTRL-C to quit ...'
		while True:
			try:
				self.rCondition.acquire()
				start(self.handle_request, ()) # we do this async, because handle_request blocks!
				while not self.requests:
					self.rCondition.wait(timeout=3.0)
				if self.requests: self.requests -= 1
				self.rCondition.release()
			except KeyboardInterrupt:
				print "[SERVER] Exiting..."
				return

	def get_request(self):
		request, client_address = self.socket.accept()
		self.rCondition.acquire()
		self.requests += 1
		self.rCondition.notifyAll()
		self.rCondition.release()
		return (request, client_address)

	def listMethods(self):
		'return list of method names (strings)'
		methodNames = self.funcs.keys()
		methodNames.sort()
		return methodNames

	def methodHelp(self, methodName):
		'method help'
		if methodName in self.funcs:
			return self.funcs[methodName].__doc__
		else:
			raise Exception('method "%s" is not supported' % methodName)


	def _marshaled_dispatch(self, data, dispatch_method = None, path = None, client_address=None):
		self.allow_none=True
		try:
			params, method = xmlrpclib.loads(data)
			params=(client_address,)+params

			if dispatch_method is not None:
				response = dispatch_method(method, params)
			else:

				response = self._dispatch(method, params)

			response = (response,)
			response = xmlrpclib.dumps(response, methodresponse=1,allow_none=self.allow_none, encoding=self.encoding)

		except Fault, fault:
			response = xmlrpclib.dumps(fault, allow_none=self.allow_none,encoding=self.encoding)
		except:

			exc_type, exc_value, exc_tb = sys.exc_info()
			response = xmlrpclib.dumps(xmlrpclib.Fault(1, "%s:%s" % (exc_type, exc_value)),encoding=self.encoding, allow_none=self.allow_none,)

		return response



if __name__ == '__main__':
	
	obj=imp.load_source("core","/usr/share/n4d/xmlrpc-server/core.py")
	l=obj.Core()
	server_address = ('', 9779) # (address, port)
	server = SecureDocXMLRPCServer(l, server_address, DEFAULTKEYFILE, DEFAULTCERTFILE)	
	#server.register_introspection_functions()
	'''
	for plugin in l.cm.plugins:
		for method in plugin.function:
			server.register_function(getattr(l.objects[plugin.class_name],method))
	'''
	
			
	sa = server.socket.getsockname()
	print "[SERVER] HTTPS on", sa[0], "port", sa[1]
	server.startup()


