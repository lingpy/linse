from linse.sampa import SAMPA
from linse.transform import segment, convert
from linse.models import BIPA
from pathlib import Path
import codecs
from linse.annotate import codepoints
import linse
import warnings


out = []
problems = set()
sampa = {k: {"sampa": v} for v, k in SAMPA.items()}

visited = set()

for sound in BIPA.values():
    grouped = segment(sound, sampa)
    converted = convert(grouped, sampa, "sampa")
    
    errors = False
    for seg in converted:
        if "«" in seg:
            problems.add(seg[1:-1])
            errors = True
    if not errors:
        out += [("".join(converted), "".join(grouped))]
        visited.add(out[-1][0])

with codecs.open(
        Path(linse.__file__).parent / 'data' / 'xsampa.tsv',
        "w",
        "utf-8") as f:
    f.write("Sequence\tBIPA\n")
    for a, b in out:
        f.write(a + '\t' + b + '\n')
    for k, v in SAMPA.items():
        if k not in visited:
            f.write(k + '\t' + v + '\n')

for p in problems:
    warnings.warn("« " + p + " » " + " ".join(codepoints(p)))


