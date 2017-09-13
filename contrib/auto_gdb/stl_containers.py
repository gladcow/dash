#!/usr/bin/python
#

try:
    import gdb
except ImportError as e:
    raise ImportError("This script must be run in GDB: ", str(e))
import sys
import os
sys.path.append(os.getcwd())
import common_helpers


class VectorObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        type_name = str(obj_type)
        if type_name.find("std::vector<") == 0:
            return True
        if type_name.find("std::__cxx11::vector<") == 0:
            return True
        return False

    @classmethod
    def from_name(cls, obj_name):
        return VectorObj(obj_name, gdb.parse_and_eval(obj_name).type)

    def element_type(self):
        return self.obj_type.template_argument(0)

    def size(self):
        return int(gdb.parse_and_eval(self.obj_name + "._M_impl._M_finish - " +
                                      self.obj_name + "._M_impl._M_start"))

    def get_used_size(self):
        if common_helpers.is_special_type(self.element_type()):
            size = self.obj_type.sizeof
            for i in range(self.size()):
                elem_str = "(" + self.obj_name + "._M_impl._M_start + " + str(i) + ")"
                obj = common_helpers.get_special_type_obj(elem_str, self.element_type())
                size += obj.get_used_size()
            return size
        return self.obj_type.sizeof + self.size() * self.element_type().sizeof


class ListObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        type_name = str(obj_type)
        if type_name.find("std::list<") == 0:
            return True
        if type_name.find("std::__cxx11::list<") == 0:
            return True
        return False

    @classmethod
    def from_name(cls, obj_name):
        return ListObj(obj_name, gdb.parse_and_eval(obj_name).type)

    def element_type(self):
        return self.obj_type.template_argument(0)

    def size(self):
        res = int(gdb.parse_and_eval(self.obj_name + "._M_impl._M_finish - " +
                                      self.obj_name + "._M_impl._M_start"))
        return res

    def get_used_size(self):
        gdb.execute("set $head = &" + self.obj_name + "._M_impl._M_node")
        head = gdb.parse_and_eval("$head")
        gdb.execute("set $current = " + self.obj_name + "._M_impl._M_node._M_next")
        is_special = common_helpers.is_special_type(self.element_type())
        size = self.obj_type.sizeof
        while gdb.parse_and_eval("$current") != head:
            if is_special:
                elem_str = "*('" + str(self.element_type()) + "'*)($current + 1)"
                obj = common_helpers.get_special_type_obj(elem_str, self.element_type())
                size += obj.get_used_size()
            else:
                size += self.element_type().sizeof
            gdb.execute("set $current = $current._M_next")

        return size


class PairObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        type_name = str(obj_type)
        if type_name.find("std::pair<") == 0:
            return True
        if type_name.find("std::__cxx11::pair<") == 0:
            return True
        return False

    @classmethod
    def from_name(cls, obj_name):
        return PairObj(obj_name, gdb.parse_and_eval(obj_name).type)

    def key_type(self):
        return self.obj_type.template_argument(0)

    def value_type(self):
        return self.obj_type.template_argument(1)

    def get_used_size(self):
        if not common_helpers.is_special_type(self.key_type()) and not common_helpers.is_special_type(self.value_type()):
            return self.key_type().sizeof + self.value_type().sizeof

        size = 0

        if common_helpers.is_special_type(self.key_type()):
            key_elem_str = "(" + self.obj_name + ").first"
            obj = common_helpers.get_special_type_obj(key_elem_str, self.key_type())
            size += obj.get_used_size()
        else:
            size += self.key_type().sizeof

        if common_helpers.is_special_type(self.value_type()):
            value_elem_str = "(" + self.obj_name + ").second"
            obj = common_helpers.get_special_type_obj(value_elem_str, self.value_type())
            size += obj.get_used_size()
        else:
            size += self.value_type().sizeof

        return size


def find_type(orig, name):
    typ = orig.strip_typedefs()
    while True:
        # Strip cv qualifiers
        search = '%s::%s' % (typ.unqualified(), name)
        try:
            return gdb.lookup_type(search)
        except RuntimeError:
            pass
        # type is not found,  try superclass search
        field = typ.fields()[0]
        if not field.is_base_class:
            raise ValueError("Cannot find type %s::%s" % (str(orig), name))
        typ = field.type


def get_value_from_aligned_membuf(buf, valtype):
    """Returns the value held in a __gnu_cxx::__aligned_membuf."""
    return buf['_M_storage'].address.cast(valtype.pointer()).dereference()


def get_value_from_Rb_tree_node(node):
    valtype = node.type.template_argument(0)
    return get_value_from_aligned_membuf(node['_M_storage'], valtype)


class MapObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type
        rep_type = find_type(self.obj_type, "_Rep_type")
        self.node_type = find_type(rep_type, "_Link_type")
        self.node_type = self.node_type.strip_typedefs()

    @classmethod
    def is_this_type(cls, obj_type):
        type_name = str(obj_type)
        if type_name.find("std::map<") == 0:
            return True
        if type_name.find("std::__cxx11::map<") == 0:
            return True
        return False

    @classmethod
    def from_name(cls, obj_name):
        return MapObj(obj_name, gdb.parse_and_eval(obj_name).type)

    def key_type(self):
        return self.obj_type.template_argument(0).strip_typedefs()

    def value_type(self):
        return self.obj_type.template_argument(1).strip_typedefs()

    def size(self):
        res = int(gdb.parse_and_eval(self.obj_name + "._M_t->_M_impl->_M_node_count"))
        return res

    def get_used_size(self):
        if not common_helpers.is_special_type(self.key_type()) and not common_helpers.is_special_type(self.value_type()):
            return self.obj_type.sizeof + self.size() * (self.key_type().sizeof + self.value_type().sizeof)
        if self.size() == 0:
            return self.obj_type.sizeof
        size = self.obj_type.sizeof
        gdb.execute("set $node = " + self.obj_name + "._M_t._M_impl._M_header._M_left")
        row_node = gdb.parse_and_eval("$node")
        for i in range(self.size()):
            node_val = row_node.cast(self.node_type).dereference()
            pair = get_value_from_Rb_tree_node(node_val)

            val_type = pair.type
            val_str = "*('%s'*)%s" % (str(val_type), str(pair.address))
            size += common_helpers.get_instance_size(val_str, val_type)

            node = row_node
            if node.dereference()['_M_right']:
                node = node.dereference()['_M_right']
                while node.dereference()['_M_left']:
                    node = node.dereference()['_M_left']
            else:
                parent = node.dereference()['_M_parent']
                while node == parent.dereference()['_M_right']:
                    node = parent
                    parent = parent.dereference()['_M_parent']
                if node.dereference()['_M_right'] != parent:
                    node = parent
            row_node = node
        return size


class SetObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        type_name = str(obj_type)
        if type_name.find("std::set<") == 0:
            return True
        if type_name.find("std::__cxx11::set<") == 0:
            return True
        return False

    @classmethod
    def from_name(cls, obj_name):
        return SetObj(obj_name, gdb.parse_and_eval(obj_name).type)

    def element_type(self):
        return self.obj_type.template_argument(0)

    def size(self):
        res = int(gdb.parse_and_eval(self.obj_name + "->_M_t->_M_impl->_M_node_count"))
        return res

    def get_used_size(self):
        if not common_helpers.is_special_type(self.element_type()):
            return self.obj_type.sizeof + self.size() * self.element_type().sizeof
        if self.size() == 0:
            return self.obj_type.sizeof
        size = self.obj_type.sizeof
        gdb.execute("set $node = " + self.obj_name + "->_M_t->_M_impl->_M_header->_M_left")
        for i in range(self.size()):
            gdb.execute("set $value = (void*)($node + 1)")
            elem_str = "*('" + str(self.element_type()) + "'*)$value"
            obj = common_helpers.get_special_type_obj(elem_str, self.element_type())
            size += obj.get_used_size()

            if gdb.parse_and_eval("$node->_M_right") != 0:
                gdb.execute("set $node = $node->_M_right")
                while gdb.parse_and_eval("$node->_M_left") != 0:
                    gdb.execute("set $node = $node->_M_left")
            else:
                gdb.execute("set $tmp_node = $node->_M_parent")
                while gdb.parse_and_eval("$node") == gdb.parse_and_eval("$tmp_node->_M_right"):
                    gdb.execute("set $node = $tmp_node")
                    gdb.execute("set $tmp_node = $tmp_node->_M_parent")
                if gdb.parse_and_eval("$node->_M_right") != gdb.parse_and_eval("$tmp_node"):
                    gdb.execute("set $node = $tmp_node")
        return size


