#!/bin/bash
P=`python -c 'import sys; print sys.version[:3]'`
gcc -shared -g -ggdb _lzss.c -I /usr/include/python$P -o _lzss.so -lpython$P
