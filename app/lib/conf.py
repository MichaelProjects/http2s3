import tomllib
import os
import json


def _load_conf():
    with open("conf.toml", "rb") as conf:
        return tomllib.load(conf)


def set_env():
    config_data = _load_conf()
    for key, value in config_data.items():
        if type(value) == list:
            os.environ[key] = json.dumps(value)
            continue
        for k, v in value.items():
            if not k in os.environ:
                os.environ[k] = str(v)