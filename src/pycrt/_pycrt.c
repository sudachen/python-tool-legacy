#include <Python.h>
#define C_STATIC static

C_STATIC PyMethodDef pycrt_funcs[] =
  {
    {0,0,0,0},
  };

void init_pycrt()
  {
    PyObject *m;
    m = Py_InitModule("_pycrt", pycrt_funcs);
    PyModule_AddObject(m,"compiled",Py_True);
    Py_INCREF(Py_True);
  }
