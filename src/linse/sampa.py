"""
Methods for handling SAMPA and XSAMPA.
"""
import pathlib
from linse.transform import SegmentGrouper


__all__ = ['SAMPA', "XSAMPA"]


SAMPA = SegmentGrouper.from_file(
        pathlib.Path(__file__).parent / "data" / "sampa.tsv")
for k, v in SAMPA.converter.items():
    v["IPA"] = eval('"""' + v["IPA"] + '"""')

XSAMPA = SegmentGrouper.from_file(pathlib.Path(__file__).parent / "data" /
                                  "xsampa.tsv")
