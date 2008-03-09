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

import sys, os, os.path, getopt, binascii, re
from binutils.treat.const import *

def safe_int(i,d):
    try:
        return int(i)
    except:
        return d

def try_treat_as_int(val,radix=10,default=0,msg=None):
    try:
        if val != None:
            if str(val).startswith('0x'):
                val = str(val)[2:]
                radix = 16
            return int(val,radix)
        else:
            return default
    except:
        if not msg:
            raise Exception("could not convert '%s' to integer"%str(val))
        else:
            raise Exception(msg)

def play_with_command_line(argv):
    flags = {
        'syntax':'att',
        'max-lines':DEFAULT_LINES,
        'skip-lines':0,
        'disasm-level':0,
        'disasm-addr-format':F_ABSOLUTE_ADDRESS,
        'command':CMD_QUICK_HEADERS,
        }

    opts,args = getopt.getopt(argv,'L:F:O:H:X:D:h?V',['intel','att'])

    if len(args):
        g = re.match('([^!]+)(?:!([^+-]+)?([+-]\\S+)?)?',args[0])

        if g:
            flags['disasm-offs'] = try_treat_as_int(g.group(3),16,0)
            args[0] = g.group(1)
            flags['disasm-entry']  = g.group(2)

    for i,j in opts:
        if i == '--intel': flags['syntax'] = 'intel'
        if i == '--att': flags['syntax'] = 'att'

        if i in ('-?','-h'):
            flags['show-help'] = True

        if i == '-V':
            flags['show-version'] = True

        if i == '-L':
            if j.startswith('r'):
                flags['disasm-level'] = 0
                j = j[1:]
            elif j.startswith('x'):
                flags['disasm-level'] = 1
                j = j[1:]
            else:
                flags['disasm-level'] = 2
            flags['max-lines'] = safe_int(j,DEFAULT_LINES)
            flags['command'] = CMD_DISASSEMBLE

        if i == '-F':
            for j in j:
                if j in ('a','A'):
                    flags['disasm-addr-format'] = F_ABSOLUTE_ADDRESS
                    if j == 'A': flags['disasm-no-addr'] = True
                elif j in ('b','B'):
                    flags['disasm-addr-format'] = F_RELATED_TO_BASE
                    if j == 'B': flags['disasm-no-addr'] = True
                elif j in ('p','P'):
                    flags['disasm-addr-format'] = F_RELATED_TO_POINT
                    if j == 'P': flags['disasm-no-addr'] = True
                elif j in ('s','S'):
                    flags['disasm-addr-format'] = F_RELATED_TO_SECTION
                    if j == 'S': flags['disasm-no-addr'] = True
                elif j in ('f','F'):
                    flags['disasm-addr-format'] = F_RELATED_TO_FILE
                    if j == 'F': flags['disasm-no-addr'] = True
                elif j == 'N':
                    flags['disasm-no-addr'] = True
                elif j == 'H':
                    flags['disasm-no-hex'] = True
                elif j == 'M':
                    flags['disasm-no-mark'] = True
                elif j == 'L':
                    flags['disasm-no-label'] = True

        if i == '-H':
            if j == 'i':
                flags['command'] = CMD_IMPORTS
            if j == 'I':
                flags['command'] = CMD_IMPORTS_FUNCS
            if j == 'e':
                flags['command'] = CMD_EXPORTS
            if j == 'q':
                flags['command'] = CMD_QUICK_HEADERS
            if j == 'x':
                flags['command'] = CMD_FULL_HEADERS

        if i == '-X':
            if j == 'f':
                flags['command'] = CMD_DESCRIBE
            if len(j):
                if j[0] == 'b':
                    flags['command'] = CMD_DESCRIBE_BYTES
                    j = j[1:]
                elif j[0] == 'w':
                    flags['command'] = CMD_DESCRIBE_WORDS
                    j = j[1:]
                elif j[0] == 'd':
                    flags['command'] = CMD_DESCRIBE_DWORDS
                    j = j[1:]
                elif j[0] == 'q':
                    flags['command'] = CMD_DESCRIBE_QWORDS
                    j = j[1:]
                elif j[0] == 'a':
                    flags['command'] = CMD_DESCRIBE_STRING
                    j = j[1:]
                elif j[0] == 'u':
                    flags['command'] = CMD_DESCRIBE_UNICODE
                    j = j[1:]
            if len(j):
                flags['data-count'] = safe_int(j,0)

    return flags,args
