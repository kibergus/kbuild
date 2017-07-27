#!/bin/bash

DIR="$( cd "$(dirname "$0")" ; pwd -P )"

cp -r $DIR/template/* ./
sed -i "s|KBUILD_ROOT_PATH|`dirname $DIR`|" build.py
