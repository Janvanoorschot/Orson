#!/usr/bin/env bash
# Builds the orson development environment

# get the root directory
CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
ROOTDIR="$(dirname "$CURDIR")"
export DOCKERDIR=$ROOTDIR/docker

# spec the current version
VERSION=1.0

cd $DOCKERDIR
docker build -f $DOCKERDIR/Dockerfile-rabbitmq -t orson/rabbitmq:$VERSION .

