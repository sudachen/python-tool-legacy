/* Module configuration */

/* This file contains the table of built-in modules.
   See init_builtin() in import.c. */

#include "Python.h"

extern void initarray(void);
extern void initaudioop(void);
extern void initbinascii(void);
extern void initcmath(void);
extern void initerrno(void);
extern void initgc(void);
extern void initimageop(void);
extern void initmath(void);
extern void initmd5(void);
extern void initoperator(void);
extern void initrgbimg(void);
extern void initsignal(void);
extern void initsha(void);
extern void initstrop(void);
extern void initstruct(void);
extern void inittime(void);
extern void initthread(void);
extern void initcStringIO(void);
extern void initcPickle(void);
extern void initmsvcrt(void);
extern void init_locale(void);
extern void init_codecs(void);
extern void init_weakref(void);
extern void init_hotshot(void);
extern void initxxsubtype(void);
extern void initzipimport(void);
extern void init_random(void);
extern void inititertools(void);
extern void initcollections(void);
extern void init_heapq(void);
extern void init_bisect(void);
extern void init_symtable(void);
extern void initmmap(void);
extern void init_csv(void);
extern void init_sre(void);
extern void initparser(void);
extern void init_winreg(void);
extern void initdatetime(void);
extern void init_multibytecodec(void);
extern void init_codecs_cn(void);
extern void init_codecs_hk(void);
extern void init_codecs_iso2022(void);
extern void init_codecs_jp(void);
extern void init_codecs_kr(void);
extern void init_codecs_tw(void);
extern void init_subprocess(void);
extern void PyMarshal_Init(void);
extern void initimp(void);
extern void initpyteggo2(void);
extern void initzlib(void);
extern void initpyexpat(void);
extern void init_socket(void);
extern void initselect(void);
extern void initunicodedata(void);
extern void init_lzss(void);
extern void init_ctypes(void);
extern void init_udis86(void);
extern void init_pycrt(void);
extern void initposix(void);
extern void initnt(void);

struct _inittab _PyImport_Inittab[] = {
        {"__pycrt",      init_pycrt},
        {"_lzss",       init_lzss},
        {"_ctypes",     init_ctypes},
        {"_udis86",     init_udis86},
        {"zlib",        initzlib},
        {"pyexpat",     initpyexpat},
        {"array",       initarray},
        {"_socket",     init_socket},
        {"_ssl",        0},
        {"select",      initselect},
        {"binascii",    initbinascii},
        {"cmath",       initcmath},
        {"errno",       initerrno},
        {"gc",          initgc},
        {"math",        initmath},
        {"md5",         initmd5},
        {"operator",    initoperator},
        {"signal",      initsignal},
        {"sha",         initsha},
        {"strop",       initstrop},
        {"struct",      initstruct},
        {"time",        inittime},
        {"cStringIO",   initcStringIO},
        {"cPickle",     initcPickle},
        {"_codecs",     init_codecs},
        {"_weakref",    init_weakref},
        {"_hotshot",    init_hotshot},
        {"_random",     init_random},
        {"_bisect",     init_bisect},
        {"_heapq",      init_heapq},
        {"itertools",   inititertools},
        {"collections", initcollections},
        {"_symtable",   init_symtable},
        {"mmap",        initmmap},
        {"_sre",        init_sre},
        {"parser",      initparser},
        {"datetime",    initdatetime},
        {"xxsubtype",   initxxsubtype},
        {"zipimport",   initzipimport},
        {"marshal",     PyMarshal_Init},
        {"imp",         initimp},
        {"__main__",    0},
        {"__builtin__", 0},
        {"sys",         0},
        {"exceptions",  0},
#ifdef WITH_THREAD
        {"thread",      initthread},
#endif
#ifdef WIN32
        {"nt",          initnt},
        {"msvcrt",      initmsvcrt},
        {"_locale",     init_locale},
        {"_winreg",     init_winreg},
        {"_subprocess", init_subprocess},
#else
        {"posix",       initposix},
#endif
        {0, 0}
};
