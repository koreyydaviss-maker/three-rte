#!/usr/bin/env python3
"""Build copy-trade-desk.html from template.html + data.json + ../paper/status.json."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(D, "template.html")).read()
data = json.load(open(os.path.join(D, "data.json")))
paper = json.load(open(os.path.join(D, "..", "paper", "status.json")))
paper.pop("trades_today", None)
out = t.replace("__DATA__", json.dumps(data), 1).replace("__PAPER__", json.dumps(paper), 1)
open(os.path.join(D, "copy-trade-desk.html"), "w").write(out)
print("built copy-trade-desk.html")
