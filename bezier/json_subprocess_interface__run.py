
import json

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)

from bezier.cooss import bezier_cooss__uniform__sym, bezier_cooss__adaptive__sym

params = json.load(sys.stdin)

distributions_to_functions = {
    'adaptive': bezier_cooss__adaptive__sym,
    'uniform': bezier_cooss__uniform__sym
}

bezier_cooss_f = distributions_to_functions[params['distribution']]

cooss = bezier_cooss_f(
    params['n'],
    params['m'],
    *params['PS']
)

cooss__tuple = list(map(lambda coos: list(map(lambda coo: tuple(coo), coos)),
                        cooss))

json.dump({'cooss': cooss__tuple}, sys.stdout)

