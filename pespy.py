
import sys, os, os.path, getopt, binascii
sys.path += [os.path.dirname(os.path.abspath(sys.argv[0]))+'/lib']

from binutils import pecoff
from binutils import disasm

DEFAULT_LINES = 30

def safe_int(v,dV):
    try:
        return int(v)
    except:
        return dV

def process_arguments(argv):
    flags = {
        'syntax':'att',
        'max-lines':DEFAULT_LINES,
        'disasm-level':0,
        }
    opts,args = getopt.getopt(argv,'L:',['intel','att'])
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
    return (args,flags)

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

def parse_entry(src):
    pe_file = None
    entry   = None
    offs    = '0'
    skip    = '0'
    marks   = []
    i = src.find('!')
    if i>0:
        pe_file = src[:i]
        src = src[i+1:]
        i = src.find(',')
        if i > 0 :
            markers = src[i+1:].split(',')
            src = src[:i]
        i = src.find(':')
        if i > 0 :
            skip = src[i+1:]
            src = src[:i]
        i = src.find('+')
        if i > 0:
            offs = src[i+1:]
            src = src[:i]
        entry = src
    else:
        pe_file = src

    try:
        offs = int(offs)
    except:
        offs = 0

    try:
        skip = int(skip)
    except:
        skip = 0

    return (pe_file,entry,offs,skip,marks)

def disassemble_at(pef,entry,offset,lines=30,syntax='att'):
    sects = pef.get_sections()

    if entry and entry != '*':
        if entry[0] in '0123456789':
            if entry.startswith('0x'):
                addr = int(entry[2:],16)
            else:
                addr = int(entry,16)
            #addr = pef.fix_RVA(addr-pef.get_image_base())
        elif entry[0] == '#':
            addr = int(entry[1:],16) + pef.get_image_base()
        else:
            addr = pef.find_symbol_address(entry)
    else:
        addr = pef.get_entry_point()

    if not addr:
        raise Exception('bad entry')

    addr += offset
    sect,sec_offs = pef.find_section_and_offset(addr)
    start_pc = addr #pef.get_image_base() + sect.VirtualAddress + sec_offs
    addr = pef.fix_RVA(sect.VirtualAddress + sec_offs)

    l,out_pc = disasm.disasm_ptr(
        addr,
        start_pc,
        sects[0].SizeOfRawData-sec_offs,
        lines,
        syntax)

    return (l,start_pc,out_pc)

def gen_comment(pef,i):
    if i.operand:
        r = []
        for j in i.operand:
            s = None
            if j.oid == disasm.UD_OP_JIMM:
                s = pef.find_symbol(j.value + i.pc + i.ins_len)
            elif j.oid == disasm.UD_OP_MEM:
                s = pef.find_symbol(j.value)
            if s: r.append('%s'%s)
        if r:
            return ' ; '+','.join(r)
    return ''

def reformat(pef,i,p):
    x = i.ins_asm.split(' ')
    c = x[0]
    return '%-6s%3s%s%s' % ( c, p, ' '.join(x[1:]), gen_comment(pef,i) )

def main(script,argv):

    args,flags = process_arguments(argv)

    if len(args) < 1:
        print_author()
        print_usage()
        sys.exit(0)

    pe_file_name,entry,offs,skip,marks = parse_entry(args[0])
    pe_file_base_name = os.path.basename(pe_file_name)
    pef = pecoff.PEfile(pe_file_name)
    pef.make_symbols_table()

    l,start_pc,out_pc = disassemble_at(pef,entry,offs,flags['max-lines']+skip,flags['syntax'])
    if not entry or entry == '*': entry = '<entrypoint>'

    if len(l) > skip:
        l = l[skip:]
        start_pc = l[0].pc
    else:
        l = []

    #info = '{'+pe_file_base_name+'!'+entry+'}'
    #if skip: info = info + ':%d'%skip
    #print info

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
        jto = to_j.get(i.pc); pref_m = ' '
        jfr = from_j.get(i.pc); post_m = ''
        if jto: pref_m = '%s'%jto
        if jfr:
            if jfr >= start_pc and jfr < out_pc:
                post_m = '(%s)'%to_j[jfr]
            else:
                post_m = '<%s>'%to_j[jfr]
        hex_code = binascii.b2a_hex(i.ins_bytes)
        sym = pef.find_symbol(i.pc)
        if sym:
            print '--------{%s}%s' % (sym,'-'*(79-len(sym)-9))
        print '%08x|%-18s%2s %-47s' %(i.pc,hex_code,pref_m,reformat(pef,i,post_m))

main(sys.argv[0],sys.argv[1:])
