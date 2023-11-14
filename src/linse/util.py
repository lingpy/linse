"""
Utility functions for linse.
"""
import csv
import json
import pathlib
import zipfile
import collections

__all__ = ['data_path', 'get_CLTS', 'get_NORMALIZE']


def data_path(*comps):
    return pathlib.Path(__file__).parent.joinpath('data', *comps)


def get_CLTS():
    with zipfile.ZipFile(data_path('clts.zip').as_posix(), 'r') as zf:
        clts = json.loads(zf.read('clts.json'))
    return clts


def get_NORMALIZE():
    with data_path('normalize.tsv').open('r') as f:
        data = dict([line.strip().split('\t') for line in f.readlines()])
    return data


def iter_dicts_from_csv(filename, delimiter=','):
    header = None
    with pathlib.Path(filename).open(newline='') as csvfile:
        for i, row in enumerate(csv.reader(csvfile, delimiter=delimiter)):
            if i == 0:
                header = row
            else:
                yield collections.OrderedDict(zip(header, row))


def write_csv(filename, rows, delimiter=','):
    with pathlib.Path(filename).open('w', newline='') as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerows(rows)
