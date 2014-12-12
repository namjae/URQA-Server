# -*- coding: utf-8 -*-

from UrqaConfigLoader import UrqaConfigLoader

urqaConfig = UrqaConfigLoader("/data/etc/urqa.io/config.cfg")


def get_config(option):
    return urqaConfig.get_config(option)

"""


cfg.add_section('urqa')
cfg.set('urqa', 'so_pool_path', '/urqa/sopool/')
cfg.set('urqa', 'log_pool_path', '/urqa/logpool/')
cfg.set('urqa', 'sym_pool_path', '/urqa/sympool/')
cfg.set('urqa', 'dmp_pool_path', '/urqa/dmppool/')

with open(os.path.join(os.path.dirname(__file__),'config.cfg'), 'wb') as configfile:
    cfg.write(configfile);
"""



