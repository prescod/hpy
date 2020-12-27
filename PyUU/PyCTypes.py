import types
from ctypes import c_int32, Structure, c_uint32
from enum import Enum, auto
from typing import NamedTuple
import traceback


handle = voidptr = strptr = ptr = int
SIZEOF_HANDLE = 4
SIZEOF_POINTER = 4
SIZEOF_KIND = 4

RuntimeContext = "PyUU.extension_wrapper.RuntimeContext"


class HPyType_Spec(Structure):
    _fields_ = [
        ("name", c_int32),
        ("basicsize", c_int32),
        ("itemsize", c_int32),
        ("flags", c_uint32),
        ("legacy_slots", c_uint32),
        ("defines", c_uint32),
    ]


class HPyFunc_Signature(Enum):
    HPyFunc_VARARGS = 1  # METH_VARARGS
    HPyFunc_KEYWORDS = 2  # METH_VARARGS | METH_KEYWORDS
    HPyFunc_NOARGS = 3  # METH_NOARGS
    HPyFunc_O = 4  # METH_O
    HPyFunc_DESTROYFUNC = auto()
    HPyFunc_UNARYFUNC = auto()
    HPyFunc_BINARYFUNC = auto()
    HPyFunc_TERNARYFUNC = auto()
    HPyFunc_INQUIRY = auto()
    HPyFunc_LENFUNC = auto()
    HPyFunc_SSIZEARGFUNC = auto()
    HPyFunc_SSIZESSIZEARGFUNC = auto()
    HPyFunc_SSIZEOBJARGPROC = auto()
    HPyFunc_SSIZESSIZEOBJARGPROC = auto()
    HPyFunc_OBJOBJARGPROC = auto()
    HPyFunc_FREEFUNC = auto()
    HPyFunc_GETATTRFUNC = auto()
    HPyFunc_GETATTROFUNC = auto()
    HPyFunc_SETATTRFUNC = auto()
    HPyFunc_SETATTROFUNC = auto()
    HPyFunc_REPRFUNC = auto()
    HPyFunc_HASHFUNC = auto()
    HPyFunc_RICHCMPFUNC = auto()
    HPyFunc_GETITERFUNC = auto()
    HPyFunc_ITERNEXTFUNC = auto()
    HPyFunc_DESCRGETFUNC = auto()
    HPyFunc_DESCRSETFUNC = auto()
    HPyFunc_INITPROC = auto()
    HPyFunc_GETTER = auto()
    HPyFunc_SETTER = auto()
    HPyFunc_OBJOBJPROC = auto()


class HPyMeth(Structure):
    _fields_ = [
        ("name", c_int32),
        ("doc", c_int32),
        ("impl", c_int32),
        ("cpy_trampoline", c_int32),
        ("signature", c_int32),
    ]

    def as_dict(self):
        return {fieldname: getattr(self, fieldname)
                for fieldname, _ in self._fields_}


class HPyDef_Kind(Enum):
    HPyDef_Kind_Slot = 1
    HPyDef_Kind_Meth = 2
    HPyDef_Kind_Member = 3
    HPyDef_Kind_GetSet = 4


class HPyModuleDef(Structure):
    _fields_ = [
        ("dummy", c_int32),
        ("m_name", c_int32),
        ("m_doc", c_int32),
        ("m_size", c_int32),
        ("legacy_methods", c_int32),
        ("defines", c_int32)]

    def as_dict(self):
        return {fieldname: getattr(self, fieldname)
                for fieldname, _ in self._fields_}



class PyMethod(NamedTuple):
    runtime: object
    extension_context: int
    name: str
    doc: str
    impl: int
    cpy_trampoline: int
    signature: HPyFunc_Signature

    def call(self, objself, args, kwargs):
        rt: "RuntimeContext" = self.runtime
        if objself is None:
            objself = rt.new_handle(None)

            if objself:
                assert rt.has_handle(objself)  # should be a handle

        if self.signature == HPyFunc_Signature.HPyFunc_NOARGS.value:
            assert not args and not kwargs
            res = rt.instance.exports.PyUU_Call_HPyFunc_NOARGS(
                self.extension_context, self.impl, objself
            )
            return rt.resolve_handle(res)
        elif self.signature == HPyFunc_Signature.HPyFunc_O.value:
            assert not kwargs
            assert len(args) == 1
            arg = rt.new_handle(args[0])
            res = rt.instance.exports.PyUU_Call_HPyFunc_O(
                self.extension_context, self.impl, objself, arg
            )
            rt.release_handle(arg)
            return rt.resolve_handle(res)
        elif self.signature == HPyFunc_Signature.HPyFunc_VARARGS.value:
            assert not kwargs
            array, arg_handles = self.args_to_array(rt, args)

            res = rt.instance.exports.PyUU_Call_HPyFunc_VARARGS(
                self.extension_context, self.impl,
                objself, array, len(args)
            )
            for arg in arg_handles:
                rt.release_handle(arg)
            return rt.resolve_handle(res)
        elif self.signature == HPyFunc_Signature.HPyFunc_KEYWORDS.value:
            array, arg_handles = self.args_to_array(rt, args)
            kw = rt.new_handle(kwargs)

            res = rt.instance.exports.PyUU_Call_HPyFunc_KEYWORDS(
                self.extension_context, self.impl,
                objself, array, len(args), kw
            )
            rt.release_handle(kw)
            for arg in arg_handles:
                rt.release_handle(arg)
            return rt.resolve_handle(res)

        else:
            assert 0, ("Unknown Signature", self.signature)

    def __call__(self, *args, **kwargs):
        # think more about objself here!
        # bound versus unbound methods etc.
        return self.call(None, args, kwargs)

    def args_to_array(self, rt: RuntimeContext, args):
        arg_handles = [rt.new_handle(arg) for arg in args]
        args_to_array = rt.instance.exports.malloc(len(args) * SIZEOF_HANDLE)
        args_to_array_view = rt.memory.int32_view(offset=args_to_array // 4)
        for addr, arg_addr in enumerate(arg_handles):
            args_to_array_view[addr] = arg_addr
        return args_to_array, arg_handles
