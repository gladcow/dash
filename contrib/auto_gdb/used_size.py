#!/usr/bin/python
#

try:
    import gdb
except ImportError as e:
    raise ImportError("This script must be run in GDB: ", str(e))

SIZE_OF_INT = 8
SIZE_OF_BOOL = 1


def get_special_type_obj(obj_str, obj_type):
    if VectorObj.is_this_type(obj_type):
        return VectorObj(obj_str, obj_type)
    if ListObj.is_this_type(obj_type):
        return ListObj(obj_str, obj_type)
    if PairObj.is_this_type(obj_type):
        return PairObj(obj_str, obj_type)
    if MapObj.is_this_type(obj_type):
        return MapObj(obj_str, obj_type)
    if SetObj.is_this_type(obj_type):
        return SetObj(obj_str, obj_type)
    if CMasternodeObj.is_this_type(obj_type):
        return CMasternodeObj(obj_str, obj_type)
    if CMasternodeVerificationObj.is_this_type(obj_type):
        return CMasternodeVerificationObj(obj_str, obj_type)
    if CMasternodeBroadcastObj.is_this_type(obj_type):
        return CMasternodeBroadcastObj(obj_str, obj_type)
    if CMasternodeIndexObj.is_this_type(obj_type):
        return CMasternodeIndexObj(obj_str, obj_type)
    if CMasternodePingObj.is_this_type(obj_type):
        return CMasternodePingObj(obj_str, obj_type)
    if CMasternodeManObj.is_this_type(obj_type):
        return CMasternodeManObj(obj_str, obj_type)
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
        if is_special_type(self.element_type()):
            size = self.obj_type.sizeof
            for i in range(self.size()):
                elem_str = "(" + self.obj_name + "._M_impl._M_start + " + str(i) + ")"
                obj = get_special_type_obj(elem_str, self.element_type())
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
            if is_special_type(self.element_type()):
                elem_str = "*('" + str(self.obj_type) + "'*)($current + 1)"
                obj = get_special_type_obj(elem_str, self.element_type())
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
        if not is_special_type(self.key_type()) and not is_special_type(self.value_type()):
            return self.key_type().sizeof + self.value_type().sizeof

        size = 0

        if is_special_type(self.key_type()):
            key_elem_str = "(" + self.obj_name + ").first"
            obj = get_special_type_obj(key_elem_str, self.key_type())
            size += obj.get_used_size()
        else:
            size += self.key_type().sizeof

        if is_special_type(self.value_type()):
            value_elem_str = "(" + self.obj_name + ").second"
            obj = get_special_type_obj(value_elem_str, self.value_type())
            size += obj.get_used_size()
        else:
            size += self.key_type().sizeof

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
        if not is_special_type(self.key_type()) and not is_special_type(self.value_type()):
            return self.obj_type.sizeof + self.size() * (self.key_type().sizeof + self.value_type().sizeof)
        if self.size() == 0:
            return self.obj_type.sizeof
        size = self.obj_type.sizeof
        gdb.execute("set $node = " + self.obj_name + "._M_t._M_impl._M_header._M_left")
        for i in range(self.size()):
            gdb.execute("set $value = (void*)($node + 1)")
            if is_special_type(self.key_type()):
                key_elem_str = "*('" + str(self.key_type()) + "'*)$value"
                obj = get_special_type_obj(key_elem_str, self.key_type())
                size += obj.get_used_size()
            else:
                size += self.key_type().sizeof

            gdb.execute("set $value = $value + " + str(self.key_type().sizeof))
            if is_special_type(self.value_type()):
                value_elem_str = "*('" + str(self.value_type()) + "'*)$value"
                obj = get_special_type_obj(value_elem_str, self.value_type())
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
        if not is_special_type(self.element_type()):
            return self.obj_type.sizeof + self.size() * self.element_type().sizeof
        if self.size() == 0:
            return self.obj_type.sizeof
        size = self.obj_type.sizeof
        gdb.execute("set $node = " + self.obj_name + "->_M_t->_M_impl->_M_header->_M_left")
        for i in range(self.size()):
            gdb.execute("set $value = (void*)($node + 1)")
            elem_str = "*('" + str(self.element_type()) + "'*)$value"
            obj = get_special_type_obj(elem_str, self.element_type())
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


class CMasternodeObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        return str(obj_type) == "CMasternode"

    def get_used_size(self):
        return get_instance_size(self.obj_name, gdb.lookup_type("masternode_info_t")) \
            + get_instance_size(self.obj_name + ".lastPing", gdb.lookup_type("CMasternodePing")) \
            + VectorObj.from_name(self.obj_name + ".vchSig").get_used_size() \
            + 4 * SIZE_OF_INT + 2 * SIZE_OF_BOOL \
            + MapObj.from_name(self.obj_name + ".mapGovernanceObjectsVotedOn").get_used_size()


class CMasternodeVerificationObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        return str(obj_type) == "CMasternodeVerification"

    def get_used_size(self):
        return get_instance_size(self.obj_name + ".vin1", gdb.lookup_type("CTxIn")) \
            + get_instance_size(self.obj_name + ".vin2", gdb.lookup_type("CTxIn")) \
            + get_instance_size(self.obj_name + ".addr", gdb.lookup_type("CService")) \
            + 2 * SIZE_OF_INT \
            + VectorObj.from_name(self.obj_name + ".vchSig1").get_used_size() \
            + VectorObj.from_name(self.obj_name + ".vchSig2").get_used_size()


class CMasternodeBroadcastObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        return str(obj_type) == "CMasternodeBroadcast"

    def get_used_size(self):
        return get_instance_size(self.obj_name, gdb.lookup_type("CMasternode")) \
            + SIZE_OF_BOOL


class CMasternodeIndexObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        return str(obj_type) == "CMasternodeIndex"

    def get_used_size(self):
        return SIZE_OF_INT \
            + MapObj.from_name(self.obj_name + ".mapIndex").get_used_size() \
            + MapObj.from_name(self.obj_name + ".mapReverseIndex").get_used_size()


class CMasternodePingObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        return str(obj_type) == "CMasternodePing"

    def get_used_size(self):
        return get_instance_size(self.obj_name + ".vin", gdb.lookup_type("CTxIn")) \
            + get_instance_size(self.obj_name + ".blockHash", gdb.lookup_type("uint256")) \
            + get_instance_size(self.obj_name + ".sigTime", gdb.lookup_type("int64_t")) \
            + VectorObj.from_name(self.obj_name + ".vchSig").get_used_size() \
            + SIZE_OF_BOOL \
            + get_instance_size(self.obj_name + ".nSentinelVersion", gdb.lookup_type("uint32_t"))


class CMasternodeManObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        return str(obj_type) == "CMasternodeMan"

    def get_used_size(self):
        return get_instance_size(self.obj_name + ".cs", gdb.lookup_type("CCriticalSection")) \
             + gdb.parse_and_eval(self.obj_name + ".pCurrentBlockIndex").type.sizeof \
             + VectorObj.from_name(self.obj_name + ".vMasternodes").get_used_size() \
             + MapObj.from_name(self.obj_name + ".mAskedUsForMasternodeList").get_used_size() \
             + MapObj.from_name(self.obj_name + ".mWeAskedForMasternodeList").get_used_size() \
             + MapObj.from_name(self.obj_name + ".mWeAskedForMasternodeListEntry").get_used_size() \
             + MapObj.from_name(self.obj_name + ".mWeAskedForVerification").get_used_size() \
             + MapObj.from_name(self.obj_name + ".mMnbRecoveryRequests").get_used_size() \
             + MapObj.from_name(self.obj_name + ".mMnbRecoveryGoodReplies").get_used_size() \
             + ListObj.from_name(self.obj_name + ".listScheduledMnbRequestConnections").get_used_size() \
             + get_instance_size(self.obj_name + ".nLastIndexRebuildTime", gdb.lookup_type("int64_t")) \
             + get_instance_size(self.obj_name + ".indexMasternodes", gdb.lookup_type("CMasternodeIndex")) \
             + get_instance_size(self.obj_name + ".indexMasternodesOld", gdb.lookup_type("CMasternodeIndex")) \
             + 3 * SIZE_OF_BOOL \
             # + VectorObj.from_name(self.obj_name + ".vecDirtyGovernanceObjectHashes").get_used_size() \
             # + get_instance_size(self.obj_name + ".nLastWatchdogVoteTime", gdb.lookup_type("int64_t")) \
             # + MapObj.from_name(self.obj_name + ".mapSeenMasternodeBroadcast").get_used_size() \
             # + MapObj.from_name(self.obj_name + ".mapSeenMasternodePing").get_used_size() \
             # + MapObj.from_name(self.obj_name + ".mapSeenMasternodeVerification").get_used_size() \
             # + get_instance_size(self.obj_name + ".nDsqCount", gdb.lookup_type("int64_t"))


class UsedSizeCommand (gdb.Command):
    """calc size of the memory used by the object"""

    def __init__ (self):
        super (UsedSizeCommand, self).__init__ ("usedsize", gdb.COMMAND_USER)

    def assign_value(self, obj_name, value):
        gdb.execute("set " + obj_name + " = " + str(value))

    def get_type(self, obj_name):
        return gdb.parse_and_eval(obj_name).type

    def invoke (self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        obj_type = self.get_type(args[1])
        print (args[1] + " is " + str(obj_type))
        size = get_instance_size(args[1], obj_type)
        self.assign_value(args[0], size)
        size_obj = gdb.parse_and_eval(args[0])
        print (size_obj)

UsedSizeCommand()
