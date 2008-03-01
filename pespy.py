
import sys, os, os.path, getopt
sys.path += [os.path.dirname(sys.argv[0])+'/lib']

from binutils import pecoff
import _udis86

def ProcessArguments(flags,argv):
    opts,args = getopt.getopt(argv,'',[])
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

def Main(script,argv):

    flags = {}

    args = ProcessArguments(flags,argv)
    if len(args) < 1:
        print_author()
        print_usage()
        sys.exit(0)

    pe_file_name = args[0]
    pe_entry = None
    i = pe_file_name.find('!')
    if i > 0:
        pe_entry = pe_file_name[i+1:]
        pe_file_name = pe_file_name[0:i]

    pef = pecoff.PEfile(pe_file_name)
    sects = pef.get_sections()
    pef.make_symbols_table()

    _udis86.setstyle('att')

    if pe_entry:
        addr = pef.find_symbol(pe_entry)
    else:
        pe_entry = '<entrypoint>'
        addr = pef.get_entry_point()

    sect, sec_offs = pef.find_section_and_offset(addr)
    start_pc = pef.get_imagebase() + sect.VirtualAddress + sec_offs
    #start_pc = sect.VirtualAddress + sec_offs

    print '{'+pe_entry+'}:'

    l,j,out_pc = _udis86.disasm_ptr(
        addr,
        start_pc,
        sects[0].SizeOfRawData-sec_offs,
        30)

    def reformat(x,p):
        x = x.split(' ')
        c = x[0]
        if p: c = c+'.'+p
        return '%-9s%s' % ( c, ' '.join(x[1:]) )

    m = marker_gen()
    j = [ (k[0],k[1],m.next()) for k in j]
    from_j = dict(map(lambda x: (x[0],(x[1],x[2])),j))
    to_j   = dict(map(lambda x: (x[1],(x[0],x[2])),j))

    for cmd_syn, pc, cmd_hex, cmd_len in l:
        jto = to_j.get(pc); pref_m = ' '
        jfr = from_j.get(pc); post_m = ''
        if jto: pref_m = '%s'%jto[1]
        if jfr:
            if jfr[0] >= start_pc and jfr[0] < out_pc:
                post_m = '%s'%jfr[1]
            else:
                post_m = '.%s'%jfr[1]
        s = '%08x|%-20s%2s|%-47s' %(pc,cmd_hex,pref_m,reformat(cmd_syn,post_m))
        print s
Main(sys.argv[0],sys.argv[1:])
