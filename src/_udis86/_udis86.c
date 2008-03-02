/*

  UDIS86 frontend

  (c)2008, Alexey Sudachen, alexey@sudachen.name

 */

#include <Python.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include "udis86.h"

#define C_STATIC /*static*/

typedef void (*ud86_syntax_t)(ud_t*);


typedef struct UDO
  {
    ud_t u;
    unsigned char *p;
    unsigned char *pE;
  } UDO;


C_STATIC ud86_syntax_t convert_to_style(char *style)
  { // style='intel','att'
    if ( 0 == stricmp(style,"intel") )
      return UD_SYN_INTEL;
    if ( 0 == stricmp(style,"att") )
      return UD_SYN_ATT;

    return UD_SYN_ATT;
  }

C_STATIC int udis86_input_hook(ud_t *udo)
  {
    if ( ((UDO*)udo)->p != ((UDO*)udo)->pE )
      return *((UDO*)udo)->p++;
    else
      return UD_EOI;
  }

C_STATIC PyObject *udis86_disasmem_S(char *address, int pc, int area_size, int max_command_count, ud86_syntax_t syntax)
  { /* returns [instructions] */
    UDO udo;
    PyObject *plst  = 0;
    PyObject *x86_ins_class = 0;
    PyObject *x86_opd_class = 0;
    PyObject *o = 0, *oo = 0;
    int count = 0, out_pc = pc;

    udo.p = address; udo.pE = udo.p + area_size;
    ud_init(&udo.u);
    ud_set_mode(&udo.u,32);
    ud_set_syntax(&udo.u,syntax);
    ud_set_input_hook(&udo.u, udis86_input_hook);
    ud_set_pc(&udo.u, pc);

    o = PyImport_ImportModule("binutils.disasm");
    if ( !o )
      {
        PyErr_SetString(PyExc_Exception,"failed to mport binutils.disasm");
        return 0;
      }

    x86_ins_class = PyDict_GetItemString(PyModule_GetDict(o),"x86_Instruction");
    x86_opd_class = PyDict_GetItemString(PyModule_GetDict(o),"x86_Operand");
    Py_DECREF(o);

    if ( !x86_ins_class || !x86_opd_class )
      {
        PyErr_SetString(PyExc_Exception,"binutils.disasm should has x86_Instruction and x86_Operand classes");
        return 0;
      }

    plst = PyList_New(0);
    oo = PyTuple_New(0);

    for ( ; count < max_command_count && ud_disassemble(&udo.u) ; ++count )
      {
        PyObject *ins = PyObject_Call(x86_ins_class,oo,0);
        struct ud_operand *opnds = udo.u.operand;
        int i,j,
          opd_n =
            (opnds[2].type!=UD_NONE?1:0) +
            (opnds[1].type!=UD_NONE?1:0) +
            (opnds[0].type!=UD_NONE?1:0);
        if ( opd_n )
          {
            o = PyTuple_New(opd_n);
            for ( i = 0, j = 0; i < 3; ++i )
              if ( opnds[i].type!=UD_NONE )
                {
                  PyObject *vals = 0;
                  if ( opnds[i].size == 8 )
                    vals = Py_BuildValue("(ii)",opnds[i].type,opnds[i].lval.sbyte);
                  else if ( opnds[i].size == 16 )
                    vals = Py_BuildValue("(ii)",opnds[i].type,opnds[i].lval.sword);
                  else
                    vals = Py_BuildValue("(ii)",opnds[i].type,opnds[i].lval.sdword);
                  PyTuple_SET_ITEM(o,j++,PyObject_Call(x86_opd_class,vals,0));
                  Py_DECREF(vals);
                  /*PyObject *p = PyObject_Call(x86_opd_class,oo,0);
                  PyObject *o0 = PyInt_FromLong(opnds[i].type);
                  PyObject_SetAttrString(p,"oid",o0); Py_DECREF(o0);
                  o0 = PyInt_FromLong(opnds[i].lval.sdword);
                  PyObject_SetAttrString(p,"value",o0); Py_DECREF(o0);
                  PyTuple_SET_ITEM(o,j++,p);*/
                }
          }
        else
          { o = Py_None; Py_INCREF(o); }

        PyObject_SetAttrString(ins,"operand",o); Py_DECREF(o);

        o = PyString_FromString(ud_insn_asm(&udo.u));
        PyObject_SetAttrString(ins,"ins_asm",o); Py_DECREF(o);

        o = PyInt_FromLong(ud_insn_off(&udo.u));
        PyObject_SetAttrString(ins,"pc",o); Py_DECREF(o);

        o = PyInt_FromLong(ud_insn_len(&udo.u));
        PyObject_SetAttrString(ins,"ins_len",o); Py_DECREF(o);

        o = PyInt_FromLong(udo.u.mnemonic);
        PyObject_SetAttrString(ins,"mnemonic",o); Py_DECREF(o);

        o = PyString_FromStringAndSize(address + (ud_insn_off(&udo.u) - pc), ud_insn_len(&udo.u));
        PyObject_SetAttrString(ins,"ins_bytes",o); Py_DECREF(o);

        PyList_Append(plst,ins);
        Py_DECREF(ins);

        out_pc = ud_insn_off(&udo.u)+ud_insn_len(&udo.u);
        /*if ( (UD_Icall == udo.u.mnemonic ||
              ( udo.u.mnemonic >= UD_Ijcxz && udo.u.mnemonic <= UD_Ijnle )) &&
             ((UD_OP_JIMM == udo.u.operand[0].type) ||
              (UD_OP_MEM == udo.u.operand[0].type)))
          {
            PyObject *t = PyTuple_New(2);
            PyTuple_SET_ITEM(t,0,PyInt_FromLong(ud_insn_off(&udo.u)));
            //PyTuple_SET_ITEM(t,0,PyInt_FromLong(count));
            PyTuple_SET_ITEM(t,1,PyInt_FromLong(ud_insn_off(&udo.u)+ud_insn_len(&udo.u)+udo.u.operand[0].lval.sdword));
            PyList_Append(pjmps,t);
            Py_DECREF(t);
          }*/
      }

    Py_DECREF(oo);
    o = PyTuple_New(2);
    PyTuple_SET_ITEM(o,0,plst);
    PyTuple_SET_ITEM(o,1,PyInt_FromLong(out_pc));
    return o;
  }

C_STATIC PyObject *udis86_disasmem_ptr(PyObject *_,PyObject *args)
  {
    char *p = 0, *style = 0;
    int  pc = 0, area_size, max_command_count;
    if ( PyArg_ParseTuple(args,"iiii|s",&p,&pc,&area_size,&max_command_count,&style) )
      {
        ud86_syntax_t syntax = UD_SYN_ATT;
        if ( style ) syntax = convert_to_style(style);
        return udis86_disasmem_S(p,pc,area_size,max_command_count,syntax);
      }
    return 0;
  }

C_STATIC PyObject *udis86_disasmem_str(PyObject *_,PyObject *args)
  {
    char *p = 0, *style = 0;
    int  pc = 0, area_size, max_command_count;
    if ( PyArg_ParseTuple(args,"s#iii|s",&p,&area_size,&pc,&max_command_count,&style) )
      {
        ud86_syntax_t syntax = UD_SYN_ATT;
        if ( style ) syntax = convert_to_style(style);
        return udis86_disasmem_S(p,pc,area_size,max_command_count,syntax);
      }
    return 0;
  }

C_STATIC PyMethodDef udis86_funcs[] =
  {
    {"disasm_ptr",udis86_disasmem_ptr,METH_VARARGS,0},
    {"disasm_str",udis86_disasmem_str,METH_VARARGS,0},
    {0,0,0,0},
  };

void init_udis86()
  {
    Py_InitModule("_udis86", udis86_funcs);
  }
