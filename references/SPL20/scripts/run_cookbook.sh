#!/bin/bash

cd ..
mkdir -p cookbook/out
python cookbook/run_all.py 2>&1 | tee cookbook/out/run_all_$(date +%Y%m%d_%H%M%S).md
