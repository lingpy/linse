"""
Utility functions for linse.
"""
from pathlib import Path
import zipfile
import json

__all__ = ['data_path', 'get_CLTS', 'get_NORMALIZE']


def data_path(*comps):
    return Path(__file__).parent.joinpath('data', *comps)


def get_CLTS():
    with zipfile.ZipFile(data_path('clts.zip').as_posix(), 'r') as zf:
        clts = json.loads(zf.read('clts.json'))
    return clts


def get_NORMALIZE():
    with data_path('normalize.tsv').open('r') as f:
        data = dict([line.strip().split('\t') for line in f.readlines()])
    return data
