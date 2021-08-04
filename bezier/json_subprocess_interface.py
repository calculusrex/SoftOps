from subprocess import Popen, PIPE
import json

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)


def call_bezier(distribution, n, m, PS):

    params = {}
    params['distribution'] = distribution
    params['n'] = n
    params['m'] = m
    params['PS'] = PS

    json_params = bytes(json.dumps(params), 'utf8')

    proc = Popen(['/usr/bin/python3.6', '/home/feral/engineering/addon_workshop/softops/bezier/json_subprocess_interface__run.py'],
                 stdin=PIPE,
                 stdout=PIPE)

    out, err = proc.communicate(input=json_params)
    proc.terminate()

    
    data = json.loads(
        out.decode('utf8'))

    cooss = data['cooss']

    return cooss


