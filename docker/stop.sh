#!/usr/bin/env bash

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
export DIR="$(dirname "$CURDIR")"
export DOCKERDIR=$DIR/docker
VERSION=1.0

cd $DOCKERDIR
docker-compose -f $DOCKERDIR/orson-dev.yml down
