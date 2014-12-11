# -*- coding: utf-8 -*-
import os
import ConfigParser

cfg = ConfigParser.RawConfigParser()
defaultPath = "/data/etc/urqa.io/config.cfg"
readPath = os.path.isfile(defaultPath) and defaultPath or os.path.join(os.path.dirname(__file__),'config.cfg')

cfg.read(readPath)

def get_config(option):
    return cfg.get('urqa',option)

"""


cfg.add_section('urqa')
cfg.set('urqa', 'so_pool_path', '/urqa/sopool/')
cfg.set('urqa', 'log_pool_path', '/urqa/logpool/')
cfg.set('urqa', 'sym_pool_path', '/urqa/sympool/')
cfg.set('urqa', 'dmp_pool_path', '/urqa/dmppool/')

with open(os.path.join(os.path.dirname(__file__),'config.cfg'), 'wb') as configfile:
    cfg.write(configfile);
"""



