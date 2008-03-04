#!/usr/bin/python

import os, os.path, sys, shutil
sys.path.append('../../lib')
from make import *

process_command_line();

tempdir = os.path.abspath('../../../build-temp/pycrt' + get_build_type())
python_base = '../../2.4.4'
#os.putenv('LIB','.'+';'+'../../lib'+';'+os.environ['LIB'])

Platform = sys.platform
if Platform != 'win32': Platform = 'posix'

if Platform == 'win32':
    CC_flags = [
        '-MD',
        '-Ox',
        '-Z7',
        '-DPyMODINIT_FUNC=void',
        '-DWIN32',
        '-DNDEBUG',
        '-D_WINDOWS',
        ]
    CC_flags.append('-nologo')
else:
    CC_flags = [
        '-O2',
        '-g -ggdb',
        '-DNDEBUG',
        '-D__fastcall= ',
        '--short-wchar',
        '-Dstricmp=strcasecmp',
        ]

CC_flags += [
    '-I"../../Include/'+Platform+'"',
    '-I"%s/PC"'%python_base,
    '-I"%s/Include"'%python_base,
    '-I"%s/Python"'%python_base,
    '-I"%s/Modules/expat"'%python_base,
    '-I"../_ctypes"',
    '-D"Py_NO_ENABLE_SHARED"',
    '-DPyMODINIT_FUNC=void',
    '-DUSE_DL_EXPORT',
    '-DXML_STATIC',
    '-DHAVE_MEMMOVE',
    ]

CC_flags.append('-I../zS')
global_flags_set['C_FLAGS'] = CC_flags

sources = [
    'Python/pythonrun.c',
    'Modules/_bisectmodule.c',
    'Modules/_codecsmodule.c',
    'Modules/_heapqmodule.c',
    'Modules/_hotshot.c',
    'Modules/_localemodule.c',
    'Modules/_randommodule.c',
    'Modules/_sre.c',
    'Modules/_weakref.c',
    'Modules/arraymodule.c',
    'Modules/binascii.c',
    'Modules/cmathmodule.c',
    'Modules/collectionsmodule.c',
    'Modules/cPickle.c',
    'Modules/cStringIO.c',
    'Modules/datetimemodule.c',
    'Modules/errnomodule.c',
    'Modules/gcmodule.c',
    'Modules/mathmodule.c',
    'Modules/md5c.c',
    'Modules/md5module.c',
    'Modules/itertoolsmodule.c',
    'Modules/main.c',
    'Modules/mmapmodule.c',
    'Modules/operator.c',
    'Modules/parsermodule.c',
    'Modules/shamodule.c',
    'Modules/signalmodule.c',
    'Modules/stropmodule.c',
    'Modules/structmodule.c',
    'Modules/symtablemodule.c',
    'Modules/threadmodule.c',
    'Modules/timemodule.c',
    'Modules/xxsubtype.c',
    'Modules/yuvconvert.c',
    'Modules/zipimport.c',
    'Modules/zlibmodule.c',
    'Modules/pyexpat.c',
    'Modules/expat/xmlparse.c',
    'Modules/expat/xmlrole.c',
    'Modules/expat/xmltok.c',
    'Modules/socketmodule.c',
    'Modules/selectmodule.c',
    'Parser/acceler.c',
    'Parser/bitset.c',
    'Parser/grammar1.c',
    'Parser/listnode.c',
    'Parser/metagrammar.c',
    'Parser/myreadline.c',
    'Parser/node.c',
    'Parser/parser.c',
    'Parser/parsetok.c',
    'Parser/tokenizer.c',
    'Objects/abstract.c',
    'Objects/boolobject.c',
    'Objects/bufferobject.c',
    'Objects/cellobject.c',
    'Objects/classobject.c',
    'Objects/cobject.c',
    'Objects/complexobject.c',
    'Objects/descrobject.c',
    'Objects/dictobject.c',
    'Objects/enumobject.c',
    'Objects/fileobject.c',
    'Objects/floatobject.c',
    'Objects/frameobject.c',
    'Objects/funcobject.c',
    'Objects/genobject.c',
    'Objects/intobject.c',
    'Objects/iterobject.c',
    'Objects/listobject.c',
    'Objects/longobject.c',
    'Objects/methodobject.c',
    'Objects/moduleobject.c',
    'Objects/object.c',
    'Objects/obmalloc.c',
    'Objects/rangeobject.c',
    'Objects/setobject.c',
    'Objects/sliceobject.c',
    'Objects/stringobject.c',
    'Objects/structseq.c',
    'Objects/tupleobject.c',
    'Objects/typeobject.c',
    'Objects/unicodectype.c',
    'Objects/unicodeobject.c',
    'Objects/weakrefobject.c',
    'Python/bltinmodule.c',
    'Python/ceval.c',
    'Python/codecs.c',
    'Python/compile.c',
    'Python/errors.c',
    'Python/exceptions.c',
    'Python/frozen.c',
    'Python/future.c',
    'Python/getargs.c',
    'Python/getcompiler.c',
    'Python/getcopyright.c',
    'Python/getmtime.c',
    'Python/getopt.c',
    'Python/getplatform.c',
    'Python/getversion.c',
    'Python/graminit.c',
    'Python/importdl.c',
    'Python/marshal.c',
    'Python/modsupport.c',
    'Python/mysnprintf.c',
    'Python/mystrtoul.c',
    'Python/pyfpe.c',
    'Python/pystate.c',
    'Python/pystrtod.c',
    'Python/structmember.c',
    'Python/symtable.c',
    'Python/sysmodule.c',
    'Python/thread.c',
    'Python/traceback.c',
    'Modules/posixmodule.c',
    'Python/import.c',
    'Modules/getbuildinfo.c',
    ]

if Platform == 'win32':
    sources += [
        'PC/_winreg.c',
        'PC/import_nt.c',
        'PC/msvcrtmodule.c',
        'PC/dl_nt.c',
        'Python/dynload_win.c',
        'PC/_subprocess.c',
        'PC/getpathp.c',
        ]
else:
    sources += [
        'Python/dynload_shlib.c',
        'Modules/getpath.c',
        #'Python/importdl.c',
        ]

sources = normolize_sources(sources,python_base)
sources += [
    '../_lzss/_lzss.c'
    ]
sources += [
    '../_udis86/_udis86.c'
    ]

sources += [
    '../_ctypes/prep_cif.c',
    '../_ctypes/stgdict.c',
    '../_ctypes/cfield.c',
    '../_ctypes/callproc.c',
    '../_ctypes/callbacks.c',
    '../_ctypes/malloc_closure.c',
    '../_ctypes/_ctypes.c',
    ]

if Platform == 'win32':
    sources += ['../_ctypes/win32.c','../_ctypes/ffi.c',]
else:
    sources += ['../_ctypes/sysv.S','../_ctypes/ffi_x86.c',]

sources += [
    '../zS/zl_adler32.c',
    '../zS/zl_compress.c',
    '../zS/zl_crc32.c',
    '../zS/zl_deflate.c',
    '../zS/zl_infblock.c',
    '../zS/zl_infcodes.c',
    '../zS/zl_inffast.c',
    '../zS/zl_inflate.c',
    '../zS/zl_inftrees.c',
    '../zS/zl_infutil.c',
    '../zS/zl_trees.c',
    '../zS/zl_uncompr.c',
    '../zS/zutil.c',
    ]

sources += [
    '../_udis86/libudis86/decode.c',
    '../_udis86/libudis86/input.c',
    '../_udis86/libudis86/mnemonics.c',
    '../_udis86/libudis86/opcmap.c',
    '../_udis86/libudis86/syn-att.c',
    '../_udis86/libudis86/syn-intel.c',
    '../_udis86/libudis86/syn.c',
    '../_udis86/libudis86/udis86.c',
    ]

sources += ['config.c','_pycrt.c']
objects = compile_files(sources,tempdir)

if Platform == 'win32':
    linker_flags = [
        '-nologo',
        '-incremental:no',
        '-release',
        '-debug',
        '-dll',
        '-opt:ref',
        '-opt:icf',
        '-def:pycrt.def',
        '-base:0x3200000',
        '-libpath:.',
        '-libpath:../../lib',
        '-pdb:../../pycrt.pdb',
        '-implib:../../lib/pycrt.lib',
        ]
else:
    linker_flags = [
#        '-g','-ggdb',
        '-L"../../lib"',
        ]

global_flags_set['LINK_FLAGS'] = linker_flags

if Platform == 'win32':
    libs = [
        'kernel32.lib',
        'user32.lib',
        'advapi32.lib',
        'shell32.lib',
        'ole32.lib',
        'oleaut32.lib',
        'gdi32.lib',
        'ws2_32.lib',
        ]
else:
    libs = [
        '-lm',
        '-lpthread',
        '-ldl',
        '-lc',
        '-lutil'
        ]

if Platform == 'win32':
    link_shared(objects,libs,tempdir,'../../pycrt.dll')
    link_static(objects,tempdir,'../../lib/pycrtS.lib')
else:
    link_shared(objects,libs,tempdir,'../../libpycrt.so')
    link_static(objects,tempdir,'../../lib/libpycrtS.a')
