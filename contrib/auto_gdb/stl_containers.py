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
        return int(gdb.parse_and_eval(self.obj_name + "._M_impl._M_finish - " +
                                      self.obj_name + "._M_impl._M_start"))

    def get_used_size(self):
        gdb.execute("set $head = &" + self.obj_name + "._M_impl._M_node")
        head = gdb.parse_and_eval("$head")
        gdb.execute("set $current = " + self.obj_name + "._M_impl._M_node->_M_next")
        size = self.obj_type.sizeof
        while gdb.parse_and_eval("$current") != head:
            if common_helpers.is_special_type(self.element_type()):
                elem_str = "*('" + str(self.obj_type) + "'*)($current + 1)"
                obj = common_helpers.get_special_type_obj(elem_str, self.element_type())
                size += obj.get_used_size()
            else:
                size += self.element_type().sizeof
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
        if not common_helpers.is_special_type(self.key_type()) and not is_special_type(self.value_type()):
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


class MapObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

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
        return self.obj_type.template_argument(0)

    def value_type(self):
        return self.obj_type.template_argument(1)

    def size(self):
        res = int(gdb.parse_and_eval(self.obj_name + "._M_t->_M_impl->_M_node_count"))
        return res

    def get_used_size(self):
        if not common_helpers.is_special_type(self.key_type()) and not is_special_type(self.value_type()):
            return self.obj_type.sizeof + self.size() * (self.key_type().sizeof + self.value_type().sizeof)
        if self.size() == 0:
            return self.obj_type.sizeof
        size = self.obj_type.sizeof
        gdb.execute("set $node = " + self.obj_name + "._M_t._M_impl._M_header._M_left")
        for i in range(self.size()):
            gdb.execute("set $value = (void*)($node + 1)")
            if common_helpers.is_special_type(self.key_type()):
                key_elem_str = "*('" + str(self.key_type()) + "'*)$value"
                obj = common_helpers.get_special_type_obj(key_elem_str, self.key_type())
                size += obj.get_used_size()
            else:
                size += self.key_type().sizeof

            gdb.execute("set $value = $value + " + str(self.key_type().sizeof))
            if common_helpers.is_special_type(self.value_type()):
                value_elem_str = "*('" + str(self.value_type()) + "'*)$value"
                obj = common_helpers.get_special_type_obj(value_elem_str, self.value_type())
                size += obj.get_used_size()
            else:
                size += self.key_type().sizeof

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


