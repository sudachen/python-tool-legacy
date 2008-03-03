# -*- coding: cp1251 -*-
"""

(c)2008, Alexey Sudachen, alexey@sudachen.name
http://www.ethical-hacker.info/

The part of binutils package

Microsoft PE/COFF structures
"""
import sys, os, os.path
from binutils.ctypes import Structure,Union,sizeof,c_char,c_byte,c_char_p,c_long,POINTER, cast
from binutils.ctypes.wintypes import *

import details

IMAGE_DOS_SIGNATURE = 0x5A4D      # MZ
IMAGE_OS2_SIGNATURE = 0x454E      # NE
IMAGE_OS2_SIGNATURE_LE = 0x454C   # LE
IMAGE_VXD_SIGNATURE = 0x454C      # LE
IMAGE_NT_SIGNATURE  = 0x00004550  # PE00

class IMAGE_DOS_HEADER(Structure):
    _fields_ = [
        ('e_magic',WORD),
        ('e_cblp',WORD),
        ('e_cp',WORD),
        ('e_crlc',WORD),
        ('e_cparhdr',WORD),
        ('e_minalloc',WORD),
        ('e_maxalloc',WORD),
        ('e_ss',WORD),
        ('e_sp',WORD),
        ('e_csum',WORD),
        ('e_ip',WORD),
        ('e_cs',WORD),
        ('e_lfarlc',WORD),
        ('e_ovno',WORD),
        ('e_res',WORD*4),
        ('e_oemid',WORD),
        ('e_oeminfo',WORD),
        ('e_res2',WORD*10),
        ('e_lfanew',LONG),
        ]

IMAGE_SIZEOF_DOS_HEADER = 64

class IMAGE_FILE_HEADER(Structure):
    _fields_ = [
        ('Machine',WORD),
        ('NumberOfSections',WORD),
        ('TimeDateStamp',DWORD),
        ('PointerToSymbolTable',DWORD),
        ('NumberOfSymbols',DWORD),
        ('SizeOfOptionalHeader',WORD),
        ('Characteristics',WORD),
        ]

IMAGE_SIZEOF_FILE_HEADER    = 20

image_file_carhs_values = [
    ('IMAGE_FILE_RELOCS_STRIPPED'           ,0x0001),  # Relocation info stripped from file.
    ('IMAGE_FILE_EXECUTABLE_IMAGE'          ,0x0002),  # File is executable  (i.e. no unresolved externel references),.
    ('IMAGE_FILE_LINE_NUMS_STRIPPED'        ,0x0004),  # Line nunbers stripped from file.
    ('IMAGE_FILE_LOCAL_SYMS_STRIPPED'       ,0x0008),  # Local symbols stripped from file.
    ('IMAGE_FILE_AGGRESIVE_WS_TRIM'         ,0x0010),  # Agressively trim working set
    ('IMAGE_FILE_LARGE_ADDRESS_AWARE'       ,0x0020),  # App can handle >2gb addresses
    ('IMAGE_FILE_BYTES_REVERSED_LO'         ,0x0080),  # Bytes of machine word are reversed.
    ('IMAGE_FILE_32BIT_MACHINE'             ,0x0100),  # 32 bit word machine.
    ('IMAGE_FILE_DEBUG_STRIPPED'            ,0x0200),  # Debugging info stripped from file in .DBG file
    ('IMAGE_FILE_REMOVABLE_RUN_FROM_SWAP'   ,0x0400),  # If Image is on removable media, copy and run from the swap file.
    ('IMAGE_FILE_NET_RUN_FROM_SWAP'         ,0x0800),  # If Image is on Net, copy and run from the swap file.
    ('IMAGE_FILE_SYSTEM'                    ,0x1000),  # System File.
    ('IMAGE_FILE_DLL'                       ,0x2000),  # File is a DLL.
    ('IMAGE_FILE_UP_SYSTEM_ONLY'            ,0x4000),  # File should only be run on a UP machine
    ('IMAGE_FILE_BYTES_REVERSED_HI'         ,0x8000),  # Bytes of machine word are reversed.
    ]
image_file_carhs_map = dict( map( lambda x: (x[1],x[0]), image_file_carhs_values) )
for i,j in image_file_carhs_values: globals()[i] = j

image_file_machine_values = [
    ('IMAGE_FILE_MACHINE_UNKNOWN'           , 0),
    ('IMAGE_FILE_MACHINE_I386'              , 0x014c),  # Intel 386.
    ('IMAGE_FILE_MACHINE_R3000'             , 0x0162),  # MIPS little-endian, 0x160 big-endian
    ('IMAGE_FILE_MACHINE_R4000'             , 0x0166),  # MIPS little-endian
    ('IMAGE_FILE_MACHINE_R10000'            , 0x0168),  # MIPS little-endian
    ('IMAGE_FILE_MACHINE_WCEMIPSV2'         , 0x0169),  # MIPS little-endian WCE v2
    ('IMAGE_FILE_MACHINE_ALPHA'             , 0x0184),  # Alpha_AXP
    ('IMAGE_FILE_MACHINE_SH3'               , 0x01a2),  # SH3 little-endian
    ('IMAGE_FILE_MACHINE_SH3DSP'            , 0x01a3),
    ('IMAGE_FILE_MACHINE_SH3E'              , 0x01a4),  # SH3E little-endian
    ('IMAGE_FILE_MACHINE_SH4'               , 0x01a6),  # SH4 little-endian
    ('IMAGE_FILE_MACHINE_SH5'               , 0x01a8),  # SH5
    ('IMAGE_FILE_MACHINE_ARM'               , 0x01c0),  # ARM Little-Endian
    ('IMAGE_FILE_MACHINE_THUMB'             , 0x01c2),
    ('IMAGE_FILE_MACHINE_AM33'              , 0x01d3),
    ('IMAGE_FILE_MACHINE_POWERPC'           , 0x01F0),  # IBM PowerPC Little-Endian
    ('IMAGE_FILE_MACHINE_POWERPCFP'         , 0x01f1),
    ('IMAGE_FILE_MACHINE_IA64'              , 0x0200),  # Intel 64
    ('IMAGE_FILE_MACHINE_MIPS16'            , 0x0266),  # MIPS
    ('IMAGE_FILE_MACHINE_ALPHA64'           , 0x0284),  # ALPHA64
    ('IMAGE_FILE_MACHINE_MIPSFPU'           , 0x0366),  # MIPS
    ('IMAGE_FILE_MACHINE_MIPSFPU16'         , 0x0466),  # MIPS
    ('IMAGE_FILE_MACHINE_AXP64'             , 0x0284),  # IMAGE_FILE_MACHINE_ALPHA64
    ('IMAGE_FILE_MACHINE_TRICORE'           , 0x0520),  # Infineon
    ('IMAGE_FILE_MACHINE_CEF'               , 0x0CEF),
    ('IMAGE_FILE_MACHINE_EBC'               , 0x0EBC),  # EFI Byte Code
    ('IMAGE_FILE_MACHINE_AMD64'             , 0x8664),  # AMD64 (K8),
    ('IMAGE_FILE_MACHINE_M32R'              , 0x9041),  # M32R little-endian
    ('IMAGE_FILE_MACHINE_CEE'               , 0xC0EE),
    ]
image_file_machine_map = dict( map( lambda x: (x[1],x[0]), image_file_machine_values) )
for i,j in image_file_machine_values: globals()[i] = j

class IMAGE_DATA_DIRECTORY(Structure):
    _fields_ = [
        ('VirtualAddress',DWORD),
        ('Size',DWORD),
        ]

IMAGE_NUMBEROF_DIRECTORY_ENTRIES = 16

image_dictionary_names_values = [
    ('IMAGE_DIRECTORY_ENTRY_EXPORT',        0),
    ('IMAGE_DIRECTORY_ENTRY_IMPORT',        1),
    ('IMAGE_DIRECTORY_ENTRY_RESOURCE',      2),
    ('IMAGE_DIRECTORY_ENTRY_EXCEPTION',     3),
    ('IMAGE_DIRECTORY_ENTRY_SECURITY',      4),
    ('IMAGE_DIRECTORY_ENTRY_BASERELOC',     5),
    ('IMAGE_DIRECTORY_ENTRY_DEBUG',         6),
    ('IMAGE_DIRECTORY_ENTRY_COPYRIGHT',     7),
    ('IMAGE_DIRECTORY_ENTRY_GLOBALPTR',     8),
    ('IMAGE_DIRECTORY_ENTRY_TLS',           9),
    ('IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG',   10),
    ('IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT',  11),
    ('IMAGE_DIRECTORY_ENTRY_IAT',           12),
    ('IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT',  13),
    ('IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR',14),
    ('IMAGE_DIRECTORY_ENTRY_RESERVED',      15),
    ]

image_dictionary_names_map = dict( map( lambda x: (x[1],x[0]), image_dictionary_names_values ) )
for i,j in image_dictionary_names_values: globals()[i] = j

class IMAGE_OPTIONAL_HEADER(Structure):
    _fields_ = [
        # Standard fields.
        ('Magic',WORD),
        ('MajorLinkerVersion',BYTE),
        ('MinorLinkerVersion',BYTE),
        ('SizeOfCode',DWORD),
        ('SizeOfInitializedData',DWORD),
        ('SizeOfUninitializedData',DWORD),
        ('AddressOfEntryPoint',DWORD),
        ('BaseOfCode',DWORD),
        ('BaseOfData',DWORD),
        # NT additional fields.
        ('ImageBase',DWORD),
        ('SectionAlignment',DWORD),
        ('FileAlignment',DWORD),
        ('MajorOperatingSystemVersion',WORD),
        ('MinorOperatingSystemVersion',WORD),
        ('MajorImageVersion',WORD),
        ('MinorImageVersion',WORD),
        ('MajorSubsystemVersion',WORD),
        ('MinorSubsystemVersion',WORD),
        ('Win32VersionValue',DWORD),
        ('SizeOfImage',DWORD),
        ('SizeOfHeaders',DWORD),
        ('CheckSum',DWORD),
        ('Subsystem',WORD),
        ('DllCharacteristics',WORD),
        ('SizeOfStackReserve',DWORD),
        ('SizeOfStackCommit',DWORD),
        ('SizeOfHeapReserve',DWORD),
        ('SizeOfHeapCommit',DWORD),
        ('LoaderFlags',DWORD),
        ('NumberOfRvaAndSizes',DWORD),
        ('DataDirectory',IMAGE_DATA_DIRECTORY*IMAGE_NUMBEROF_DIRECTORY_ENTRIES),
        ]

class IMAGE_NT_HEADERS(Structure):
    _fields_ = [
        ('Signature',DWORD),
        ('FileHeader',IMAGE_FILE_HEADER),
        ('OptionalHeader',IMAGE_OPTIONAL_HEADER),
    ]

IMAGE_SIZEOF_SHORT_NAME = 8

class IMAGE_SECTION_HEADER(Structure):
    _fields_ = [
        ('Name',c_char*IMAGE_SIZEOF_SHORT_NAME),
        ('VirtualSize',DWORD),
        ('VirtualAddress',DWORD),
        ('SizeOfRawData',DWORD),
        ('PointerToRawData',DWORD),
        ('PointerToRelocations',DWORD),
        ('PointerToLinenumbers',DWORD),
        ('NumberOfRelocations',WORD),
        ('NumberOfLinenumbers',WORD),
        ('Characteristics',DWORD),
    ]

class IMAGE_EXPORT_DIRECTORY(Structure):
    _fields_ = [
        ('Characteristics',DWORD),
        ('TimeDateStamp',DWORD),
        ('MajorVersion',WORD),
        ('MinorVersion',WORD),
        ('Name',DWORD),
        ('Base',DWORD),
        ('NumberOfFunctions',DWORD),
        ('NumberOfNames',DWORD),
        ('AddressOfFunctions',DWORD),     # RVA from base of image
        ('AddressOfNames',DWORD),         # RVA from base of image
        ('AddressOfNameOrdinals',DWORD),  # RVA from base of image
    ]

class IMAGE_IMPORT_BY_NAME(Structure):
    _fields_ = [
        ('Hint',WORD),
        ('Name',c_char*256)
    ]


class IMAGE_THUNK_DATA(Union):
    _fields_ = [
        ('ForwarderString', DWORD),
        ('Function',DWORD),
        ('Ordinal',DWORD),
        ('AddressOfData',DWORD),
    ]

class IMAGE_IMPORT_DESCRIPTOR(Structure):
    _fields_ = [
        ('OriginalFirstThunk',DWORD),
        ('TimeDateStamp',DWORD),
        ('ForwarderChain',DWORD),
        ('Name',DWORD),
        ('FirstThunk',DWORD),
    ]

class PEfile(object):

    def __init__(self,fname):
        mem = 0
        try:
            mem = details.mmap_file(fname)
            dsh = IMAGE_DOS_HEADER.from_address(mem)
            if dsh.e_magic != IMAGE_DOS_SIGNATURE: raise Exception('file is not DOS/PE image')
            nth = IMAGE_NT_HEADERS.from_address(mem+dsh.e_lfanew)
            if nth.Signature != IMAGE_NT_SIGNATURE: raise Exception('file is not PE image')
            self._basemem = mem
            self.dos_header = dsh
            self.nt_headers = nth
        except:
            if mem:
                details.unmmap_file(mem)
            raise

    def close(self):
        if self._basemem:
            details.unmmap_file(self._basename)
            self._basename = 0
            self.nt_headers = None
            self.dos_header = None

    def find_section_by_RVA(self,rva):
        for sect in self.get_sections():
            if rva >= sect.VirtualAddress and rva < sect.VirtualAddress+max(sect.VirtualSize,sect.SizeOfRawData):
                return sect
        return None

    def fix_RVA(self,rva):
        sec = self.find_section_by_RVA(rva)
        if sec:
            return self._basemem + (rva - sec.VirtualAddress + sec.PointerToRawData)
        raise Exception('failed to fixup RVA %08x' % rva)

    def get_base_address(self):
        return self._basemem

    def get_first_section_offset(self):
        return self.dos_header.e_lfanew + 4 + \
            sizeof(IMAGE_FILE_HEADER) + \
            self.nt_headers.FileHeader.SizeOfOptionalHeader

    def get_sections(self):
        return (IMAGE_SECTION_HEADER*self.nt_headers.FileHeader.NumberOfSections).\
            from_address(self._basemem + self.get_first_section_offset())

    def get_section_data_address(self,no):
        return self._basemem+self.get_sections()[no].PointerToRawData

    def get_section_data(self,no):
        sect = self.get_sections()
        return (c_byte*sect[no].SizeOfRawData).from_address(self._basemem+sect[no].PointerToRawData)

    def get_exports(self):
        exports_rva = self.nt_headers.OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress
        if exports_rva:
            exports = self.fix_RVA(exports_rva)
            return IMAGE_EXPORT_DIRECTORY.from_address(exports)
        return None

    def enumerate_exports(self):
        exports = self.get_exports()
        if exports and exports.NumberOfNames:
            names = (DWORD*exports.NumberOfNames).from_address(self.fix_RVA(exports.AddressOfNames))
            funcs = (DWORD*exports.NumberOfFunctions).from_address(self.fix_RVA(exports.AddressOfFunctions))
            ords  = (WORD*exports.NumberOfNames).from_address(self.fix_RVA(exports.AddressOfNameOrdinals))
            for i in range(exports.NumberOfNames):
                yield ((c_char*256).from_address(self.fix_RVA(names[i])).value,\
                       funcs[ords[i]]+self.get_image_base())
                       #self.fix_RVA(funcs[ords[i]]))

    def get_imports(self):
        l = []
        imports_rva = self.nt_headers.OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress
        if imports_rva:
            p = self.fix_RVA(imports_rva)
            i = IMAGE_IMPORT_DESCRIPTOR.from_address(p)
            while i.FirstThunk and i.Name:
                name = c_char_p(self.fix_RVA(i.Name)).value
                j = i.OriginalFirstThunk
                if not j: j = i.FirstThunk
                l.append( (name, self.fix_RVA(j), self.get_image_base()+i.FirstThunk) )
                p += sizeof(IMAGE_IMPORT_DESCRIPTOR)
                i = IMAGE_IMPORT_DESCRIPTOR.from_address(p)
        return l

    def enumerate_imports(self):
        l = []
        imports = self.get_imports()
        for n,p,f in imports:
            lf = []
            n = os.path.splitext(n)[0]
            p = cast(p,POINTER(DWORD)); i = 0
            while p[i]:
                a = p[i]
                if a & 0x80000000:
                    lf.append(('#%d'%(a&0x0ffff),i*4+f))
                else:
                    a = cast(self.fix_RVA(a)+2,c_char_p)
                    lf.append((a.value,i*4+f))
                i += 1
            l.append((n,lf))
        return l

    def get_entry_point(self):
        return self.get_image_base()+self.nt_headers.OptionalHeader.AddressOfEntryPoint

    def get_image_base(self):
        return self.nt_headers.OptionalHeader.ImageBase

    def find_section_and_offset(self,addr):
        return self.find_section_and_offset_by_RVA(addr-self.get_image_base())

    def addr_of_fOFFSET(self,p):
        for sect in self.get_sections():
            if p >= sect.PointerToRawData and p < sect.PointerToRawData+sect.SizeOfRawData:
                return (p-sect.PointerToRawData)+sect.VirtualAddress+self.get_image_base()
        return None

    def find_section_and_offset_by_mem(self,addr):
        p = addr-self._basemem
        for sect in self.get_sections():
            if p >= sect.PointerToRawData and p < sect.PointerToRawData+sect.SizeOfRawData:
                return (sect,p-sect.PointerToRawData)
        return (None,addr)

    def find_section_and_offset_by_RVA(self,rva):
        sect = self.find_section_by_RVA(rva)
        if sect:
            return (sect,rva-sect.VirtualAddress)
        return (None,rva)

    #
    # header printing
    #

    def fetch_nt_sections(self):
        s = self.get_first_section_offset()
        sect = self.get_sections()
        return [
            (s + no*sizeof(IMAGE_SECTION_HEADER),
             sect[no].Name,
             sect[no].Characteristics,
             #"",
             sect[no].VirtualAddress, sect[no].VirtualSize,
             sect[no].PointerToRawData, sect[no].SizeOfRawData,
            ) for no in range(self.nt_headers.FileHeader.NumberOfSections)]

    def print_nt_sections(self,out=None):
        if not out: out = sys.stdout
        for i in self.fetch_nt_sections():
            out.write('+%03x: %-8s %08x %08x(%08x) <= %08x(%08x)\n' %i)

    def fetch_nt_headers(self):
        l = []; s = self.dos_header.e_lfanew
        l.append((s,'Signature',self.nt_headers.Signature))
        s += 2
        for i,j in IMAGE_FILE_HEADER._fields_:
            k = getattr(self.nt_headers.FileHeader,i)
            l.append((s,i,k))
            s += sizeof(j)
        for i,j in IMAGE_OPTIONAL_HEADER._fields_:
            if not i in ('DataDirectory',):
                k = getattr(self.nt_headers.OptionalHeader,i)
                l.append((s,i,k))
            s += sizeof(j)
        return l

    def print_nt_headers(self,out=None):
        if not out: out = sys.stdout
        for i in self.fetch_nt_headers():
            out.write('+%03x: %-38s = %08x\n' % i)

    def fetch_nt_directory(self):
        s = self.dos_header.e_lfanew + sizeof(IMAGE_NT_HEADERS) - IMAGE_NUMBEROF_DIRECTORY_ENTRIES*8
        return [
            ( s + i*8,
              image_dictionary_names_map[i],
              self.nt_headers.OptionalHeader.DataDirectory[i].VirtualAddress,
              self.nt_headers.OptionalHeader.DataDirectory[i].Size)
            for i in range(IMAGE_NUMBEROF_DIRECTORY_ENTRIES)]

    def print_nt_directory(self,out=None):
        if not out: out = sys.stdout
        for i in self.fetch_nt_directory():
            out.write('+%03x: %-38s = %08x,%08x\n' % i)

    def fetch_dos_header(self):
        l = []; s = 0
        for i,j in IMAGE_DOS_HEADER._fields_:
            if not i in ('e_res','e_res2'):
                k = getattr(self.dos_header,i)
                l.append((s,i,k))
            s += sizeof(j)
        return l

    def print_dos_header(self,out=None):
        if not out: out = sys.stdout
        for i in self.fetch_dos_header():
            out.write('+%03x: %-38s = %08x\n' % i)

    def print_headers(self,out=None):
        if not out: out = sys.stdout
        out.write('-- DOS HEADER --\n')
        self.print_dos_header(out)
        out.write('-- NT HEADERS --\n')
        self.print_nt_headers(out)
        out.write('-- DIRECTORY --\n')
        self.print_nt_directory(out)
        out.write('-- SECTIONS --\n')
        self.print_nt_sections(out)
