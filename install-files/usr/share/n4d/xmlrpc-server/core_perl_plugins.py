#!/usr/bin/env python
from subprocess import Popen, PIPE
import json , os , sys , tempfile
class_module = sys.argv[1]
function_module = sys.argv[2]
pipe_in = tempfile.NamedTemporaryFile().name
fd = open(pipe_in,'w')
args = {'args':[2,1]}
json.dump(args,fd)
fd.close()
exec_result = Popen(["/usr/share/n4d/xmlrpc-server/core_perl_plugins.pl",class_module,function_module,pipe_in],stdout=PIPE,stderr=PIPE)
result_json_path = exec_result.communicate()[0]
if os.path.exists(result_json_path):
    fd = open(result_json_path,'r')
    raw_result = fd.readlines()
    result = json.loads(raw_result[0])
    print result['result']
    os.remove(result_json_path)
else:
    print "error"
