#!/usr/bin/env bash

INTERNALPORT="8989"
EXTERNALPORT="5000"
DOCKERIMAGE="localhost/myflask"

podman machine start
podman run -v \
   /Users/tinabruce/Documents/Programming/CS50/final_project/myflask/code:/code \
   -p "$INTERNALPORT":"$EXTERNALPORT" "$DOCKERIMAGE" --restart always

