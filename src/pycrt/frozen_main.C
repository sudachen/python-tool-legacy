#include <stdlib.h>
#include <malloc.h>
#include <string.h>

#if defined _WIN32 && !defined _PY2CC_STATIC
#define DLL_IMPORT __declspec(dllimport)
#else
#define DLL_IMPORT
#endif

/*extern struct _frozen _py2cc_Modules[];*/
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
        struct _frozen *i = (struct _frozen*)_py2cc_Modules;
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

#if defined _PY2CC_USE_RUNTIME
    Z_frozen = j_access_runtime(_PY2CC_USE_RUNTIME);

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

#if defined _PY2CC_ON_POSIX || defined _PY2CC_CONSOLE_SUBSYSTEM
int main(int argc,char **argv)
#elif defined _PY2CC_ON_WINDOWS && defined _PY2CC_WINDOWS_SUBSYSTEM
char *__stdcall GetCommandLineA();
int __stdcall WinMain(int _0,int _1,int _2,int _3)
#else
#error "unknown platform"
#endif
  {
    int sts = 0;
#if defined _PY2CC_ON_WINDOWS && defined _PY2CC_WINDOWS_SUBSYSTEM
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
