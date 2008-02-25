# -*- coding: cp1251 -*-
#
# (c)2008, Alexey Sudachen, alexey@sudachen.name
# http://www.ethical-hacker.info/
#

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
    }

global_build_type = 'RELEASE'
global_build_config = 'DEFAULT'
global_build_operation = 'BUILD'

def process_command_line():
    opts,args = getopt.getopt(sys.argv[1:],"vh",[])

    global global_build_type
    global global_build_config
    global global_build_operation

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

def _ms_cl_compile_file(source,target,flags):
    if global_build_operation == 'BUILD':
        if _need_to_build(source,target):
            cmd_S = 'cl %s -c -Fo"%s" %s' % (' '.join(flags),target,source)
            print cmd_S
            e = os.system(cmd_S)
            if e != 0 :
                raise Exception('failed to CC build: %s')
    elif global_build_operation == 'CLEAN':
        if os.path.exists(target):
            print 'unlink "%s"' % target
            os.unlink(target)

def _cc_build_rule(source,target,flags,deps):
    rel_flags = flags + global_flags_set['C_FLAGS'] + global_flags_set['CC_FLAGS'] \
        + _select_flags_with_build_type('C_') \
        + _select_flags_with_build_type('CC_')
    _ms_cl_compile_file(source,target,rel_flags)
    return target

def _cxx_build_rule(source,target,flags,deps):
    rel_flags = flags + global_flags_set['C_FLAGS'] + global_flags_set['CXX_FLAGS'] \
        + _select_flags_with_build_type('C_') \
        + _select_flags_with_build_type('CXX_')
    _ms_cl_compile_file(source,target,rel_flags)
    return target

global_tool_types = {
    'c-file':{
        'maker':_cc_build_rule,
        'object-ext':'.obj','source_exts':['.c']},
    'c++-file':{
        'maker':_cxx_build_rule,
        'object-ext':'.obj','source_exts':['.C','.cpp','.c++','.cc']},
    'o-file':{
        'maker':_fake_build_rule,
        'object-ext':'.obj','source_exts':['.obj']},
    'lib-file':{
        'maker':_fake_build_rule,
        'object-ext':'.lib','source_exts':['.lib']},
    }

global_ext_map = {}
for i,j in global_tool_types.items():
    for k in j['source_exts']:
        global_ext_map[k] = i

def select_tool_type(ext):
    file_type = global_ext_map.get(ext)
    if file_type:
        return global_tool_types[file_type]
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
    return (source,target,flags,deps,tool_type['maker'])

def normolize_sources(sources,basedir,resolve_deps=(False,[])):
    """sources - list of sources or tuples(source,[flags],[deps])
       basedir - base for relative soruce paths
       resolve_deps - tule(on/of,[exlude paths])
       flags_set - set of flags for building tools"""
    return [_normalize_source_tuple(i,basedir,resolve_deps) for i in sources]

def compile_files(sources,tempdir):
    objects = []
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
    for source_data in sources:
        if type(source_data) == type(''):
            source_data = _normalize_source_tuple(source_data,'.',(None,[]))
        source,target,flags,deps,tool = source_data
        target = os.path.join(tempdir,target)
        objects.append(tool(source,target,flags,deps))
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
            cmd_S = (cmd+' -out:"%s" '%target)+' '.join(flags)+(' @"%s"'%objectslist)
            print cmd_S
            if 0 != os.system( cmd_S ):
                raise Exception('faile to link "%s"'%target)
    elif global_build_operation == 'CLEAN':
        if os.path.exists(target):
            print 'unlink "%s"' % target
            os.unlink(target)

def link_static(objects,tempdir,target,flags=[]):
    rel_flags = flags + global_flags_set['LIB_FLAGS'] + _select_flags_with_build_type('LIB_')
    _msc_link_file(objects,[],tempdir,target,rel_flags,'lib')

def link_shared(objects,libs,tempdir,target,flags=[]):
    rel_flags = flags + global_flags_set['LINK_FLAGS'] + _select_flags_with_build_type('LINK_')
    _msc_link_file(objects,libs,tempdir,target,rel_flags,'link')

def link_executable(objects,libs,tempdir,target,flags_set={}):
    pass
