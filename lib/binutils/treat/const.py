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

DEFAULT_LINES = 30
F_ABSOLUTE_ADDRESS      = 0
F_RELATED_TO_BASE       = 1
F_RELATED_TO_POINT      = 2
F_RELATED_TO_SECTION    = 3
F_RELATED_TO_FILE       = 4
F_NONE_ADDRESS          = 5
CMD_NONE                = 0
CMD_DISASSEMBLE         = 1
CMD_IMPORTS             = 2
CMD_IMPORTS_FUNCS       = 3
CMD_EXPORTS             = 4
CMD_QUICK_HEADERS       = 5
CMD_FULL_HEADERS        = 6
CMD_SHOW_SECTIONS       = 7
CMD_SHOW_DIRECTORY      = 8
CMD_DECSRIBE            = 20
CMD_DECSRIBE_BYTE       = 21
CMD_DECSRIBE_WORD       = 22
CMD_DECSRIBE_DWORD      = 23
CMD_DECSRIBE_QWORD      = 24
CMD_DECSRIBE_STRING     = 25
CMD_DECSRIBE_UNICODE    = 26
