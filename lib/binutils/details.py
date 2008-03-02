# -*- coding: cp1251 -*-
"""

(c)2008, Alexey Sudachen, alexey@sudachen.name
http://www.ethical-hacker.info/

The part of binutils package

"""

import sys, os, os.path
import ctypes

if sys.platform == 'win32':

    FILE_SHARE_READ   = 0x00000001  
    FILE_SHARE_WRITE  = 0x00000002  
    FILE_SHARE_DELETE = 0x00000004  
    CREATE_NEW        = 1
    CREATE_ALWAYS     = 2
    OPEN_EXISTING     = 3
    OPEN_ALWAYS       = 4
    TRUNCATE_EXISTING = 5

    PAGE_NOACCESS          = 0x01     
    PAGE_READONLY          = 0x02     
    PAGE_READWRITE         = 0x04     
    PAGE_WRITECOPY         = 0x08     
    PAGE_EXECUTE           = 0x10     
    PAGE_EXECUTE_READ      = 0x20     
    PAGE_EXECUTE_READWRITE = 0x40     
    PAGE_EXECUTE_WRITECOPY = 0x80     
    PAGE_GUARD             = 0x100     
    PAGE_NOCACHE           = 0x200     
    PAGE_WRITECOMBINE      = 0x400     
    FILE_MAP_COPY          = 1
    FILE_MAP_WRITE         = 2
    FILE_MAP_READ          = 4
    FILE_MAP_EXECUTE       = 0x20
    GENERIC_READ           = 0x80000000
    GENERIC_WRITE          = 0x40000000
    GENERIC_EXECUTE        = 0x20000000
    GENERIC_ALL            = 0x10000000

    _k32 = ctypes.windll.kernel32

    def mmap_file(filename,offset=0,size=0,ro=True):
        hF = -1; hM = 0; a = 0 
        try:
            hF = _k32.CreateFileA(filename,\
                                      (GENERIC_READ,GENERIC_WRITE)[not ro],\
                                      FILE_SHARE_READ,0,\
                                      (OPEN_EXISTING,OPEN_ALWAYS)[not ro],\
                                      0,0)
            if hF == -1: raise Exception("failed to open file '%s'" % filename)
            hM = _k32.CreateFileMappingA(hF,0,(PAGE_READONLY,PAGE_READWRITE)[not ro],0,size,0)
            if not hM: raise Exception("failed to allocat mmap object for %d bytes of '%s'" % (size,filename))
            a  = _k32.MapViewOfFile(hM,(FILE_MAP_READ,FILE_MAP_READ|FILE_MAP_WRITE)[not ro],0,offset,size)
            if not a: raise Exception("failed to mmap %d bytes from %d of '%s'" % (size,offset,filename))
            return a
        finally:
            if hF != -1: _k32.CloseHandle(hF)
            if hM : _k32.CloseHandle(hM)
            
    def unmmap_file(address):
        if address:
            _k32.UnmapViewOfFile(address)
