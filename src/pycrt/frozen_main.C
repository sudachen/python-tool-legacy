
#include<string.h>

#if defined _WIN32 
#define DLL_IMPORT __declspec(dllimport)
#endif

extern struct _frozen _Jungle_Modules[];
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
static char **j_buildargv(char const *input,int *count);

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
    mem = (struct _frozen *)malloc( 0, sizeof(struct _frozen)*(ftable_count+frozen_table_count+1) );
    memcpy( mem + (before?0:frozen_table_count), ftable, ftable_count*sizeof(struct _frozen));
    memcpy( mem + (!before?0:ftable_count), PyImport_FrozenModules, frozen_table_count*sizeof(struct _frozen));
    if ( frozen_table_mem ) free(frozen_table_mem);
    frozen_table_mem = mem;
    PyImport_FrozenModules = mem;
    frozen_table_count += ftable_count;
    memset( PyImport_FrozenModules + frozen_table_count, 0, sizeof(struct _frozen) );
  }

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
        PyImport_ImportFrozenModule("jungle_runtime_import_hook");
      }
#endif

    Py_FrozenFlag = 1; /* Suppress errors from getpath.c */
    Py_IgnoreEnvironmentFlag = 1;
    Py_OptimizeFlag = 3;
    Py_SetProgramName(argv[0]);
    Py_Initialize();
    PySys_SetArgv(argc,argv);
    n = PyImport_ImportFrozenModule("__main__");
    if (n == 0)
      Py_FatalError("__main__ not frozen");
    if (n < 0) 
      PyErr_Print();
    Py_Finalize();
    return n<0?-1:0;
  }

#if defined _JUNGLE_ON_POSIX || defined _JUNGLE_CONSOLE_SUBSYSTEM
int main(int argc,char **argv)
#elif defined _JUNGLE_ON_WINDOWS && defined _JUNGLE_WINDOWS_SUBSYSTEM
int __stdcall WinMain(int,int,int,int)
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
