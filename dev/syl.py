import sqlite3
import linse
from linse.annotate import soundclass
from collections import defaultdict
from linse.typedsequence import Morpheme, Word
from re import findall


def chunk(segments, vowel="V"):
    out = [Morpheme("")]
    vowels = len([x for x in segments if x in vowel])
    for i, c in enumerate(segments):
        if c in vowel:
            vowels -= 1
            out[-1] += c
            if i != len(segments) - 1 and vowels:
                out += [Morpheme("")]
        else:
            out[-1] += c
    return out


def get_v(elm, vowel="V"):
    out = []
    for s in elm:
        if s not in vowel:
            out += [s]
        if s in vowel:
            return out
    return out


def sylbify(word, scl="dolgo", vowel="V"):
    cv = soundclass(word, scl)
    chunks = chunk(cv, vowel)
    if len(chunks) == 1:
        return []
    
    out = []
    for elm in chunks[1:]:
        cvals = get_v(elm, vowel)
        out += [" ".join(cvals)]
    return out



db = sqlite3.connect("lexibank.sqlite3")
cursor = db.cursor()
cursor.execute("select cldf_segments from formtable order by cldf_segments;")

uni = set()
counts = defaultdict(list)
chunker = defaultdict(list)
for row in cursor.fetchall():
    segments = row[0].split(" + ")
    for sform in segments:
        if sform in uni:
            pass
        else:
            uni.add(sform)
            chunks = sylbify(Word(sform), scl="sca", vowel="AEIOUY")
            for c in chunks:
                chunker[c] += [sform]
            cv = soundclass(sform.split(), "cv")
            counts[tuple(cv)] += [sform]

with open('syllables.tsv', "w") as f:
    f.write("Chunk\tFrequency\tWords\n")
    for k, v in sorted(chunker.items(), key=lambda x: (len(x[0]), x[0])):
        if not [x for x in k if x in "123456"] and len(k.split()) > 2:
            f.write("{0}\t{1}\t{2}\n".format(
                k, len(v), " // ".join(v)))
