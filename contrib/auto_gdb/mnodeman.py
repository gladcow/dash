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
import stl_containers


class CMasternodeObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        return str(obj_type) == "CMasternode"

    def get_used_size(self):
        return common_helpers.get_instance_size(self.obj_name, gdb.lookup_type("masternode_info_t")) \
            + common_helpers.get_instance_size("(" + self.obj_name + ").lastPing", gdb.lookup_type("CMasternodePing")) \
            + stl_containers.VectorObj.from_name("(" + self.obj_name + ").vchSig").get_used_size() \
            + 4 * common_helpers.SIZE_OF_INT + 2 * common_helpers.SIZE_OF_BOOL \
            + stl_containers.MapObj.from_name("(" + self.obj_name + ").mapGovernanceObjectsVotedOn").get_used_size()


class CMasternodeVerificationObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        return str(obj_type) == "CMasternodeVerification"

    def get_used_size(self):
        return common_helpers.get_instance_size("(" + self.obj_name + ").vin1", gdb.lookup_type("CTxIn")) \
            + common_helpers.get_instance_size("(" + self.obj_name + ").vin2", gdb.lookup_type("CTxIn")) \
            + common_helpers.get_instance_size("(" + self.obj_name + ").addr", gdb.lookup_type("CService")) \
            + 2 * common_helpers.SIZE_OF_INT \
            + stl_containers.VectorObj.from_name("(" + self.obj_name + ").vchSig1").get_used_size() \
            + stl_containers.VectorObj.from_name("(" + self.obj_name + ").vchSig2").get_used_size()


class CMasternodeBroadcastObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        return str(obj_type) == "CMasternodeBroadcast"

    def get_used_size(self):
        return common_helpers.get_instance_size(self.obj_name, gdb.lookup_type("CMasternode")) \
            + common_helpers.SIZE_OF_BOOL


class CMasternodeIndexObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        return str(obj_type) == "CMasternodeIndex"

    def get_used_size(self):
        return common_helpers.SIZE_OF_INT \
            + stl_containers.MapObj.from_name("(" + self.obj_name + ").mapIndex").get_used_size() \
            + stl_containers.MapObj.from_name("(" + self.obj_name + ").mapReverseIndex").get_used_size()


class CMasternodePingObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        return str(obj_type) == "CMasternodePing"

    def get_used_size(self):
        return common_helpers.get_instance_size("(" + self.obj_name + ").vin", gdb.lookup_type("CTxIn")) \
            + common_helpers.SIZE_OF_UINT256 \
            + common_helpers.SIZE_OF_INT64 \
            + stl_containers.VectorObj.from_name("(" + self.obj_name + ").vchSig").get_used_size() \
            + common_helpers.SIZE_OF_BOOL \
            + common_helpers.SIZE_OF_INT


class CMasternodeManObj:

    def __init__ (self, obj_name, obj_type):
        self.obj_name = obj_name
        self.obj_type = obj_type

    @classmethod
    def is_this_type(cls, obj_type):
        return str(obj_type) == "CMasternodeMan"

    def get_used_size(self):
        return common_helpers.get_instance_size("(" + self.obj_name + ").cs", gdb.lookup_type("CCriticalSection")) \
             + common_helpers.SIZE_OF_INT \
             + stl_containers.VectorObj.from_name("(" + self.obj_name + ").vMasternodes").get_used_size() \
             + stl_containers.MapObj.from_name("(" + self.obj_name + ").mAskedUsForMasternodeList").get_used_size() \
             + stl_containers.MapObj.from_name("(" + self.obj_name + ").mWeAskedForMasternodeList").get_used_size() \
             + stl_containers.MapObj.from_name("(" + self.obj_name + ").mWeAskedForMasternodeListEntry").get_used_size() \
             + stl_containers.MapObj.from_name("(" + self.obj_name + ").mWeAskedForVerification").get_used_size() \
             + stl_containers.MapObj.from_name("(" + self.obj_name + ").mMnbRecoveryRequests").get_used_size() \
             + stl_containers.MapObj.from_name("(" + self.obj_name + ").mMnbRecoveryGoodReplies").get_used_size() \
             + stl_containers.ListObj.from_name("(" + self.obj_name + ").listScheduledMnbRequestConnections").get_used_size() \
             + common_helpers.SIZE_OF_INT64 \
             + 3 * common_helpers.SIZE_OF_BOOL \
             + stl_containers.VectorObj.from_name("(" + self.obj_name + ").vecDirtyGovernanceObjectHashes").get_used_size() \
             + common_helpers.SIZE_OF_INT64 \
             + stl_containers.MapObj.from_name("(" + self.obj_name + ").mapSeenMasternodeBroadcast").get_used_size() \
             + stl_containers.MapObj.from_name("(" + self.obj_name + ").mapSeenMasternodePing").get_used_size() \
             + stl_containers.MapObj.from_name("(" + self.obj_name + ").mapSeenMasternodeVerification").get_used_size() \
             + common_helpers.SIZE_OF_INT64


