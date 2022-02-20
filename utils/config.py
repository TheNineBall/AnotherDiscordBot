import yaml
from dotdict import dotdict


def read_config():
    return dotdict(yaml.safe_load(open('config.yaml', 'r')))


config = read_config()