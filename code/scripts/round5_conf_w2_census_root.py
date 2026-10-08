#!/usr/bin/env python
"""Round 5 W2 part 2: stamp the part2 output root and place the findings and merged check tables there."""
import os, shutil, sys
import round5_conf_io as IO
root = sys.argv[1]
IO.stamp(root, "round5-conformal W2 part2", "output root of W2 part 2: input, released runs, acceptance, wrapper validation")
for f in sys.argv[2:]:
    shutil.copy(f, os.path.join(root, os.path.basename(f)))
IO.write_provenance(root, "W2p2_root", os.path.abspath(__file__), {"files": sys.argv[2:]})
