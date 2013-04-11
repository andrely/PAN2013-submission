import logging
import os

logging.basicConfig(level=logging.INFO)

config = None

def read_config():
    parent, _ = os.path.split(os.path.dirname(__file__))
    config_fn = os.path.join(parent, 'config.prop')

    logging.info("Reading config from %s" % config_fn)

    items = []

    if os.path.exists(config_fn):
        with open(config_fn) as f:
            for line in f.readlines():
                if line.strip() != '':
                    key, val = line.split('=')
                    items.append((key.strip().lower(), val.strip()))
    else:
        raise ValueError("Could not read config file %s" % config_fn)

    logging.info("Read %d items" % len(items))

    return dict(items)

def get_config(key):
    global config

    if not config:
        config = read_config()

    if config.has_key(key):
        return config[key]
    else:
        raise ValueError("%s not found in config" % key)
