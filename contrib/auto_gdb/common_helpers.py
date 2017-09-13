#!/usr/bin/python
#

try:
    import gdb
except ImportError as e:
    raise ImportError("This script must be run in GDB: ", str(e))
import sys
import os
sys.path.append(os.getcwd())
import stl_containers
import simple_class_obj

SIZE_OF_INT = 4
SIZE_OF_BOOL = 1
SIZE_OF_INT64 = 8
SIZE_OF_UINT256 = 32


def get_special_type_obj(obj_str, obj_type):
    if stl_containers.VectorObj.is_this_type(obj_type):
        return stl_containers.VectorObj(obj_str, obj_type)
    if stl_containers.ListObj.is_this_type(obj_type):
        return stl_containers.ListObj(obj_str, obj_type)
    if stl_containers.PairObj.is_this_type(obj_type):
        return stl_containers.PairObj(obj_str, obj_type)
    if stl_containers.MapObj.is_this_type(obj_type):
        return stl_containers.MapObj(obj_str, obj_type)
    if stl_containers.SetObj.is_this_type(obj_type):
        return stl_containers.SetObj(obj_str, obj_type)
    if simple_class_obj.SimpleClassObj.is_this_type(obj_type):
        return simple_class_obj.SimpleClassObj(obj_str, obj_type)
    return False


def is_special_type(type_obj):
    if not get_special_type_obj("", type_obj):
        return False
    return True


def get_instance_size(obj_str, obj_type):
    obj = get_special_type_obj(obj_str, obj_type)
    if not obj:
        return obj_type.sizeof
    return obj.get_used_size()
