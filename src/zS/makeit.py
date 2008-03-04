#!/usr/bin/python

import os,sys,os.path

os.chdir(os.path.dirname(sys.argv[0]))
sys.path.append('../../lib')
from make import *

process_command_line();

Platform = sys.platform
if Platform != 'win32': Platform = 'posix'

files = \
('zl_adler32.c',
'zl_compress.c',
'zl_crc32.c',
'zl_deflate.c',
'zl_infblock.c',
'zl_infcodes.c',
'zl_inffast.c',
'zl_inflate.c',
'zl_inftrees.c',
'zl_infutil.c',
'zl_trees.c',
'zl_uncompr.c',
'zutil.c')

srcdir = '.'
tmpdir = '../../../build-temp/pycrt-zlibS'

files = [ os.path.join(srcdir,i) for i in files ]

if Platform == 'win32':
    CC_flags = [
        '-MD',
        '-Ox',
        '-Z7',
        '-DWIN32',
        '-DNDEBUG',
        '-D_WINDOWS',
        ]
    CC_flags.append('-nologo')
else:
    CC_flags = [
        '-O2',
        '-g','-ggdb',
        '-DNDEBUG',
        ]

global_flags_set['C_FLAGS'] = CC_flags
objects = compile_files(files,tmpdir)

if Platform == 'win32':
  link_static(objects,tmpdir,'../../lib/zS.lib')
else:
  link_static(objects,tmpdir,'../../lib/libzS.a')
