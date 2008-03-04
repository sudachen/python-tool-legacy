#!/usr/bin/python

import os, os.path, sys, shutil

sys.path.append('../../lib')
from make import *
process_command_line();

if sys.platform == 'win32':
    os.putenv('LIB','.'+';'+'../../lib'+';'+'%s/Libs/'%sys.prefix+';'+os.environ['LIB'])
    pythonXX_lib = 'python%s%s.lib' % (sys.version_info[0], sys.version_info[1])
else:
    pythonXX_lib = '-lpython%s.%s' % (sys.version_info[0], sys.version_info[1])


if sys.platform == 'win32':
    CC_flags = [
        '-MD',
        '-Ox',
        '-Z7',
        '-DHAVE_MEMMOVE',
        '-DWIN32',
        '-DNDEBUG',
        '-D_WINDOWS',
        '-I"."',
        '-I"%s/include"' % sys.prefix,
        ]
    CC_flags.append('-nologo')
else:
    CC_flags = [
	'-O2',
	'-g',
	'-ggdb',
        '-DNDEBUG',
        '-I"."',
        '-I"/usr/include/python%s"' % sys.version[:3],
	]

global_flags_set['C_FLAGS'] = CC_flags

tempdir = '../../../build-temp/_ctypes-' + get_build_type()

sources = [
    'prep_cif.c',
    'stgdict.c',
    'cfield.c',
    'callproc.c',
    'callbacks.c',
    'malloc_closure.c',
    '_ctypes.c',
    ]

if sys.platform == 'win32':
    sources += ['win32.c','ffi.c',]
else:
    sources += ['sysv.S','ffi_x86.c',]

if sys.platform == 'win32':
    linker_flags = [
	'-nologo',
        '-incremental:no',
        '-release',	
        '-debug',
        '-dll',
        '-opt:ref',
        '-opt:icf',
        '-export:init_ctypes',
        '-base:0x3300000',
        '-libpath:.',
        '-pdb:../../_ctypes.pdb',
        '-implib:../../lib/_ctypes.lib',
	]
else:
    linker_flags = [
	]

global_flags_set['LINK_FLAGS'] = linker_flags

if sys.platform == 'win32':
    libs = [	
	'kernel32.lib',
        'user32.lib',
	'advapi32.lib',
        'shell32.lib',
	'ole32.lib',
        'oleaut32.lib',
	'gdi32.lib',
        'ws2_32.lib',
	pythonXX_lib,
	]
else:
    libs = [
	'-lm',
	'-lc',
	'-ldl',
	pythonXX_lib,
	]

objects = compile_files(sources,tempdir)

if sys.platform == 'win32':
    link_shared(objects,libs,tempdir,'../../_ctypes.pyd')
else:
    link_shared(objects,libs,tempdir,'../../_ctypes.so')

