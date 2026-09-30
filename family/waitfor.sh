#!/bin/bash
# wait until process $1 exits (poll), max $2 seconds
for i in $(seq 1 $2); do kill -0 $1 2>/dev/null || exit 0; sleep 1; done
