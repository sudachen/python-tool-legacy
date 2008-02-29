import sys,os

if sys.platform == 'win32':
    cmd_S = 'cl -nologo -Z7 -LD -MD -Ox _lzss.c -I"%s\\include" "%s\\Libs\\python%s%s.lib" -Fe"..\\..\\_lzss.pyd" -link -implib:"..\\..\\lib\\_lzss.lib" -debug -incremental:no -pdb:"..\\..\\_lzss.pdb" -export:init_lzss' %\
                ( sys.prefix, sys.prefix, sys.version_info[0], sys.version_info[1])
else:
    cmd_S = "gcc -shared -O2 _lzss.c -I /usr/include/python%s -o ../../_lzss.so -lpython%s" %\
                ( sys.version[:3], sys.version[:3] )

print cmd_S
os.system(cmd_S)
