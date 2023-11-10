#!/bin/bash

python src/version.py

if [ "$ENV" != "production" ]
then
    watchmedo auto-restart --recursive --pattern="*.py" --directory="/app/" python src/process.py
else
    python src/process.py
fi
