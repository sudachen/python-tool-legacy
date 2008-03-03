
import sys, stat, getopt, os, os.path

compiled = False

try:
    import _pycrt
    compiled =  _pycrt.compiled
except:
    import warnings
    import encodings
    from encodings import aliases, ascii, base64_codec, charmap, cp1251, cp1252, cp866
    from encodings import hex_codec, iso8859_5, koi8_r, koi8_u, latin_1
    from encodings import mbcs, raw_unicode_escape, undefined, unicode_escape, unicode_internal
    from encodings import utf_16, utf_16_be, utf_16_le, utf_7, utf_8, uu_codec

if not compiled:
    sys.path += ['../../lib','../..']

import pespy
pespy.main(sys.argv[0],sys.argv[1:])
