# -*- coding: cp1251 -*-
#
# (c)2008, Alexey Sudachen, alexey@sudachen.name
# http://www.ethical-hacker.info/jungle
#

version = "3.0"

import sys,os,os.path,getopt,marshal,locale
from modulefinder import *

locale.setlocale(locale.LC_ALL,'')

flags = { \
    'subsystem':'console',
    'addpath':[],
    'exclude':[],
    'depth':1,
    'cc':'gnu',
    }

flags['exclude'].extend(['os2emxpath','macpath','ce','riscos','riscospath'])

if sys.platform == 'win32':
    import _winreg
elif sys.platform.startswith('linux'):
    pass


usage_msg = """jungle [options] main_python_file.py

-p <path of modules separated by '"""+os.pathsep+"""'>
-x <excluded module name>
-l <shared object/dynamic library name> current python2x by default
-r <precompiled runtime modules> 'jungle.Z' by default
-f "<compiler flags>"

--verbose   verbose compilation process
--no-logo   hide copyright logo
--no-main   produce .C files contains frized modules table
--c-only    produce .C file only, do not link final binary
--single    compile only main file
--local     compile if in script folder (*default)
--all       compile all dependenses

microsoft windows specific:
--rc <rcfile.RC>
--cc <gnu|ms>[,"compiler.exe-path"] """+flags['cc']+""" by default
--windows   make executable for subsystem 'windows'
--console   make executable for subsystem 'console' (*defult)
"""

#--no-python disable to find & append path of installed python modules

class ErrorMessageException(Exception):
    pass

def GetMyOpts(a):
    try:
        return getopt.getopt(
              a,
              'o:p:x:l:r:f:?hvVZ',
              ['no-python',
               'no-logo',
               'no-main',
               'c-only',
               'python='
               'runtime=',
               'c-flags=',
               'jrtl=',
               'rcfile=',
               'windows',
               'help',
               'verbose',
               'single',
               'local',
               'all',
               'cc=',
               'print-version'])
    except getopt.error:
        raise ErrorMessageException(str(sys.exc_info()[1]))

def OperateWithOpts(opts,flags):
    global version
    for o, a in opts:
        if o == '--verbose' or o == '-v':
            flags['debug'] = True
        if o == '-p':
            def prepare_paths(p):
                s_path = os.path.normpath(os.path.abspath(os.path.dirname(args[0])))
                j = []
                for i in p:
                    if not os.path.isabs(i):
                        j.append( os.path.normpath(os.path.join(s_path,i)) )
                    else:
                        j.append(i)
                return j
            flags['addpath'].extend(prepare_paths(a.strip('"').split(os.pathsep)))
        if o == '-x':
            flags['exclude'].append(a)
        if o == '-?' or o == '-h' or o == '--help':
            print usage_msg
            sys.exit(0)
        if o == '-o':
            flags['output-name'] = a
        if o == '--runtime' or o == '-r':
            flags['runtime'] = os.path.normpath(os.path.abspath(a))
        if o == '--python' or o == '-l':
            flags['python'] = a
        if o == '--no-main':
            flags['no-main'] = True
        if o == '--c-only':
            flags['c-only'] = True
        if o == '--c-flags' or o == '-f':
            flags['c-flags'] = a
        if o == '--jrtl':
            flags['jrtl'] = a
        if o == '--windows':
            flags['subsystem'] = 'windows'
        if o == '--no-python':
            flags['no-python'] = True
        if o == '--no-logo':
            flags['no-logo'] = True
        if o == '--rcfile':
            flags['rcfile'] = a
        if o == '--cc':
            cc_path = None
            i = a.find(',')
            if i > 0:
                cc_path = a[i+1:]
                a = a[:i]
            flags['cc'] = a
            if cc_path: flags['cc-path'] = cc_path
        if o == '--single':
            flags['depth'] = 0
        if o == '--local':
            flags['depth'] = 1
        if o == '--all':
            flags['depth'] = 2
        if o == '-Z':
            flags['compress'] = True
        if o == '--print-version' or o == '-V':
            print version
            sys.exit(0)

def Compile(files,path,exclude,debug,no_main,depth,C_file):

    mf = ModuleFinder(path, debug, exclude)
    for arg in files[1:]: mf.load_file(arg)
    mf.run_script(files[0])
    if debug: mf.report()

    def sort(x): x.sort(); return x

    compiled = []
    modules_size = 0
    modules_nsize = 0

    main_folder = os.path.dirname(os.path.normpath(os.path.abspath(mf.modules['__main__'].__file__)))

    print "--->>"
    for real_name in sort(mf.modules.keys()):
        m = mf.modules[real_name]
        if real_name == '__main__' and no_main:
            continue
        if real_name != '__main__' and depth == 0:
            continue
        if depth < 2 and m.__file__ \
                and not os.path.dirname(os.path.normpath(os.path.abspath(m.__file__))).startswith(main_folder):
            continue
        name = "__".join(real_name.split("."))
        if m.__code__:
            s = marshal.dumps(m.__code__)
            o_msize = len(s)
            o_nsize = o_msize

            if not m.__path__:

                if compress_hook:
                    try:
                        s = compress_hook(s,'JJLZ')
                        o_nsize = len(s)
                    except:
                        #print str(sys.exc_info()[1])
                        pass

                j_code = 'ed62969f98484bca902e8af82f039880("%s",%s)\n' % (real_name,repr(s))
                c = compile(j_code,m.__file__,'exec')
                s = marshal.dumps(c)

            msize = len(s)
            nsize = msize
            modules_size += o_msize
            modules_nsize += o_nsize
            print "%3d%% %-24s %s" % ( (o_nsize*100)/o_msize, real_name, m.__file__ )
            C_file.write("static char _S_"+name+"[] = \n")
            for i in xrange(0,nsize):
              if i % 19 == 0:
                  if i: C_file.write("\"\n")
                  C_file.write("  \"")
              C_file.write("\\x%02x"%ord(s[i]))
            C_file.write("\";\n")
            #C_file.write(("int _S_"+name+"_length = %d;\n") %  nsize)
            if m.__path__: msize = -msize
            compiled.append( (name, real_name, msize, nsize) )

    print "---<<\nsummary: %d bytes of modules was written, it's %d%% of original %d bytes" % \
        (modules_nsize, modules_nsize*100/modules_size, modules_size)

    return compiled

def FreezeTable(compiled,C_file):
    C_file.write("\nstatic struct {char*_1;char*_2;int _3;} _Jungle_Modules[] = {\n")
    for i in compiled: C_file.write("{\"%s\",_S_%s,%d},\n" % (i[1],i[0],i[2]) )
    C_file.write("{0,0,0}};\n")

def AppendPythonPath(ignore_python):
    addpath = []
    if not ignore_python:
        pypath = os.getenv('PYTHONPATH',None)
        if pypath:
            addpath.extend(pypath.split(os.pathsep))
        if sys.platform == 'win32':
            ptn_ver = sys.version[:3]
            hkey = None
            for reg_base in (_winreg.HKEY_CURRENT_USER,_winreg.HKEY_LOCAL_MACHINE) :
                try:
                    hkey = _winreg.OpenKey(reg_base,'Software\\Python\\PythonCore\\'+ptn_ver+'\\PythonPath')
                    try:
                        s,t = _winreg.QueryValueEx(hkey,'')
                        addpath.extend(str(s).split(os.pathsep))
                        try:
                            hkey2 = _winreg.OpenKey(reg_base,'Software\\Python\\PythonCore\\'+ptn_ver+'\\InstallPath')
                            try:
                                s,t = _winreg.QueryValueEx(hkey2,'')
                                addpath.append(os.path.join(str(s),'Lib\\site-packages\\win32\\Lib'))
                            finally:
                                _winreg.CloseKey(hkey2)
                        except:
                            pass
                        return addpath
                    finally:
                        _winreg.CloseKey(hkey)
                except EnvironmentError:
                    pass
    return addpath

compress_hook = None

def Main(script,sys_argv):
    global flags, version, frozen_main, compress_hook
    opts, args = GetMyOpts(sys_argv)
    OperateWithOpts(opts,flags)

    if not flags.get('no-logo'):
        print ".Py Compiler "+version+" - the .py to .exe compiler"
        print "(c)2008, Alexey Sudachen, alexey@sudachen.name"
        print "http://www.ethical-hacker.com/jungle"
        print "~\n"

    if not args:
        print "error: there is no input file"
        print "~\n"
        print usage_msg
        sys.exit(-1)

    path = [os.path.normpath(os.path.dirname(args[0])),os.path.normpath(os.path.dirname(script))]
    path.extend(sys.path)
    path.extend(flags['addpath'])
    path.extend(AppendPythonPath(flags.get('no-python')))
    sys.path.extend(AppendPythonPath(False))

    if flags.get('compress'):
        try:
            import _lzss
            compress_hook = _lzss.compress
        except:
            print 'failed to load _lzss extesion, compression is disabled'

    output_name = flags.get('output-name',None)
    if not output_name:
        output_name = os.path.splitext(os.path.basename(args[0]))[0]
    if sys.platform == 'win32':
        if not output_name.lower().endswith('.exe'):
            output_name = output_name + '.exe'
    C_file_name = output_name + '.c'
    C_file = open(C_file_name,"w+t")
    C_file.write(frozen_header)
    compiled = Compile(args,path,flags['exclude'],flags.get('debug'),flags.get('no-main'),flags.get('depth'),C_file)
    FreezeTable(compiled,C_file)
    C_file.write(frozen_main)
    if flags['subsystem'] == 'windows' and sys.platform == 'win32':
        C_file.write(build_argv)
    C_file.close()

    if not flags.get('c-only') and not flags.get('no-main'):
        if sys.platform == 'win32':
            flags['c-flags'] = flags.get('c-flags','') + ' -D_JUNGLE_ON_WINDOWS'
        else:
            flags['c-flags'] = flags.get('c-flags','') + ' -D_JUNGLE_ON_POSIX'

        if flags.get('python'):
            if flags['cc'] == 'ms':
                python_lib = flags['python']+'.lib'
            else:
                python_lib = '-l'+flags['python']
        else:
            if sys.platform == 'win32':
                if flags['cc'] == 'ms':
                    python_lib = os.path.join(sys.exec_prefix,'libs','python%d%d.lib'%sys.version_info[:2])
                else:
                    python_lib = '-L"'+os.path.join(sys.exec_prefix,'libs')+'" -lpython%d%d'%sys.version_info[:2]
            else:
                python_lib = '-lpython%d%d'%sys.version_info[:2]

        if flags['subsystem'] == 'windows' and sys.platform == 'win32':
            flags['c-flags'] = flags['c-flags']+ ' -D_JUNGLE_WINDOWS_SUBSYSTEM'
        else:
            flags['c-flags'] = flags['c-flags']+ ' -D_JUNGLE_CONSOLE_SUBSYSTEM'

        if flags['cc'] == 'ms' and sys.platform == 'win32':
            CC = flags.get('cc-path','cl')
            cmd_S = '%s %s "%s" -o "%s" "%s"' % (CC,flags['c-flags'],C_file_name,output_name,python_lib)
        else:
            CC = flags.get('cc-path','gcc')
            cmd_S = '%s %s "%s" -o "%s" %s' % (CC,flags['c-flags'],C_file_name,output_name,python_lib)

        print cmd_S
        if os.system(cmd_S) != 0 :
            raise ErrorMessageException('failed to compile .C code to binary image')

frozen_header = """
/*

  This source file was generated with Jungle
  Jungle .Py Compiler available at http://www.ethical-hacker.info/jungle

  On *NIX:  gcc -D_JUNGLE_ON_POSIX <source_C> -o <binary> -lpython2x

*/

"""

frozen_main = """
#include <stdlib.h>
#include <malloc.h>
#include <string.h>

#if defined _WIN32
#define DLL_IMPORT __declspec(dllimport)
#else
#define DLL_IMPORT
#endif

/*extern struct _frozen _Jungle_Modules[];*/
struct _frozen { char *name; unsigned char *code; int size; };

DLL_IMPORT extern struct _frozen *PyImport_FrozenModules;
DLL_IMPORT extern int Py_SetProgramName(char *);
DLL_IMPORT extern int PyImport_ImportFrozenModule(char *);
DLL_IMPORT extern int PySys_SetArgv(int argc,char **argv);
DLL_IMPORT extern int Py_FatalError(char *);
DLL_IMPORT extern int PyErr_Print();
DLL_IMPORT extern int Py_Initialize();
DLL_IMPORT extern int Py_Finalize();
DLL_IMPORT extern int Py_FrozenFlag;
DLL_IMPORT extern int Py_IgnoreEnvironmentFlag;
DLL_IMPORT extern int Py_OptimizeFlag;

static int j_frozen_main(struct _frozen *);

static void *frozen_table_mem = 0;
static int  frozen_table_count = 0;

static j_init_frozen_table()
  {
    if ( !frozen_table_count )
      {
        struct _frozen *i = (struct _frozen*)_Jungle_Modules;
        PyImport_FrozenModules = i;
        while ( i->name ) ++frozen_table_count, ++i;
      }
  }

static void j_extend_frozen_table(struct _frozen *ftable, int before)
  {
    int ftable_count = 0;
    struct _frozen *i = ftable;
    struct _frozen *mem = 0;
    while ( i->name ) ++ftable_count, ++i;
    mem = (struct _frozen *)malloc( sizeof(struct _frozen)*(ftable_count+frozen_table_count+1) );
    memcpy( mem + (before?0:frozen_table_count), ftable, ftable_count*sizeof(struct _frozen));
    memcpy( mem + (!before?0:ftable_count), PyImport_FrozenModules, frozen_table_count*sizeof(struct _frozen));
    if ( frozen_table_mem ) free(frozen_table_mem);
    frozen_table_mem = mem;
    PyImport_FrozenModules = mem;
    frozen_table_count += ftable_count;
    memset( PyImport_FrozenModules + frozen_table_count, 0, sizeof(struct _frozen) );
  }

typedef struct PyObject PyObject;
typedef struct PyMethodDef {
    char  *ml_name; /* The name of the built-in function/method */
    void  *ml_meth; /* The C function that implements it */
    int    ml_flags;  /* Combination of METH_xxx flags, which mostly
           describe the args expected by the C func */
    char  *ml_doc;  /* The __doc__ attribute, or NULL */
} PyMethodDef;
enum {METH_VARARGS =0x0001};
DLL_IMPORT extern PyObject _Py_NoneStruct;
#define Py_None (&_Py_NoneStruct)

DLL_IMPORT extern void      Py_IncRef(PyObject *o);
DLL_IMPORT extern void      Py_DecRef(PyObject *o);
DLL_IMPORT extern PyObject *PyImport_ExecCodeModuleEx(char *name, PyObject *co, char *pathname);
DLL_IMPORT extern PyObject *PyImport_GetModuleDict();
DLL_IMPORT extern PyObject *PyDict_GetItemString(PyObject *,char *);
DLL_IMPORT extern PyObject *PyCFunction_NewEx(PyMethodDef *,void *,PyObject *);
DLL_IMPORT extern void      PyModule_AddObject(PyObject *,char *,PyObject *);
DLL_IMPORT extern PyObject *PyMarshal_ReadObjectFromString(char *, int);
DLL_IMPORT extern PyObject *PyImport_AddModule(char *);
DLL_IMPORT extern PyObject *PyImport_ImportModule(char *);
DLL_IMPORT extern void      PyErr_Clear();
DLL_IMPORT extern PyObject *PyExc_ImportError;

static void j_builtin_function(PyMethodDef *ml)
  {
    PyObject *builtin, *pfunc;
    builtin  = PyDict_GetItemString(PyImport_GetModuleDict(),"__builtin__");
    pfunc    = PyCFunction_NewEx(ml,0,0);
    PyModule_AddObject(builtin,ml->ml_name,pfunc);
    PyErr_Clear();
  }

static PyObject *j_import_frozen_module(PyObject *,PyObject *args);
static PyMethodDef j_import_frozen_module_ml = { "ed62969f98484bca902e8af82f039880",&j_import_frozen_module,METH_VARARGS,0};

int j_frozen_main_1(int argc, char **argv)
  {
    char *p;
    int n;
    struct _frozen *Z_frozen = 0;

    j_init_frozen_table();

#if defined _JUNGLE_USE_RUNTIME
    Z_frozen = j_access_runtime(_JUNGLE_USE_RUNTIME);

    if ( Z_frozen )
      {
        j_extend_frozen_table(Z_frozen,0);
      }
#endif

    Py_FrozenFlag = 1; /* Suppress errors from getpath.c */
    Py_IgnoreEnvironmentFlag = 1;
    Py_OptimizeFlag = 1;
    Py_SetProgramName(argv[0]);
    Py_Initialize();
    PySys_SetArgv(argc,argv);

    j_builtin_function(&j_import_frozen_module_ml);
    n = PyImport_ImportFrozenModule("__main__");

    if (n == 0)
      Py_FatalError("__main__ not frozen");
    if (n < 0)
      PyErr_Print();
    Py_Finalize();
    return n<0?-1:0;
  }

static char **j_buildargv(char *input,int *count);

#if defined _JUNGLE_ON_POSIX || defined _JUNGLE_CONSOLE_SUBSYSTEM
int main(int argc,char **argv)
#elif defined _JUNGLE_ON_WINDOWS && defined _JUNGLE_WINDOWS_SUBSYSTEM
char *__stdcall GetCommandLineA();
int __stdcall WinMain(int _0,int _1,int _2,int _3)
#else
#error "unknown platform"
#endif
  {
    int sts = 0;
#if defined _JUNGLE_ON_WINDOWS && defined _JUNGLE_WINDOWS_SUBSYSTEM
    int argc = 0;
    char **argv = j_buildargv( GetCommandLineA(), &argc );
#endif
    return j_frozen_main_1(argc,argv);
  }

static char *j_jjlz_decompressor(unsigned char *buffer, int *len);
static PyObject *j_import_frozen_module(PyObject *_0,PyObject *args)
  {
    char *mod_name = 0, *mod_code = 0, *mod_file = "<frozen>";
    int mod_code_len = 0;
    if ( PyArg_ParseTuple(args,"ss#|s",&mod_name,&mod_code,&mod_code_len,&mod_file) )
      {
        PyObject *code = 0;
        PyObject *o = 0;
        char *temp_buff = 0;
        if ( mod_code_len >= 8 && 0 == memcmp(mod_code,"JJLZ",4) )
          {
            temp_buff = j_jjlz_decompressor(mod_code,&mod_code_len);
            if ( !temp_buff )
              {
                PyErr_SetString(PyExc_ImportError,"failed to init module");
                return 0;
              }
            mod_code = temp_buff;
          }

        code = PyMarshal_ReadObjectFromString(mod_code,mod_code_len);
        if ( temp_buff ) free(temp_buff);

        if ( code )
          {
            o = PyImport_ExecCodeModuleEx(mod_name, code, mod_file);
            Py_DecRef(code);
          }
        if ( o )
          {
            Py_IncRef(Py_None);
            return Py_None;
          }
      }
    return 0;
  }

static char *j_jjlz_decompressor(unsigned char *in_b, int *inout_len)
  {
    enum { JJLZ_MAX_LEN = 15 };

    int  out_i=0, in_i = 0, out_b_len, in_b_len = *inout_len-8;
    char *out_b;

    in_b += 4; /*skip 'JJLZ'*/
    out_b_len = (unsigned int)in_b[0]|((unsigned int)in_b[1]<<8)|
          ((unsigned int)in_b[2]<<16)|((unsigned int)in_b[3]<<24);
    out_b = malloc(out_b_len);
    in_b += 4; /*skip out_b_len*/

    while ( in_i < in_b_len && out_i < out_b_len )
      {
        if ( in_b[in_i] == 0x80 )
          {/* one char */
            out_b[out_i++] = in_b[++in_i];
            ++in_i;
          }
        else if ( !in_b[in_i] )
          {/* several chars */
            int l = (int)in_b[++in_i]+1;
            ++in_i;
            while ( l-- )
              {
                out_b[out_i++] = in_b[in_i++];
              }
          }
        else
          {/* code */
            unsigned short code = (short)in_b[in_i]|((short)in_b[in_i+1] << 8);
            int l = code & 0x0f;
            int off = code >> 4;
            memcpy(out_b+out_i,out_b+out_i-off-JJLZ_MAX_LEN,l);
            out_i += l;
            in_i += 2;
          }
      }

    *inout_len = out_i;
    return out_b;
  }

"""

build_argv = """
#if defined _JUNGLE_ON_WINDOWS && defined _JUNGLE_WINDOWS_SUBSYSTEM

static void j_freeargv(char **vector)
  {
    char **scan;
    if (vector != NULL)
      {
        for (scan = vector; *scan != NULL; scan++) free (*scan);
        free (vector);
      }
  }

#define ISBLANK(a) ((a) == ' ' || (a) == '\t')
static char **j_buildargv(char *input, int *_argc)
  {

    enum {EOS=0,INITIAL_MAXARGC=128};

    char *arg;
    char *copybuf;
    int squote = 0;
    int dquote = 0;
    int bsquote = 0;
    int argc = 0;
    int maxargc = 0;
    char **argv = NULL;
    char **nargv;

    if (input != NULL)
      {
        copybuf = (char *) _alloca (strlen (input) + 1);
        /* Is a do{}while to always execute the loop once.  Always return an
           argv, even for null strings.  See NOTES above, test case below. */
        do
          {
            /* Pick off argv[argc] */
            while ( ISBLANK(*input) )
              {
                input++;
              }
            if ((maxargc == 0) || (argc >= (maxargc - 1)))
              {
                /* argv needs initialization, or expansion */
                if (argv == NULL)
                  {
                    maxargc = INITIAL_MAXARGC;
                    nargv = (char **) malloc (maxargc * sizeof (char *));
                  }
                else
                  {
                    maxargc *= 2;
                    nargv = (char **) realloc (argv, maxargc * sizeof (char *));
                  }
                if (nargv == NULL)
                  {
                    if (argv != NULL)
                      {
                        j_freeargv (argv);
                        argv = NULL;
                      }
                    break;
                  }
                argv = nargv;
                argv[argc] = NULL;
              }
            /* Begin scanning arg */
            arg = copybuf;
            while (*input != EOS)
              {
                if (ISBLANK (*input) && !squote && !dquote && !bsquote)
                  {
                    break;
                  }
                else
                  {
                    if (bsquote)
                      {
                        bsquote = 0;
                        *arg++ = *input;
                      }
                    else if (squote)
                      {
                        if (*input == '\\'') squote = 0;
                        else *arg++ = *input;
                      }
                    else if (dquote)
                      {
                        if (*input == '"') dquote = 0;
                        else *arg++ = *input;
                      }
                    else
                      {
                        if (*input == '\\'') squote = 1;
                        else if (*input == '"') dquote = 1;
                        else *arg++ = *input;
                      }
                    input++;
                  }
              }
            *arg = EOS;
            argv[argc] = strdup (copybuf);
            if (argv[argc] == NULL)
              {
                j_freeargv (argv);
                argv = NULL;
                break;
              }
            argc++;
            argv[argc] = NULL;

            while (ISBLANK (*input)) ++input;
          }
        while (*input != EOS);
      }
    *_argc = argc;
    return (argv);
  }

#endif
"""

try:
    Main(sys.argv[0],sys.argv[1:])
except ErrorMessageException:
    print 'failed with error: %s' % str(sys.exc_info()[1])
    sys.exit(-1)
