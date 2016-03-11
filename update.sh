#!/usr/bin/env bash
DEPLOYDIR=~/apps/testing_app

GIT_WORK_TREE="$DEPLOYDIR" git checkout -f

cd "$DEPLOYDIR"

forever stop index.js

npm install

forever start index.js

echo "All done ;)"