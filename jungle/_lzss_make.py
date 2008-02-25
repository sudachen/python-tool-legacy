import sys,os

print sys.prefix
print sys.version_info

if sys.platform == 'win32':
    os.system("cl -LD -MD -Ox _lzss.c -I%s\include %s\Libs\python%s%s.lib -Fe_lzss.pyd" %\
                ( sys.prefix, sys.prefix, sys.version_info[0], sys.version_info[1]))
else:
    os.system("gcc -shared -O2 _lzss.c -I /usr/include/python%s -o _lzss.so -lpython%s" %\
                ( sys.version[:3], sys.version[:3] ))
