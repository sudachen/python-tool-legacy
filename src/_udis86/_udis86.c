/*

  UDIS86 frontend

  (c)2008, Alexey Sudachen, alexey@sudachen.name

 */

#include <Python.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include "udis86.h"

#define C_STATIC static

void (*ud86_syntax)(ud_t*) = UD_SYN_ATT;

typedef struct UDO {
  ud_t u;
  unsigned char *p;
  unsigned char *pE;
} UDO;

C_STATIC PyObject *udis86_setstyle(PyObject *_,PyObject *args)
  { // style='intel','att'
    char *style =0;
    if ( PyArg_ParseTuple(args,"s",&style) )
      {
        if ( 0 == strcmp(style,"intel") ) 
          ud86_syntax = UD_SYN_INTEL;
        if ( 0 == strcmp(style,"att") ) 
          ud86_syntax = UD_SYN_ATT;
        Py_INCREF(Py_None);
        return Py_None;        
      }
    return 0;
  }

C_STATIC int udis86_input_hook(ud_t *udo)
  {
    if ( ((UDO*)udo)->p != ((UDO*)udo)->pE )
      return *((UDO*)udo)->p++;
    else 
      return UD_EOI;
  }

C_STATIC PyObject *udis86_disasmem_S(char *address, int pc, int area_size, int max_command_count)
  { /* ( [(command,pc,hex,len)], [(pc,to)] ) */
    UDO udo; 
    PyObject *pcmds = PyList_New(0);
    PyObject *pjmps = PyList_New(0);
    PyObject *pret  = PyTuple_New(3);
    int count = 0, out_pc = pc;
    udo.p = address; udo.pE = udo.p + area_size;
    ud_init(&udo.u);
    ud_set_mode(&udo.u,32);
    ud_set_syntax(&udo.u,ud86_syntax);
    ud_set_input_hook(&udo.u, udis86_input_hook);
    ud_set_pc(&udo.u, pc);
    PyTuple_SET_ITEM(pret,0,pcmds);
    PyTuple_SET_ITEM(pret,1,pjmps);
    for ( ; count < max_command_count && ud_disassemble(&udo.u) ; ++count )
      {
        PyObject *t = PyTuple_New(4);
        PyTuple_SET_ITEM(t,0,PyString_FromString(ud_insn_asm(&udo.u)));
        PyTuple_SET_ITEM(t,1,PyInt_FromLong(ud_insn_off(&udo.u)));
        PyTuple_SET_ITEM(t,2,PyString_FromString(udo.u.insn_hexcode));
        PyTuple_SET_ITEM(t,3,PyInt_FromLong(ud_insn_len(&udo.u)));
        PyList_Append(pcmds,t);
        Py_DECREF(t);
        out_pc = ud_insn_off(&udo.u)+ud_insn_len(&udo.u);
        if ( (UD_Icall == udo.u.mnemonic || 
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
          }
      }    
    PyTuple_SET_ITEM(pret,2,PyInt_FromLong(out_pc));
    return pret;
  }

C_STATIC PyObject *udis86_disasmem_ptr(PyObject *_,PyObject *args)
  { 
    char *p = 0;
    int  pc = 0, area_size, max_command_count;    
    if ( PyArg_ParseTuple(args,"iiii|i",&p,&pc,&area_size,&max_command_count/*,&process_handle*/) )
      {
        return udis86_disasmem_S(p,pc,area_size,max_command_count);
      }
    return 0;
  }

C_STATIC PyObject *udis86_disasmem_str(PyObject *_,PyObject *args)
  { 
    char *p = 0;
    int  pc = 0, area_size, max_command_count;    
    if ( PyArg_ParseTuple(args,"s#iii",&p,&area_size,&pc,&max_command_count) )
      {
        return udis86_disasmem_S(p,pc,area_size,max_command_count);
      }
    return 0;
  }

C_STATIC PyMethodDef udis86_funcs[] =
  {
    {"setstyle",udis86_setstyle,METH_VARARGS,0},
    {"disasm_ptr",udis86_disasmem_ptr,METH_VARARGS,0},
    {"disasm_str",udis86_disasmem_str,METH_VARARGS,0},
    {0,0,0,0},
  };

void init_udis86()
  {
    Py_InitModule("_udis86", udis86_funcs);
  }
