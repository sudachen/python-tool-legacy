import os,sys,os.path

files = \
('zl_adler32.c',
'zl_compress.c',
'zl_crc32.c',
'zl_deflate.c',
'zl_infblock.c',
'zl_infcodes.c',
'zl_inffast.c',
'zl_inflate.c',
'zl_inftrees.c',
'zl_infutil.c',
'zl_trees.c',
'zl_uncompr.c',
'zutil.c')

srcdir = os.path.join('..','..','Media','lib.z')
tmpdir = os.path.join('..','..','~temp~','media.zlib')

files = [ os.path.join(srcdir,i) for i in files ]

def c_compile(f):
  if not os.path.exists(tmpdir):
    os.makedirs(tmpdir)
  o_file = os.path.join(tmpdir,os.path.basename(f)[:-2] + '.obj')
  os.system('cl -c -MD -Ox -Fo"%s" "%s"'%(o_file,f))
  return o_file

objects = [c_compile(i) for i in files]
os.system('lib -out:z.lib ' + ' '.join(objects))
