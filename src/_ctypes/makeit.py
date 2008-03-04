
import os, os.path, sys, shutil
Platform = sys.platform
if Platform != 'win32': Platform = 'posix'

sys.path.append('../../lib')
from make import *
process_command_line();

pythonXX_lib = 'python%s%s.lib' % (sys.version_info[0], sys.version_info[1])

os.putenv('LIB','.'+';'+'../../lib'+';'+'%s/Libs/'%sys.prefix+';'+os.environ['LIB'])
python_base = '../../2.4.4'

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
global_flags_set['C_FLAGS'] = CC_flags

tempdir = '../../../~temp~/pycrt-_ctypes-' + get_build_type()

sources = [
    'prep_cif.c',
    #'types.c',
    'stgdict.c',
    'cfield.c',
    'callproc.c',
    'callbacks.c',
    'ffi.c',
    'malloc_closure.c',
    'win32.c',
    '_ctypes.c',
    ]

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
global_flags_set['LINK_FLAGS'] = linker_flags

libs = [
    'kernel32.lib',
    'user32.lib',
    'advapi32.lib',
    'shell32.lib',
    'ole32.lib',
    'oleaut32.lib',
    'gdi32.lib',
    'ws2_32.lib',
    'zS.lib',
    pythonXX_lib,
    ]

objects = compile_files(sources,tempdir)
link_shared(objects,libs,tempdir,'../../_ctypes.pyd')
link_static(objects,tempdir,'../../lib/_ctypesS.lib')
