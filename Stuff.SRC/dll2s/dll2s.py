#!/usr/bin/python
# -*- coding: cp1251 -*-
#
# (c)2008, Alexey Sudachen, alexey@sudachen.name
# http://www.ethical-hacker.info/dll2c
#

version = "1.0"

import sys, os, os.path, getopt
import pefile


def print_author():
    print 'dll2s - .DLL to .S converter'
    print '(c)2008, Alexey Sudachen, alexey@sudachen.name'
    print 'http://www.ethical-hacker.info/dll2s'
    print '~\n'

def print_usage():
    print 'dll2s [flags] infile.DLL [outfile.S]'

def ProcessArguments(flags,argv):
    opts,args = getopt.getopt(argv,'',[])
    return args

def Main(script,argv):

    flags = {}

    if not argv:
        print_author()
        print_usage()
        sys.exit(0)
    else:
        args = ProcessArguments(flags,argv)

    if not flags.get('nologo'):
        print_author()

    ifile = open(args[0],"rb")
    if len(args) > 1 :
        ofile_name = args[1]
    else:
        ofile_name = os.path.splitext(args[0])[0] + '.S'
    ofile = open(ofile_name,"w+b")

    pef = pefile.PEfile(ifile)
    for sec in pef.Sections():
        if sec.characteristics & pefile.SCN_CNT_CODE:
            #code section
            ofile.write('section_%s:'%str(sec.virtual_address))
            sec_data = pef.ReadSectionData(sec)
            j = 0
            for i in range(len(sec_data)):
                if j % 20 == 0:
                    ofile.write('\n')
                    ofile.write('.byte ')
                else:
                    ofile.write(',')
                j += 1
                ofile.write('%d'%ord(sec_data[i]))

Main(sys.argv[0],sys.argv[1:])
