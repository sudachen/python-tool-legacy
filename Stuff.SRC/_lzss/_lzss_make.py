import sys,os

print sys.prefix
print sys.version_info


if sys.platform == 'win32':
    cmd_S = 'cl -nologo -Z7 -LD -MD -Ox _lzss.c -I"%s\\include" "%s\\Libs\\python%s%s.lib" -Fe"..\\..\\bin\\_lzss.pyd" -link -implib:"..\\..\\lib\\_lzss.lib" -debug -incremental:no -pdb:"..\\..\\bin\\_lzss.pdb"' %\
                ( sys.prefix, sys.prefix, sys.version_info[0], sys.version_info[1])
else:
    cmd_S = "gcc -shared -O2 _lzss.c -I /usr/include/python%s -o ../../bin/_lzss.so -lpython%s" %\
                ( sys.version[:3], sys.version[:3] )

print cmd_S
os.system(cmd_S)
