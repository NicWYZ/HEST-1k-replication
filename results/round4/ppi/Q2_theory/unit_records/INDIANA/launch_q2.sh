#!/bin/bash
cd /Users/nicolaszhang/.claude-science/orgs/c42040b3-6d87-451b-9b93-c94218d0c812/workspaces/29d26232-3024-422c-8c8b-0dd27509ba09
B=/Users/nicolaszhang/.claude-science/orgs/c42040b3-6d87-451b-9b93-c94218d0c812/workspaces/29d26232-3024-422c-8c8b-0dd27509ba09/hpc/scp-713a0994673a7eda/b1_predictions__INDIANA_KIDNEY__
for nl in 4 6 8 12 16; do echo "hoptimus0 ${B}hoptimus0.parquet $nl"; echo "uni_v2 ${B}uni_v2.parquet $nl"; echo "resnet50 ${B}resnet50.parquet $nl"; echo "permuted ${B}resnet50.parquet $nl"; done | xargs -P 3 -L 1 ./run_q2.sh
