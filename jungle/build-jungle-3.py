
import os, os.path, stat

build_type = 'release'
tempdir = os.path.abspath('../../~temp~/jungle3-%s' % build_type)

if not os.path.exists(tempdir):
    os.makedirs(tempdir)

class CompilationError(Exception):
    pass

def build_compile_CL(tempdir,cc_flags,fname_I,fname_O):
    ext = os.path.splitext(fname_O)[1]
    compiler = None

    if ext == '.c':
        compiler = 'cl  %s -c -Fo"%%s" "%%s"' % ' '.join(cc_flags)
        fname_O = os.path.join(tempdir,fname_O[0:-2] + '.obj')

    if len(os.path.dirname(fname_O)) and not os.path.exists(os.path.dirname(fname_O)):
        os.makedirs(os.path.dirname(fname_O))

    if compiler:
        fmtime_O = None

        if os.path.exists(fname_O):
            fmtime_O = os.stat(fname_O)[stat.ST_MTIME]
            fmtime_I = os.stat(fname_I)[stat.ST_MTIME]

        if fmtime_O == None or fmtime_O < fmtime_I:
            cmd_S = compiler % (fname_O,fname_I)
            print cmd_S
            if 0 != os.system( cmd_S ):
                raise CompilationError(fname_I)
            fmtime_O = os.stat(fname_O)[stat.ST_MTIME]

        return (fname_O,fmtime_O,fname_I)
    else:
        raise CompilationError('unknwon file type')

def build_CL_files(tempdir,base,cc_flags,files):
    ret = []
    for f in files:
        f_path   = os.path.normpath(os.path.join(base,f))
        f_path_O = f_path.replace('..'+os.sep,'@')
        f_path_O = f_path_O.replace(os.sep,'#')
        ret.append(build_compile_CL(tempdir,cc_flags,f_path,f_path_O))
    return ret

def build_link_shared(tempdir,files,ld_flags,target):
    objectslist = os.path.join(tempdir,"~objectslist~")
    if os.path.exists(objectslist):
        os.unlink(objectslist)
    f = open(objectslist,"w+t")
    for i in files:
        f.write('"'+i[0]+'"\n')
    f.close()
    cmd_S = ('link -out:"%s" '%target)+' '.join(ld_flags)+(' @"%s"'%objectslist)
    print cmd_S
    if 0 != os.system( cmd_S ):
        raise CompilationError(target)

def build_lib_static(tempdir,files,lib_flags,target):
    objectslist = os.path.join(tempdir,"~objectslist~")
    if os.path.exists(objectslist):
        os.unlink(objectslist)
    f = open(objectslist,"w+t")
    for i in files:
        f.write('"'+i[0]+'"\n')
    f.close()
    cmd_S = ('lib -out:"%s" '%target)+' '.join(lib_flags)+(' @"%s"'%objectslist)
    print cmd_S
    if 0 != os.system( cmd_S ):
        raise CompilationError(target)

python_base = '../../Python/2.4.4'
os.putenv('LIB','../../Python'+';'+os.environ['LIB'])

CC_flags = [
        '-MD',
        '-Ox',
        '-DPyMODINIT_FUNC=void',
        '-DUSE_DL_EXPORT',
        '-DXML_STATIC',
        '-DHAVE_MEMMOVE',
        '-DWIN32',
        '-DNDEBUG',
        '-D_WINDOWS',
    '-I"%s/PC"'%python_base,
        '-I"%s/Include"'%python_base,
        '-I"%s/Python"' %python_base,
        '-I"%s/Modules/expat"' %python_base,
    '-D"-Py_NO_ENABLE_SHARED"',
        ]

CC_flags.append('-nologo')
CC_flags.append('-I../../Media/lib.z')

l = build_CL_files(tempdir,python_base,CC_flags,(
'PC/_winreg.c',
'PC/import_nt.c',
'PC/msvcrtmodule.c',
'PC/_subprocess.c',
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
'PC/getpathp.c',
'Modules/posixmodule.c',
'Python/pythonrun.c',
'Python/import.c',
'Modules/getbuildinfo.c',
'Python/dynload_win.c',
'PC/dl_nt.c',
))

#l.extend(build_CL_files(tempdir,os.path.join(media_base,'lib.z'),CC_flags,(
#'zl_adler32.c',
#'zl_compress.c',
#'zl_crc32.c',
#'zl_deflate.c',
#'zl_infblock.c',
#'zl_infcodes.c',
#'zl_inffast.c',
#'zl_inflate.c',
#'zl_inftrees.c',
#'zl_infutil.c',
#'zl_trees.c',
#'zl_uncompr.c',
#'zutil.c',
#)))

l.extend(build_CL_files(tempdir,'.',CC_flags,(
'config.c',
)))

linker_flags = (
    '-incremental:no',
    '-release',
    '-debug',
    '-dll',
    '-map',
    '-opt:ref',
    '-opt:icf',
    '-def:jungle.def',
    '-base:0x3200000',
    '-libpath:.',
    '-pdb:jungle.pdb',
    '-implib:./jungle3.lib',
    'kernel32.lib',
    'user32.lib',
    'advapi32.lib',
    'shell32.lib',
    'ole32.lib',
    'oleaut32.lib',
    'gdi32.lib',
    'ws2_32.lib',
    'z.lib',
    )

build_link_shared(tempdir,l,linker_flags,'jungle3.dll')

lib_flags = ['z.lib',]

build_lib_static(tempdir,l,lib_flags,'jungle3s.lib')
