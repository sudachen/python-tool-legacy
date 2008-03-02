
import sys, os, os.path, getopt, binascii, re
sys.path += [os.path.dirname(os.path.abspath(sys.argv[0]))+'/lib']

from binutils import pecoff
from binutils import disasm

DEFAULT_LINES = 30
F_ABSOLUTE_ADDRESS      = 0
F_RELATED_TO_BASE       = 1
F_RELATED_TO_POINT      = 2
F_RELATED_TO_SECTION    = 3
F_RELATED_TO_FILE       = 4
F_NONE_ADDRESS          = 5
CMD_NONE                = 0
CMD_DISASSEMBLE         = 1
CMD_IMPORTS             = 2
CMD_IMPORTS_FUNCS       = 3
CMD_EXPORTS             = 4
flags = None

class Symbols:

    def __init__(self,pefile):
        self._syms = {}
        self._sym_by_address = {}
        self._sym_by_address[pefile.get_entry_point()] = 'ENTRYPOINT'
        for fn_name,addr in pefile.enumerate_exports():
            self._syms[fn_name] = addr
            self._sym_by_address[addr] = fn_name
        for dll_name,funcs in pefile.enumerate_imports():
            for fn_name,addr in funcs:
                self._syms[dll_name+'!'+fn_name] = addr
                self._sym_by_address[addr] = dll_name+'!'+fn_name

    def find_symbol(self,addr):
        return self._sym_by_address.get(addr,None)

    def find_symbol_address(self,sym):
        addr = None
        if not addr:
            addr = self._syms.get(sym)
        return addr

def safe_int(i,d):
    try:
        return int(i)
    except:
        return d

def process_arguments(argv):
    global flags
    flags = {
        'syntax':'att',
        'max-lines':DEFAULT_LINES,
        'skip-lines':0,
        'disasm-level':0,
        'disasm-addr-format':F_ABSOLUTE_ADDRESS,
        'command':CMD_NONE,
        }
    opts,args = getopt.getopt(argv,'L:F:O:H:',['intel','att'])
    for i,j in opts:
        if i == '--intel': flags['syntax'] = 'intel'
        if i == '--att': flags['syntax'] = 'att'

        if i == '-L':
            if j.startswith('r'):
                flags['disasm-level'] = 0
                j = j[1:]
            elif j.startswith('x'):
                flags['disasm-level'] = 1
                j = j[1:]
            else:
                flags['disasm-level'] = 2
            flags['max-lines'] = safe_int(j,DEFAULT_LINES)
            flags['command'] = CMD_DISASSEMBLE

        if i == '-F':
            for j in j:
                if j in ('a','A'):
                    flags['disasm-addr-format'] = F_ABSOLUTE_ADDRESS
                    if j == 'A': flags['disasm-no-addr'] = True
                elif j in ('b','B'):
                    flags['disasm-addr-format'] = F_RELATED_TO_BASE
                    if j == 'B': flags['disasm-no-addr'] = True
                elif j in ('p','P'):
                    flags['disasm-addr-format'] = F_RELATED_TO_POINT
                    if j == 'P': flags['disasm-no-addr'] = True
                elif j in ('s','S'):
                    flags['disasm-addr-format'] = F_RELATED_TO_SECTION
                    if j == 'S': flags['disasm-no-addr'] = True
                elif j in ('f','F'):
                    flags['disasm-addr-format'] = F_RELATED_TO_FILE
                    if j == 'F': flags['disasm-no-addr'] = True
                elif j == 'N':
                    flags['disasm-no-addr'] = True
                elif j == 'H':
                    flags['disasm-no-hex'] = True
                elif j == 'M':
                    flags['disasm-no-mark'] = True
                elif j == 'L':
                    flags['disasm-no-label'] = True

        if i == '-H':
            if j == 'i':
                flags['command'] = CMD_IMPORTS
            if j == 'I':
                flags['command'] = CMD_IMPORTS_FUNCS
            if j == 'e':
                flags['command'] = CMD_EXPORTS

    return args

def print_lines(l,skip=0):
    for i in l[skip:]:
        print i

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
    pefile = g.group(1)
    entry  = g.group(2)

    return (pefile,entry,offs)

def normalize_address(addr,pef):

    f = flags['disasm-addr-format']

    if f != F_ABSOLUTE_ADDRESS:

        sect,sec_offs = pef.find_section_and_offset(addr)

        if not sect:
            raise Exception('address %08x dose not belong to any PE section' % addr)


        if f == F_RELATED_TO_BASE:
            return addr-pef.get_image_base()
        elif f == F_RELATED_TO_SECTION:
            return sec_offs
        elif f == F_RELATED_TO_FILE:
            return sec_offs + sect.PointerToRawData

    return addr

def disasm_func(args):

    pe_file_name,entry,offs = parse_entry(args[0])
    pe_file_base_name = os.path.basename(pe_file_name)
    pef = pecoff.PEfile(pe_file_name)

    syms = Symbols(pef)

    def disassemble_at(entry,offset,lines=30,syntax='att',pef=pef,syms=syms):

        sects = pef.get_sections()

        if entry and entry != '~ENTRY' and entry != '*':
            if entry[0] in '0123456789':
                addr = try_treat_as_int(entry,16)
            elif entry == '~BASE' or entry[0] == '@':
                addr = pef.get_image_base()
            elif entry == '~FILE' or entry[0] == '%':
                addr = pef.addr_of_fOFFSET(offset)
                if addr == None:
                    raise Exception('offset %08x dose not belong to any PE section' % offset)
                offset = 0
            else:
                addr = syms.find_symbol_address(entry)
        else:
            if offset:
                addr = pef.get_image_base()
            else:
                addr = pef.get_entry_point()

        if not addr:
            raise Exception('bad entry')

        addr += offset
        sect,sec_offs = pef.find_section_and_offset(addr)

        if not sect:
            raise Exception('address %08x dose not belong to any PE section' % addr)

        start_pc = addr
        f = flags['disasm-addr-format']
        if f == F_RELATED_TO_BASE:
            start_pc = addr-pef.get_image_base()
        elif f == F_RELATED_TO_POINT:
            start_pc = 0
        elif f == F_RELATED_TO_SECTION:
            start_pc = sec_offs
        elif f == F_RELATED_TO_FILE:
            start_pc = sec_offs + sect.PointerToRawData

        addr = pef.fix_RVA(sect.VirtualAddress + sec_offs)

        l,out_pc = disasm.disasm_ptr(
            addr,
            start_pc,
            sects[0].SizeOfRawData-sec_offs,
            lines,
            syntax)

        return (l,start_pc,out_pc)

    def gen_comment(i,pef=pef,syms=syms):
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
        h = '%-18s' % hex_code
        if flags.get('disasm-no-hex'): h = ''
        if not flags.get('disasm-no-mark'):pref_m = '%2s '%pref_m
        else: pref_m = ''
        print '%s%s%s%-47s' %(a,h,pref_m,y)


def show_imports_funcs(args):
    mask = None
    pef = pecoff.PEfile(args[0])
    if len(args) > 1:
        mask = re.compile(args[1])
    for F,f in pef.enumerate_imports():
        b = False
        for n,a in f:
            nn = F+'!'+n
            if mask and not mask.search(nn):
                continue
            if not b:
                b = True
                #print '%s:'%F
            if flags.get('disasm-no-addr'):
                print nn
            else:
                print '%08x| %s'%(normalize_address(a,pef),nn)

def show_imports(args):
    pef = pecoff.PEfile(args[0])
    for F,f in pef.enumerate_imports():
        if flags.get('disasm-no-addr'):
            print '%s'%F
        else:
            a0 = normalize_address(f[0][1],pef)
            a1 = normalize_address(f[-1][1]+4,pef)
            print '%-16s (%08x .. %08x), %3d imports' %(F,a0,a1,len(f))

def show_exports(args):
    mask = None
    pef = pecoff.PEfile(args[0])
    if len(args) > 1:
        mask = re.compile(args[1])
    for n,a in pef.enumerate_exports():
        if mask and not mask.search(n):
            continue
        print '%08x| %s'%(normalize_address(a,pef),n)

def main(script,argv):

    args = process_arguments(argv)
    if len(args) < 1:
        print_author()
        print_usage()
        sys.exit(0)

    c = flags['command']
    if c == CMD_DISASSEMBLE:
        disasm_func(args)
    elif c == CMD_EXPORTS:
        show_exports(args)
    elif c == CMD_IMPORTS:
        show_imports(args)
    elif c == CMD_IMPORTS_FUNCS:
        show_imports_funcs(args)

main(sys.argv[0],sys.argv[1:])
