#!/usr/bin/python2.7

from distutils.core import setup
import sys
import os
setup(
      name='n4d',
      version='0.1',
      description='Network for Dummies',
      author=['Hector Garcia Huerta','Raul Rodrigo Segura'],
      author_email=["hectorgh@gmail.com","raurodse@gmail.com"],
      packages=["n4d","n4d.auth","n4d.config"],
      scripts = ['xmlrpc-server/n4d-server'],
      data_files =  [('usr/share/n4d/xmlrpc-server/',['xmlrpc-server/class_skel.py']),
            ('usr/share/n4d/xmlrpc-server/',['xmlrpc-server/core.py'])]
     )

if sys.argv[1] == 'install':
      '''
      Create auxiliar directories
      '''
      os.mkdir('/usr/share/n4d/xmlrpc-server/custom-variables')