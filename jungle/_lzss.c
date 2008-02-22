
/*

  LZSS python module
  there is simple & dirty LZ77 implementation

  (c)2008, Alexey Sudachen, alexey@sudachen.name

 */

#include <Python.h>
#include <string.h>
#include <stdlib.h>

enum { 
  LZSS_MIN_LEN = 4, 
  LZSS_MAX_LEN = 15, 
  LZSS_TABLE_ROWS = 4, 
  LZSS_TABLE_MOD = 4096, 
  LZSS_TABLE_LEN = (LZSS_TABLE_MOD+1)*LZSS_TABLE_ROWS 
};

enum { PARENT, LEFT, RIGHT, NEXT };

static int lzss_cmp(char *a, char *b, int n)
  {
  }

static void lzss_delete_node(short *table, int n)
  {
    short r = table[0]*LZSS_TABLE_ROWS;
    int o = 0, n = (in_b % LZSS_TABLE_MOD) +1;

    if ( o = table[c+NEXT] )
      {
        int x = table[c+NEXT];
        table[x+LEFT]  = table[c+LEFT];
        table[x+RIGHT] = table[c+RIGHT];
        table[x+NEXT]  = table[c+NEXT];
        if ( table[x+LEFT] ) table[table[x+LEFT]+PARENT] = x;
        if ( table[x+RIGHT] ) table[table[x+RIGHT]+PARENT] = x;
      }

    if ( table[c+PARENT] )
      {
        l = table[c+PARENT];
        if ( o ) 
          {
            if ( table[l+LEFT] == c ) table[l+LEFT] = o;
            else table[l+RIGHT] = o;
          }
        else
          {
          }
      }
    else
      {
        // root
        accert(r == c);
        if ( o ) r = o;
        else if ( table[c+LEFT] ) // left
          {
            if ( table[c+RIGHT] ) 
              r = table[()?c+LEFT:c+RIGHT];
            else
              r = table[c+LEFT];
          }
        else
          r = table[c+RIGHT]; // right
        table[0] = r;
        table[r+PARENT] = 0; // root node has no parent
      }
  }

static int lzss_insert_node(short *table, int n, char *in_b, int l)
  {
    table[n+PARENT] = 0;
    table[n+LEFT] = 0;
    table[n+RIGHT] = 0;
    table[n+NEXT] = 0;

    /* add node */
    for(;;)
      {
        l = lzss_cmp(in_b,o,LZSS_MAX_LEN);
        if ( l > 0 )
          {
          }
        else if ( l < 0 )
          {
          }
        else
          {
            table[o+NEXT] = c;
            break;
          }
      }
  }

static int lzss_update_table(short *table, char *in_b, int in_i, int in_b_len)
  {
    int o = 0, n = (in_b % LZSS_TABLE_MOD) +1;
    short r = table[0]*LZSS_TABLE_ROWS;
    lzss_delete_node(table,n);
    return lzss_insert_node(table,n,in_b,LZSS_MAX_LEN);
  }

static PyObject *lzss_compress(PyObject *_0,PyObject *args)
  {
    char *in_b;
    int   in_b_len;
    if ( PyArg_ParseTuple(args,"s#",&in_b,&in_b_len) )
      {
        short *table = malloc(LZSS_TABLE_LEN*sizeof(short));
        int  out_b_len = in_b_len+4+2;
        unsigned char *out_b = malloc(out_b_len);
        int  out_i = 4, int_i = 0;
        unsigned char *cnt_p = 0;
        out_b[0] = in_b_len&0x0ff;
        out_b[1] = (in_b_len>>8)&0x0ff;
        out_b[2] = (in_b_len>>16)&0x0ff;
        out_b[3] = (in_b_len>>24)&0x0ff;
        memset(table,0,LZSS_TABLE_LEN*sizeof(short));
        table[0] = 1;
        out_b[out_i++] = 0;
        cnt_p = out_b;
        out_b[out_i++] = LZSS_MAX_LEN - 1;        
        memcpy(out_b+out_i,in_b,LZSS_MAX_LEN);
        while ( in_i != in_b_len && out_i+1 < out_b_len )
          {
            unsigned short code = lzss_update_table(table,in_b,in_i,in_b_len);
            if ( !code )
              {
                if ( !cnt_p || (!cnt_[-1] && *cnt_p == 255) ) 
                  {
                    out_b[out_i++] = 0x80;
                    *(cnt_p = out_b + out_i++) = in_b[in_i++];
                  }
                else
                  {
                    if ( cnt_p[-1] & 0x80 )
                      {
                        out_p[out_i++] = *cnt_p;
                        *cnt_p = cnt_p[-1] = 0;
                      }
                    ++*cnt_p;
                    out_b[out_i++] = in_b[in_i++];
                  }
              }
            else
              {
                cnt_p = 0;
                out_b[out_i++] = code&0x0ff;
                out_b[out_i++] = (code>>8)&0x0ff;
                in_i += code&0x0f;
              }
          }
        free(table);
        return PyString_FromStringAndSize(out_b,out_i);
      }
    return 0;
  }

static PyObject *lzss_decompress(PyObject *_0,PyObject *args)
  {
    return 0;
  }

static PyMethodDef lzss_funcs[] =
  {
    {"compress",lzss_compress,METH_VARARGS,0},
    {"decompress",lzss_decompress,METH_VARARGS,0},
    {0,0,0,0},
  };

void init_lzss()
  {
    Py_InitModule("_lzss", lzss_funcs);    
  }

#ifdef _LZSS_BUILD_TEST
int main()
  {
    printf("passed\n");
    return 0;
  }
#endif
