# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
import json , os , sys , tempfile
class %CLASSNAME%:
        
        def __run_function(self,class_module,function_module,*raw_args):
                pipe_in = tempfile.NamedTemporaryFile().name
                fd = open(pipe_in,'w')
                args_parsed = []
                for i in raw_args:
                        args_parsed.append(i)
                args = {'args':args_parsed}
                json.dump(args,fd)
                fd.close()
                exec_result = Popen(["/usr/share/n4d/xmlrpc-server/perl_support/core_perl_plugins.pl",class_module,function_module,pipe_in],stdout=PIPE,stderr=PIPE)
                result_json_path = exec_result.communicate()[0]
                if os.path.exists(result_json_path):
                        fd = open(result_json_path,'r')
                        raw_result = fd.readlines()
                        result = json.loads(raw_result[0])
                        os.remove(result_json_path)
                        return result['result']
                else:
                        return None
        