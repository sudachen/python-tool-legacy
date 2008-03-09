#!/usr/bin/python
# -*- coding: cp1251 -*-
"""
(c)2008 Alexey Sudachen, alexey@sudachen.name
http://www.ethical-hacker.info/

TREAT - The Reverse Engineering & Analizing Tool.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

version = "1.0"

import sys, os, os.path

if __name__ == '__main__':
    import _pycrt
    if not _pycrt.compiled:
        sys.path = [os.path.dirname(os.path.abspath(sys.argv[0]))+'/lib'] + sys.path

from binutils.treat import options
from binutils.treat import detector

def main(prog,args):
    try:
        flags, args = options.play_with_command_line(args)
        if len(args) < 1 or flags.get('print-usage'):
            print_hello()
            print_usage()
            return 0
        file_name = os.path.normpath(os.path.abspath(args[0]))
        if not os.path.exists(file_name):
            raise Exception('file % is not exists' % file_name)
        bfile = detector.detect_file_type_and_open(file_name)
        try:
            bfile.do_command(flags,args[1:])
        finally:
            if bfile:
                bfile.close()
    except:
        import traceback
        traceback.print_exc()
        #print str(sys.exc_info()[1])
        return -1

if __name__ == '__main__':
    sys.exit(main(sys.argv[0],sys.argv[1:]))
