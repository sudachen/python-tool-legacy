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

from binutils.details import mmap_file
from binutils.ctypes import cast, POINTER, c_ushort, c_int, c_uint
from binutils.treat.spy import FileSpy

def detect_file_type_and_open(file_name):
    mf = mmap_file(file_name)
    if cast( mf, POINTER(c_ushort) )[0] == 0x05a4d:
        if cast( mf+cast(mf+0x3c, POINTER(c_int))[0], POINTER(c_int))[0]  == 0x00004550:
            from binutils.treat.pefile import Bfile
            return FileSpy(Bfile(mf))

    raise Exception('unkown file format')
