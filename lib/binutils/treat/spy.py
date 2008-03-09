# -*- coding: cp1251 -*-
"""
(c)2008 Alexey Sudachen, alexey@sudachen.name
http://www.ethical-hacker.info/

TREAT - The Reverse Engineering & Analizing Tool.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import sys, os, os.path, getopt, binascii, re
from binutils import disasm

from binutils.treat.const import *

class Bsection(object):

    __slots__ = ['flags','virtual_address','virtual_size','pointer_to_data','size_of_data','name']

    ACCESS_EXECUTE = 0x8
    ACCESS_WRITE   = 0x2
    ACCESS_XWRITE  = 0xa

    def __init__(self,flags,name,va,vsize,dta,dsize):
        self.virtual_address = va
        self.virtual_size = vsize
        self.pointer_to_data = dta
        self.size_of_data = dsize
        self.name = name
        self.flags = flags

    def __str__(self):
        return "SECTION{%s %8s %04x/%04x <= %04x/%04x}" % (
            self.access(), self.name,
            self.virtual_address,self.virtual_size,
            self.pointer_to_data,self.size_of_data)

    def access(self):
        x = self.flags & 0x0f
        if x == Bsection.ACCESS_WRITE:  return 'W'
        if x == Bsection.ACCESS_XWRITE: return 'X'
        if x == Bsection.ACCESS_EXECUTE:return 'E'
        return 'R'

class Bsymbol(object):

    __slots__ = ['address','name']

    def __init__(self,name,addr):
        self.name = name
        self.address = int(addr)

    def __str__(self):
        return 'SYMBOL{%s,%08x}' % (self.name,self.address)

class Bheader(object):

    pass

class Symbols(object):

    def __init__(self,bfile):

        self._syms = {}
        self._sym_by_address = {}
        self._sym_by_address[bfile.get_entry_point_va()] = 'ENTRYPOINT'

        for i in bfile.enumerate_symbols():
            self._syms[i.name] = i.address
            self._sym_by_address[i.address] = i.name

    def find_symbol(self,addr):
        return self._sym_by_address.get(addr,None)

    def find_symbol_address(self,sym):
        addr = None
        if not addr:
            addr = self._syms.get(sym)
        return addr


def marker_gen():
    for i in xrange(10):
        yield str(i)
    for i in xrange(ord('a'),ord('z')):
        yield chr(i)
    for i in xrange(ord('A'),ord('Z')):
        yield chr(i)
    raise Exception('out of marker range');

def try_treat_as_int(val,radix=10,default=0,msg=None):
    try:
        if val != None:
            if str(val).startswith('0x'):
                val = str(val)[2:]
                radix = 16
            return int(val,radix)
        else:
            return default
    except:
        if not msg:
            raise Exception("could not convert '%s' to integer"%str(val))
        else:
            raise Exception(msg)

def parse_entry(src):

    g = re.match('([^!]+)(?:!([^+-]+)?([+-]\\S+)?)?',src)

    if not g:
        raise Exception('failed to parse starting disassemble point')

    offs = try_treat_as_int(g.group(3),16,0)
    bfileile = g.group(1)
    entry  = g.group(2)

    return (bfileile,entry,offs)

def normalize_address(addr,bfile,flags):

    f = flags['disasm-addr-format']

    if f != F_ABSOLUTE_ADDRESS:

        sect,sec_offs = bfile.find_section_and_offset(addr)

        if not sect:
            raise Exception('address %08x dose not belong to any PE section' % addr)


        if f == F_RELATED_TO_BASE:
            return addr-bfile.get_image_base()
        elif f == F_RELATED_TO_SECTION:
            return sec_offs
        elif f == F_RELATED_TO_FILE:
            return sec_offs + sect.PointerToRawData

    return addr

def disasm_func(bfile,flags,args):

    entry = flags.get('disasm-entry',None)
    offs  = flags.get('disasm-offs',0)
    syms = Symbols(bfile)

    def disassemble_at(entry,offset,lines=30,syntax='att',bfile=bfile,syms=syms):

        if entry and entry != '~ENTRY' and entry != '*':
            if entry[0] in '0123456789':
                addr = try_treat_as_int(entry,16)
            elif entry == '~BASE' or entry[0] == '@':
                addr = bfile.get_image_base()
            elif entry == '~FILE' or entry[0] == '%':
                addr = bfile.get_mmap_offs(offset)
                if addr == None:
                    raise Exception('offset %08x dose not belong to any PE section' % offset)
                offset = 0
            else:
                addr = syms.find_symbol_address(entry)
        else:
            if offset:
                addr = bfile.get_image_base()
            else:
                addr = bfile.get_entry_point_va()

        if not addr:
            raise Exception('bad entry')

        addr += offset
        sect,sec_offs = bfile.find_section_and_offset(addr)

        if not sect:
            raise Exception('address %08x dose not belong to any PE section' % addr)

        start_pc = addr
        f = flags['disasm-addr-format']
        if f == F_RELATED_TO_BASE:
            start_pc = addr-bfile.get_image_base()
        elif f == F_RELATED_TO_POINT:
            start_pc = 0
        elif f == F_RELATED_TO_SECTION:
            start_pc = sec_offs
        elif f == F_RELATED_TO_FILE:
            start_pc = sec_offs + sect.pointer_to_data

        addr = bfile.get_mmap_rva(sect.virtual_address + sec_offs)

        l,out_pc = disasm.disasm_ptr(
            addr,
            start_pc,
            sect.size_of_data-sec_offs,
            lines,
            syntax)

        return (l,start_pc,out_pc)

    def gen_comment(i,bfile=bfile,syms=syms):

        if i.operand:
            r = []
            for j in i.operand:
                s = None
                if j.oid == disasm.UD_OP_JIMM:
                    s = syms.find_symbol(j.value + i.pc + i.ins_len)
                elif j.oid == disasm.UD_OP_MEM:
                    s = syms.find_symbol(j.value)
                if s: r.append('%s'%s)
            if r:
                return ' ; '+','.join(r)
        return ''

    skip = flags['skip-lines']
    l,start_pc,out_pc = disassemble_at(entry,offs,flags['max-lines']+skip,flags['syntax'])
    if not entry or entry == '*': entry = '<entrypoint>'

    if len(l) > skip:
        l = l[skip:]
        start_pc = l[0].pc
    else:
        l = []

    if flags['disasm-level'] < 2:
        ret_no = -1
        for i in range(len(l)):
            if l[i].mnemonic == disasm.UD_Iret:
                ret_no = i
                break
        if ret_no > 1:
            l = l[0:ret_no+1]
            out_pc = l[-1].pc + l[-1].ins_len

    m = marker_gen()
    from_j = {}
    to_j = {}
    for i in l:
        if ( i.mnemonic == disasm.UD_Icall or \
            ( i.mnemonic >= disasm.UD_Ijcxz and i.mnemonic <= disasm.UD_Ijnle )) and \
            i.operand[0].oid in (disasm.UD_OP_JIMM,): #disasm.UD_OP_MEM) :
            t_addr = i.pc + i.ins_len + i.operand[0].value
            idx = to_j.get(t_addr)
            if not idx:
                idx = m.next(); to_j[t_addr] = idx
            from_j[i.pc] = t_addr

    for i in l:
        pref_m = ''; post_m = ''
        if not flags.get('disasm-no-mark'):
            jto = to_j.get(i.pc); pref_m = ' '
            jfr = from_j.get(i.pc); post_m = ''
            if jto: pref_m = '%s'%jto
            if jfr:
                if jfr >= start_pc and jfr < out_pc:
                    post_m = '(%s)'%to_j[jfr]
                else:
                    post_m = '<%s>'%to_j[jfr]
        hex_code = binascii.b2a_hex(i.ins_bytes)
        sym = syms.find_symbol(i.pc)
        if sym and not flags.get('disasm-no-label'):
            print '--------{%s}%s' % (sym,'-'*(79-len(sym)-9))

        x = i.ins_asm.split(' '); c = x[0]
        y = '%-6s%3s%s%s' % ( c, post_m, ' '.join(x[1:]), gen_comment(i) )
        if flags.get('disasm-no-addr'):
            a = ''
        else:
            a = '%08x|'%i.pc
        h = '%-20s' % hex_code
        if flags.get('disasm-no-hex'): h = ''
        if not flags.get('disasm-no-mark'):pref_m = '%2s '%pref_m
        else: pref_m = ''
        print '%s%s%s%-47s' %(a,h,pref_m,y)


def show_imports_funcs(bfile,flags,args):

    mask = None
    if len(args) > 1:
        mask = re.compile(args[1],re.IGNORECASE)
    for sym in bfile.enumerate_imports():
        b = False
        if mask and not mask.search(sym.anme):
            continue
        if not b:
            b = True
            #print '%s:'%F
        if flags.get('disasm-no-addr'):
            print sym.name
        else:
            print '%08x| %s'%(normalize_address(sym.address,bfile,flags),sym.name)

def show_imports(bfile,flags,args):

    for F in bfile.enumerate_dependences():
        print '%s'%F

def show_exports(bfile,flags,args):

    mask = None
    if len(args) > 1:
        mask = re.compile(args[1],re.IGNORECASE)
    for s in bfile.enumerate_exports():
        if mask and not mask.search(n):
            continue
        print '%08x| %s'%(normalize_address(s.address,bfile,flags),s.name)

def show_quick_headers(bfile,flags,args):

    eps,epf = bfile.find_section_and_offset(bfile.get_entry_point_va())

    fields = bfile.fill_valuable_fields()

    sects = [
        (   i.access(),
            i.name,
            '%x(%x..%x)' % (i.virtual_address,
                i.virtual_address+bfile.get_image_base(),
                i.virtual_address+bfile.get_image_base()+i.virtual_size),
            '%x/%x' % (i.pointer_to_data,i.size_of_data) )
            for i in bfile.enumerate_sections()
        ]

    sects = map(lambda x: \
        ("%s %"+\
            str(max(map(lambda x:len(x[1]),sects)))\
            +"s: %"+\
            str(max(map(lambda x:len(x[2]),sects)))\
            +"s <= %s") %x, sects)

    imports = ['%s/%d' % (i[0].lower(),i[1]) for i in bfile.enumerate_dependences_and_count()]
    imports.sort()
    if len(imports) % 3: imports += ['']* (3-len(imports)%3)
    k = str(max(map(len,imports)))
    imports = [
        ("%-"+k+"s  %-"+k+"s  %s")%(imports[i],imports[i+1],imports[i+2])
        for i in range(0,len(imports),3) ]

    sects += ['----------------------------------------']
    sects += imports
    sects = ["starting at %08x ('%s'+%x)" % (bfile.get_image_base(),eps.name,epf),
             '----------------------------------------'] \
             + sects
    sects += ['----------------------------------------']
    sects += bfile.fill_specific_fields()

    def gen(x):
        for i in x: yield i
        while True: yield ''

    k = str(max(map(len,fields)))
    lgen = gen(fields); rgen = gen(sects)
    for i in range(max(len(sects),len(fields))):
        print ('%-'+k+'s | %s') % (lgen.next(),rgen.next())

def show_full_headers(bfile,flags,args):
    out = bfile.fill_full_headers()
    for i in out:
        print i

class FileSpy:

    def __init__(self,bfile):

        self._bfile = bfile

    def do_command(self,flags,args):

        c = flags['command']
        if c == CMD_DISASSEMBLE:
            disasm_func(self._bfile,flags,args)
        elif c == CMD_EXPORTS:
            show_exports(self._bfile,flags,args)
        elif c == CMD_IMPORTS:
            show_imports(self._bfile,flags,args)
        elif c == CMD_IMPORTS_FUNCS:
            show_imports_funcs(self._bfile,flags,args)
        elif c == CMD_QUICK_HEADERS:
            show_quick_headers(self._bfile,flags,args)
        elif c == CMD_FULL_HEADERS:
            show_full_headers(self._bfile,flags,args)

    def close(self):

        if self._bfile:
            self._bfile.close()
            self._bfile = None
