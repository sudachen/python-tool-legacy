
import struct

IMAGE_NUMBEROF_DIRECTORY_ENTRIES = 16
PE_SIZEOF_SECTION = 40

SCN_CNT_CODE = 0x00000020
SCN_CNT_INITIALIZED_DATA = 0x00000040
SCN_CNT_UNINITIALIZED_DATA = 0x00000080
SCN_MEM_EXECUTE = 0x20000000
SCN_MEM_READ = 0x40000000
SCN_MEM_WRITE = 0x80000000

class PEheader(object):

    class OptsHeader(object):

        __slots__ = [
            'magic', #w
            'major_linker_version', #b
            'minor_linker_version', #b
            'size_of_code', #i
            'size_of_initialized_data', #i
            'size_of_uninitialized_data', #i
            'address_of_entry_point', #i
            'base_of_code', #i
            'base_of_data', #i
            'image_base', #i
            'section_alignment', #i
            'file_alignment', #i
            'major_operating_system_version', #w
            'minor_operating_system_version', #w
            'major_image_version', #w
            'minor_image_version', #w
            'major_subsystem_version', #w
            'minor_subsystem_version', #w
            'win32_version_value', #i
            'size_of_image', #i
            'size_of_headers', #i
            'check_sum', #i
            'subsystem', #w
            'dll_characteristics', #w
            'size_of_stack_reserve', #i
            'size_of_stack_commit', #i
            'size_of_heap_reserve', #i
            'size_of_heap_commit', #i
            'loader_flags', #i
            'number_of_rva_and_sizes', #i
            'data_directory', # IMAGE_DATA_DIRECTORY/IMAGE_NUMBEROF_DIRECTORY_ENTRIES
            ]

        def __init__(self,ifile):
            self.magic,\
            self.major_linker_version,\
            self.minor_linker_version,\
            self.size_of_code,\
            self.size_of_initialized_data,\
            self.size_of_uninitialized_data,\
            self.address_of_entry_point,\
            self.base_of_code,\
            self.base_of_data,\
            self.image_base,\
            self.section_alignment,\
            self.file_alignment,\
            self.major_operating_system_version,\
            self.minor_operating_system_version,\
            self.major_image_version,\
            self.minor_image_version,\
            self.major_subsystem_version,\
            self.minor_subsystem_version,\
            self.win32_version_value,\
            self.size_of_image,\
            self.size_of_headers,\
            self.check_sum,\
            self.subsystem,\
            self.dll_characteristics,\
            self.size_of_stack_reserve,\
            self.size_of_stack_commit,\
            self.size_of_heap_reserve,\
            self.size_of_heap_commit,\
            self.loader_flags,\
            self.number_of_rva_and_sizes = \
                struct.unpack('HBBiiiiiiiiiHHHHHHiiiiHHiiiiii',ifile.read(96))
            self.data_directory = [
                struct.unpack('HH',ifile.read(4)) \
                for i in range(IMAGE_NUMBEROF_DIRECTORY_ENTRIES)]

    class ImageHeader(object):

        __slots__ = [
            'machine', #w
            'number_of_sections', #w
            'time_date_stamp', #i
            #i
            #i
            'size_of_optional_header', #w
            'characteristics', #w
            ]

        def __init__(self,ifile):

            self.machine,\
            self.number_of_sections,\
            self.time_date_stamp = struct.unpack('HHL',ifile.read(8))
            ifile.seek(8,1)
            self.size_of_optional_header,\
            self.characteristics = struct.unpack('HH',ifile.read(4))


    __slots__ = [
        'signature',
        'hfile',
        'hopts']

    def __init__(self,ifile,offs):
        ifile.seek(offs,0)
        self.signature = struct.unpack("L",ifile.read(4))[0]
        self.hfile = PEheader.ImageHeader(ifile)
        self.hopts = PEheader.OptsHeader(ifile)

class PEsection(object):
    __slots__ = [
        'name',  #8
        'virtual_size', #i
        'virtual_address', #i
        'size_of_raw_data', #i
        'pointer_to_raw_data', #i
        #'pointer_to_relocations', #i
        #'pointer_to_linenumbers', #i
        #'number_of_relocations', #w
        #'number_of_linenumbers', #w
        'characteristics', #i
    ]

    def __init__(self,ifile,offs):
        ifile.seek(offs,0)
        self.name,\
        self.virtual_size,\
        self.virtual_address,\
        self.size_of_raw_data,\
        self.pointer_to_raw_data = struct.unpack('8siiiL',ifile.read(8+16))
        ifile.seek(12,1)
        self.characteristics = struct.unpack('L',ifile.read(4))[0]
        #print "%s(%08x,%08x)" % (self.name,self.virtual_address,self.size_of_raw_data)

class PEfile:

    def __init__(self,ifile):

        self._ifile = ifile
        self._ifile.seek(0x3c,0)
        self._pe_offs = struct.unpack("i",self._ifile.read(4))[0]
        self._hdr    = PEheader(self._ifile,self._pe_offs)

        sects_offs = self._pe_offs + 24 + self._hdr.hfile.size_of_optional_header
        print sects_offs
        self._sects  = [ PEsection(self._ifile,sects_offs+i*PE_SIZEOF_SECTION) \
                 for i in range(self._hdr.hfile.number_of_sections) ]

    def Sections(self):
        return self._sects

    def ReadSectionData(self,sec):
        self._ifile.seek(sec.pointer_to_raw_data,0)
        return self._ifile.read(sec.size_of_raw_data)
