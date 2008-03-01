import sys,os

if sys.platform == 'win32':
    cmd_S = 'cl -nologo -Z7 -LD -MD -Ox _udis86.c -I"%s\\include" "%s\\Libs\\python%s%s.lib" -Fe"..\\..\\_udis86.pyd" -link -implib:"..\\..\\lib\\_udis86.lib" -debug -incremental:no -pdb:"..\\..\\_udis86.pdb" -export:init_udis86 libudis86\udis86.lib' %\
                ( sys.prefix, sys.prefix, sys.version_info[0], sys.version_info[1])
else:
    cmd_S = "gcc -shared -O2 _udis86.c -I /usr/include/python%s -o ../../_udis86.so -lpython%s" %\
                ( sys.version[:3], sys.version[:3] )

print cmd_S
os.system(cmd_S)
