# -*- coding: cp1251 -*-
"""

(c)2008, Alexey Sudachen, alexey@sudachen.name
http://www.ethical-hacker.info/

"""

import os, os.path, sys, getopt, stat

global_flags_set = {
    'CXX_FLAGS':[],
    'CXX_DEBUG_FLAGS':[],
    'CXX_RELEASE_FLAGS':[],
    'CC_FLAGS':[],
    'CC_DEBUG_FLAGS':[],
    'CC_RELEASE_FLAGS':[],
    'C_FLAGS':[],
    'C_DEBUG_FLAGS':[],
    'C_RELEASE_FLAGS':[],
    'LINK_FLAGS':[],
    'LINK_DEBUG_FLAGS':[],
    'LINK_RELEASE_FLAGS':[],
    'LIB_FLAGS':[],
    'LIB_DEBUG_FLAGS':[],
    'LIB_RELEASE_FLAGS':[],
    'RC_FLAGS':[],
    'RC_DEBUG_FLAGS':[],
    'RC_RELEASE_FLAGS':[],
    'S_FLAGS':[],
    'S_DEBUG_FLAGS':[],
    'S_RELEASE_FLAGS':[],
    }

global_build_type = 'RELEASE'
global_build_config = 'DEFAULT'
global_build_operation = 'BUILD'
global_j_vals = {}
global_verbose = False

if sys.platform == 'win32':
    global_tool_set = 'msc'
else:
    global_tool_set = 'gnu'

def set_msc_tool():
    global global_tool_set
    global_tool_set = 'msc'
def set_gnu_tool():
    global global_tool_set
    global_tool_set = 'gnu'

def process_command_line():
    opts,args = getopt.getopt(sys.argv[1:],"vhj:",[])

    global global_build_type
    global global_build_config
    global global_build_operation
    global global_verbose

    if args:
        if not args[0].lower() in ('release','debug','build','rebuild','clean'):
            global_build_config = args[0].upper()
            print 'setting build config to %s' %global_build_config
            args = args[1:]
    if args:
        if args[0].lower() in ('release','debug'):
            global_build_type = args[0].upper()
            print 'setting build type to %s' %global_build_type
            args = args[1:]

    if args:
        if args[0].lower() in ('build','rebuild','clean'):
            global_build_operation = args[0].upper()
            print 'setting build operation to %s' %global_build_operation
            args = args[1:]

    for i,j in opts:
        if i == '-j':
            val = True
            k = j.find('=')
            if k>0:
                val = j[k+1:]
                j = j[:k]
            global_j_vals[j] = val
        if i == '-v':
            global_verbose = True

def get_build_type():
    return global_build_type.lower()

def get_build_config():
    return global_build_config.lower()

def set_build_type(build_type):
    global global_build_type
    build_type = build_type.upper()
    if not build_type in ('RELEASE','DEBUG'):
        raise Exception('invalid build type, should be RELEASE or DEBUG')
    global_build_type = build_type

def set_build_config(build_config):
    global global_build_config
    global_build_config = build_config.upper()

def _select_flags_with_build_type(prefix):
    return global_flags_set[prefix+global_build_type+'_FLAGS']

def _fake_build_rule(source,*a):
    return source

def _need_to_build(source,target):
    fmtime_O = None
    if os.path.exists(target):
        fmtime_O = os.stat(target)[stat.ST_MTIME]
        fmtime_I = os.stat(source)[stat.ST_MTIME]
    return fmtime_O == None or fmtime_O < fmtime_I

def doi_build_it():
    return global_build_operation == 'BUILD'

def doi_need_2build_s2t(source,target):
    return global_build_operation == 'BUILD' and _need_to_build(source,target)

def doi_clean_it():
    return global_build_operation == 'CLEAN'

def doi_need_clean(target):
    return global_build_operation == 'CLEAN' and os.path.exists(target)

def try_clean_target(target):
    if global_build_operation == 'CLEAN':
        if os.path.exists(target):
            if global_verbose: print 'unlink "%s"' % target
            os.unlink(target)

def try_compile(source,target,flags,format):
    if global_build_operation == 'BUILD':
        if _need_to_build(source,target):
            cmd_S = format % (' '.join(flags),target,source)
            if global_verbose: print cmd_S
            e = os.system(cmd_S)
            if e != 0 :
                raise Exception('failed to compile: %s'%source)
        return True

def _ms_cl_compile_file(source,target,flags):
    if not try_compile(source,target,flags,'cl %s -c -Fo"%s" %s'):
        try_clean_target(target)

def _gnu_cc_compile_file(source,target,flags,tool):
    if not try_compile(source,target,flags,tool+' %s -c -o"%s" %s'):
        try_clean_target(target)

def _cc_build_rule(source,target,flags,deps):
    rel_flags = flags + global_flags_set['C_FLAGS'] + global_flags_set['CC_FLAGS'] \
        + _select_flags_with_build_type('C_') \
        + _select_flags_with_build_type('CC_')
    if global_tool_set == 'msc':
        _ms_cl_compile_file(source,target,rel_flags)
    else:
        _gnu_cc_compile_file(source,target,rel_flags,'gcc')
    return target

def _cxx_build_rule(source,target,flags,deps):
    rel_flags = flags + global_flags_set['C_FLAGS'] + global_flags_set['CXX_FLAGS'] \
        + _select_flags_with_build_type('C_') \
        + _select_flags_with_build_type('CXX_')
    if global_tool_set == 'msc':
        _ms_cl_compile_file(source,target,rel_flags)
    else:
        _gnu_cc_compile_file(source,target,rel_flags,'g++')
    return target

def _rc_build_rule(source,target,flags,deps):
    rel_flags = global_flags_set['RC_FLAGS'] + _select_flags_with_build_type('RC_') + flags
    if global_build_operation == 'BUILD':
        if _need_to_build(source,target):
            if global_tool_set == 'msc':
                cmd_S = 'rc %s -fo"%s" %s' % (' '.join(rel_flags),target,source)
            else:
                cmd_S = 'windres %s -Ocoff "%s" "%s"' % (' '.join(rel_flags),source,target)
            if global_verbose: print cmd_S
            e = os.system(cmd_S)
            if e != 0 :
                raise Exception('failed to RC build: %s'%source)
    else:
        try_clean_target(target)
    return target

def _S_build_rule(source,target,flags,deps):
    rel_flags = global_flags_set['S_FLAGS'] + _select_flags_with_build_type('S_') + flags
    if global_build_operation == 'BUILD':
        if _need_to_build(source,target):
            cmd_S = 'as %s -o"%s" %s' % (' '.join(rel_flags),target,source)
            if global_verbose: print cmd_S
            e = os.system(cmd_S)
            if e != 0 :
                raise Exception('failed to GAS build: %s'%source)
    else:
        try_clean_target(target)
    return target

global_tool_types = {
    'msc':{
        'c-file':{
            'maker':_cc_build_rule,
            'object-ext':'.obj','source_exts':['.c']},
        'c++-file':{
            'maker':_cxx_build_rule,
            'object-ext':'.obj','source_exts':['.C','.cpp','.c++','.cc']},
        'o-file':{
            'maker':_fake_build_rule,
            'object-ext':'.obj','source_exts':['.obj','.o']},
        'lib-file':{
            'maker':_fake_build_rule,
            'object-ext':'.lib','source_exts':['.lib']},
        'rc-file':{
            'maker':_rc_build_rule,
            'object-ext':'.res','source_exts':['.rc','.RC','.Rc']},
        's-file':{
            'maker':_S_build_rule,
            'object-ext':'.obj','source_exts':['.S','.s']},
        },
    'gnu':{
        'c-file':{
            'maker':_cc_build_rule,
            'object-ext':'.o','source_exts':['.c']},
        'c++-file':{
            'maker':_cxx_build_rule,
            'object-ext':'.o','source_exts':['.C','.cpp','.c++','.cc']},
        'o-file':{
            'maker':_fake_build_rule,
            'object-ext':'.o','source_exts':['.obj','.o']},
        'lib-file':{
            'maker':_fake_build_rule,
            'object-ext':'.a','source_exts':['.lib']},
        'rc-file':{
            'maker':_rc_build_rule,
            'object-ext':'.o','source_exts':['.rc','.RC','.Rc']},
        's-file':{
            'maker':_cc_build_rule,
            'object-ext':'.o','source_exts':['.S','.s']},
        }
    }

global_ext_map = {'msc':{},'gnu':{}}

for t in ('msc','gnu'):
    for i,j in global_tool_types[t].items():
        for k in j['source_exts']:
            global_ext_map[t][k] = i

def select_tool_type(ext):
    file_type = global_ext_map[global_tool_set].get(ext)
    if file_type:
        return global_tool_types[global_tool_set][file_type]
    return None

def _normalize_source_tuple(indata,base_dir,resolve_deps):
    if type(indata) == type(''):
        indata = [indata,[],[]]
    source = indata[0]
    flags  = indata[1]
    deps   = indata[2]
    if base_dir and base_dir != '.':
        if not os.path.isabs(source):
            source = os.path.join(base_dir,source)
    target,ext = os.path.splitext(source)
    target = os.path.normpath(target).replace('..'+os.sep,'@').replace(os.sep,'#')
    tool_type = select_tool_type(ext)
    target = target + tool_type['object-ext']
    if global_tool_set != 'msc' and sys.platform == 'win32':
        target = target.replace('\\','/')
        source = source.replace('\\','/')
    return (source,flags,deps,target,tool_type['maker'])

def normolize_sources(sources,basedir,resolve_deps=(False,[])):
    """sources - list of sources or tuples(source,[flags],[deps])
       basedir - base for relative soruce paths
       resolve_deps - tule(on/of,[exlude paths])
       flags_set - set of flags for building tools"""
    return [_normalize_source_tuple(i,basedir,resolve_deps) for i in sources]

def compile_files(sources,tempdir,com_flags=[]):
    objects = []
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
    for source_data in sources:
        if type(source_data) == type('') or len(source_data) < 4:
            source_data = _normalize_source_tuple(source_data,'.',(None,[]))
        source,flags,deps,target,tool = source_data
        target = os.path.join(tempdir,target)
        if global_tool_set != 'msc' and sys.platform == 'win32':
            target = target.replace('\\','/')
        objects.append(tool(source,target,com_flags+flags,deps))
    return objects

def _make_objects_list(objects,libs,tempdir,objectslist):
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
    if os.path.exists(objectslist):
        os.unlink(objectslist)
    f = open(objectslist,"w+t")
    fmtime = 0
    for i in objects:
        f.write('"'+i+'"\n')
        fmtime = max(os.stat(i)[stat.ST_MTIME],fmtime)
    for i in libs:
        f.write('"'+i+'"\n');
        if os.path.exists(i):
            fmtime = max(os.stat(i)[stat.ST_MTIME],fmtime)
    f.close()
    return fmtime

def _msc_link_file(objects,libs,tempdir,target,flags,cmd):
    if global_build_operation == 'BUILD':
        objectslist = os.path.join(tempdir,"~objectslist~")
        fmtime = _make_objects_list(objects,libs,tempdir,objectslist)
        if not os.path.exists(target) or fmtime > os.stat(target)[stat.ST_MTIME]:
            if os.path.exists(target): os.unlink(target)
            cmd_S = (cmd+' -out:"%s" '%target)+' '.join(flags)+(' @"%s"'%objectslist)
            if global_verbose: print cmd_S
            if 0 != os.system( cmd_S ):
                raise Exception('failed to link "%s"'%target)
    else:
        try_clean_target(target)

def quote(i):
    if sys.platform == 'win32':
        return i
    else:
        return i.replace('~','\\~').replace(' ','\\ ').replace('@','\\@').replace('#','\\#')

def _gnu_link_file(objects,libs,tempdir,target,flags):
    if global_build_operation == 'BUILD':
        #if len(objects) > 1:
        #    build_a = os.path.join(tempdir,'@@build@@.a')
        #    _gnu_lib_file(objects[1:],[],tempdir,build_a,[])
        #else:
        #    build_a = ''
        #fmtime = os.stat(build_a)[stat.ST_MTIME]
        objectslist = os.path.join(tempdir,"~objectslist~")
        fmtime = _make_objects_list(objects,libs,tempdir,objectslist)
        if not os.path.exists(target) or fmtime > os.stat(target)[stat.ST_MTIME]:
            #cmd_S = ('gcc -o%s '%target)+' '.join(flags)+' '+objects[0]+' '+build_a
            cmd_S = ('ld -o%s '%target)+' '.join(flags)+' @%s'%objectslist
            if global_verbose: print cmd_S
            if 0 != os.system( cmd_S ):
                raise Exception('failed to link "%s"'%target)
    else:
        try_clean_target(target)

def _gnu_lib_file(objects,libs,tempdir,target,flags):
    if global_build_operation == 'BUILD':
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)
        l = []
        fmtime = 0
        for i in objects:
            l.append(i)
            fmtime = max(os.stat(i)[stat.ST_MTIME],fmtime)
        for i in libs:
            l.append(i)
            if os.path.exists(i):
                fmtime = max(os.stat(i)[stat.ST_MTIME],fmtime)
        if not os.path.exists(target) or fmtime > os.stat(target)[stat.ST_MTIME]:
            if os.path.exists(target):
                os.unlink(target)
            for i in l:
                cmd_S = 'ar qf %s %s'%(target,quote(i))
                if global_verbose: print cmd_S
                if 0 != os.system( cmd_S ):
                    if os.path.exists(target):
                        os.unlink(target)
                    raise Exception('failed to link "%s"'%target)
            os.system( 'ranlib %s'%target )
    else:
        try_clean_target(target)

def link_static(objects,tempdir,target,flags=[]):
    rel_flags = flags + global_flags_set['LIB_FLAGS'] + _select_flags_with_build_type('LIB_')
    if global_tool_set == 'msc':
        _msc_link_file(objects,[],tempdir,target,rel_flags,'lib')
    else:
        _gnu_lib_file(objects,[],tempdir,target,rel_flags)

def link_shared(objects,libs,tempdir,target,flags=[]):
    rel_flags = flags + global_flags_set['LINK_FLAGS'] + _select_flags_with_build_type('LINK_')
    if global_tool_set == 'msc':
        _msc_link_file(objects,libs,tempdir,target,['-dll']+rel_flags,'link')
    else:
        _gnu_link_file(objects,libs,tempdir,target,['-shared']+rel_flags)

def link_executable(objects,libs,tempdir,target,flags=[]):
    rel_flags = flags + global_flags_set['LINK_FLAGS'] + _select_flags_with_build_type('LINK_')
    if global_tool_set == 'msc':
        _msc_link_file(objects,libs,tempdir,target,rel_flags,'link')
    else:
        _gnu_link_file(objects,libs,tempdir,target,rel_flags)

def get_jVal(name):
    return global_j_vals.get(name,None)

def do_safexec(cmd):
    if global_verbose: print cmd
    if 0 != os.system( cmd ):
        raise Exception('failed with "%s"'%cmd)

def add_global_flags_for_msvc(**k):

    global_flags_set['C_FLAGS'] += ['-DWIN32','-D_WINDOWS','-D_WIN32_WINNT="0x0500"']

    if global_build_type == 'RELEASE':
        global_flags_set['C_FLAGS'] += ['-Ox', '-Os', '-Oi', '-Ob2', '-Oy-', '-Gy', '-GF']
    else:
        if not k.get('no_debug'):
            global_flags_set['C_FLAGS'] += ['-D_DEBUG', '-Od', '-Zi']

    if k.get('no_throw'): global_flags_set['C_FLAGS'] += ['-EHs-c-', '-GR-']

    if k.get('static'):
        if global_build_type == 'RELEASE':
            global_flags_set['C_FLAGS'] += ['-MT']
        else:
            global_flags_set['C_FLAGS'] += ['-MTd']
    else:
        if global_build_type == 'RELEASE':
            global_flags_set['C_FLAGS'] += ['-MD']
        else:
            global_flags_set['C_FLAGS'] += ['-MDd']
