from linse.transform import segment, convert, SegmentGrouper
from linse.models import BIPA
from pathlib import Path
import codecs
from linse.annotate import codepoints
import linse
import warnings


sampa2ipa = SegmentGrouper.from_file(
        Path(linse.__file__).parent / "data" / "sampa.tsv")
ipa2sampa = {eval('"""' + v["IPA"] + '"""'): {"sampa": k} for k, v in
             sampa2ipa.converter.items()}

out = []
problems = set()

visited = set()

for sound in BIPA.values():
    grouped = segment(sound, ipa2sampa)
    converted = convert(grouped, ipa2sampa, "sampa")
    
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
    for k, v in ipa2sampa.items():
        if v["sampa"] not in visited:
            f.write(v["sampa"] + '\t' + k + '\n')
    f.write(" \tNULL\n")

for p in problems:
    warnings.warn("« " + p + " » " + " ".join(codepoints(p)))


