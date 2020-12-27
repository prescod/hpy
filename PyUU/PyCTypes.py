from ctypes import c_int32, Structure, c_uint32, Union, sizeof
from enum import Enum, auto
from typing import NamedTuple
import functools
from dataclasses import dataclass


handle = voidptr = strptr = ptr = int
SIZEOF_HANDLE = 4
SIZEOF_POINTER = 4
SIZEOF_ENUM = 4

RuntimeContext = "PyUU.extension_wrapper.RuntimeContext"


class HPyType_Spec(Structure):
    runtime = None  # set later
    _fields_ = [
        ("name", c_int32),
        ("basicsize", c_int32),
        ("itemsize", c_int32),
        ("flags", c_uint32),
        ("legacy_slots", c_uint32),
        ("defines", c_uint32),
    ]

    @property
    def name_as_str(self):
        nameptr = self.runtime.Ptr(self.name)
        return nameptr.deref_to_str()

    def defines_as_list(self, ctx):
        return defines_as_list(self.runtime, self.defines, ctx)


def defines_as_list(rt, defines, ctx):
    type_defines = rt.Ptr(defines)
    pointer_views = rt.split_array(type_defines.offset, SIZEOF_POINTER)
    pointers_as_ints = [
        c_int32.from_buffer_copy(ptr).value for ptr in pointer_views
    ]

    pointer_objs = [rt.Ptr(ptr) for ptr in pointers_as_ints]
    defines = [parse_define(rt, ctx, pointer) for pointer in pointer_objs]
    return defines


def parse_define(runtime_context, ctx, pointer):
    kind = pointer.deref_to_int()

    if kind == HPyDef_Kind.HPyDef_Kind_Meth.value:
        sub_struct_pointer = pointer + SIZEOF_ENUM
        return create_function(runtime_context, ctx, sub_struct_pointer)
    if kind == HPyDef_Kind.HPyDef_Kind_Slot.value:
        sub_struct_pointer = pointer + SIZEOF_ENUM
        return create_slot(runtime_context, ctx, sub_struct_pointer)
    else:
        assert 0, ("Can't handle", HPyDef_Kind(kind).name)


def create_function(runtime_context, extension_context, sub_struct_pointer):
    type_struct = sub_struct_pointer.deref_to_struct(HPyMeth)
    name = runtime_context.Ptr(type_struct.name).deref_to_str()
    doc = runtime_context.Ptr(type_struct.doc).deref_to_str()
    signature = type_struct.signature

    return PyMethod(
        runtime_context,
        extension_context,
        name,
        doc,
        type_struct.impl,
        type_struct.cpy_trampoline,
        signature,
    )


def create_slot(runtime_context, extension_context, sub_struct_pointer):
    type_struct = sub_struct_pointer.deref_to_struct(HPySlot)
    kind = HPySlot_Slot(type_struct.slot)
    if kind == HPySlot_Slot.HPy_tp_new:
        return PyUnboundMethod(
            runtime_context,
            extension_context,
            "__new__",
            "Initialize",
            type_struct.impl,
            type_struct.cpy_trampoline,
            HPyFunc_Signature.HPyFunc_KEYWORDS.value,
        )
    elif kind == HPySlot_Slot.HPy_tp_repr:
        return PyUnboundMethod(
            runtime_context,
            extension_context,
            "__repr__",
            "Represent",
            type_struct.impl,
            type_struct.cpy_trampoline,
            HPyFunc_Signature.HPyFunc_NOARGS.value,
        )
    else:
        assert 0, kind.name


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
        return {
            fieldname: getattr(self, fieldname)
            for fieldname, _ in self._fields_
        }


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
        ("defines", c_int32),
    ]

    def as_dict(self):
        return {
            fieldname: getattr(self, fieldname)
            for fieldname, _ in self._fields_
        }


class HPySlot(Structure):
    _fields_ = [
        ("slot", c_int32),
        ("impl", c_int32),
        ("cpy_trampoline", c_int32),
    ]


class HPyMember(Structure):
    _fields_ = []
    # TODO


class HPyGetSet(Structure):
    _fields_ = []
    # TODO


class HPyDefUnion(Union):
    _fields_ = [
        ("slot", HPySlot),
        ("meth", HPyMeth),
        ("member", HPyMember),
        ("getset", HPyGetSet),
    ]


class HPyDef:
    _anonymous_ = ("_u",)
    _fields_ = [("kind", int), ("_u", HPyDefUnion)]


@dataclass
class PyMethod:
    runtime: object
    extension_context: int
    name: str
    doc: str
    impl: int
    cpy_trampoline: int
    signature: HPyFunc_Signature

    @property
    def __name__(self):
        return self.name

    def call(self, self_handle, args, kwargs):
        rt: "RuntimeContext" = self.runtime
        if self_handle is None:
            self_handle = rt.new_handle(None)

        if self_handle:
            assert rt.has_handle(self_handle)  # should be a handle

        if self.signature == HPyFunc_Signature.HPyFunc_NOARGS.value:
            assert not args and not kwargs, (
                self_handle,
                rt.resolve_handle(self_handle),
                args,
                kwargs,
            )
            res = rt.instance.exports.PyUU_Call_HPyFunc_NOARGS(
                self.extension_context, self.impl, self_handle
            )
            return rt.resolve_handle(res)
        elif self.signature == HPyFunc_Signature.HPyFunc_O.value:
            assert not kwargs
            assert len(args) == 1
            arg = rt.new_handle(args[0])
            res = rt.instance.exports.PyUU_Call_HPyFunc_O(
                self.extension_context, self.impl, self_handle, arg
            )
            rt.release_handle(arg)
            return rt.resolve_handle(res)
        elif self.signature == HPyFunc_Signature.HPyFunc_VARARGS.value:
            assert not kwargs
            array, arg_handles = self.args_to_array(rt, args)

            res = rt.instance.exports.PyUU_Call_HPyFunc_VARARGS(
                self.extension_context,
                self.impl,
                self_handle,
                array,
                len(args),
            )
            for arg in arg_handles:
                rt.release_handle(arg)
            return rt.resolve_handle(res)
        elif self.signature == HPyFunc_Signature.HPyFunc_KEYWORDS.value:
            array, arg_handles = self.args_to_array(rt, args)
            kw = rt.new_handle(kwargs)
            res = rt.instance.exports.PyUU_Call_HPyFunc_KEYWORDS(
                self.extension_context,
                self.impl,
                self_handle,
                array,
                len(args),
                kw,
            )
            rt.release_handle(kw)
            for arg in arg_handles:
                rt.release_handle(arg)
            return rt.resolve_handle(res)

        else:
            assert 0, ("Unknown Signature", self.signature)

    def __call__(self, *args, **kwargs):
        return self.call(None, args, kwargs)

    def args_to_array(self, rt: RuntimeContext, args):
        arg_handles = [rt.new_handle(arg) for arg in args]
        args_to_array = rt.instance.exports.malloc(len(args) * SIZEOF_HANDLE)
        args_to_array_view = rt.memory.int32_view(offset=args_to_array // 4)
        for addr, arg_addr in enumerate(arg_handles):
            args_to_array_view[addr] = arg_addr
        return args_to_array, arg_handles


def PyUnboundMethod(
    runtime: object,
    extension_context: int,
    name: str,
    doc: str,
    impl: int,
    cpy_trampoline: int,
    signature: HPyFunc_Signature,
):
    method = PyMethod(
        runtime, extension_context, name, doc, impl, cpy_trampoline, signature
    )

    def unbound_method_wrapper(self, *args, **kwargs):
        """An object instance cannot easily serve as an unbound method wrapper.
        So we use a real function"""
        objself = runtime.new_handle(self)
        return method.call(objself, args, kwargs)

    unbound_method_wrapper = functools.update_wrapper(unbound_method_wrapper, method)
    unbound_method_wrapper.name = name
    unbound_method_wrapper.__qualname__ = name + "(wasmproxy)"

    return unbound_method_wrapper


class Ptr:
    def __init__(self, runtime_context: RuntimeContext, offset: int):
        self.runtime_context = runtime_context
        assert isinstance(offset, int)
        self.offset = offset
        self.buffer = self.runtime_context.memory.buffer

    def deref_to_view(self):
        return memoryview(self.buffer)[self.offset:]

    def deref_to_str(self):
        return self.runtime_context.decode(self.offset)

    def deref_to_int(self):
        view = self.deref_to_view()
        i = c_int32.from_buffer_copy(view)
        return i.value

    def deref_to_ptr(self):
        return Ptr(self.runtime_context, self.deref_to_int())

    def deref_to_struct(self, struct_type):
        sizeof_spec = sizeof(struct_type)
        struct_view = self.deref_to_view()[0:sizeof_spec]
        struct = struct_type.from_buffer_copy(struct_view)
        struct.runtime = self.runtime_context
        return struct

    def __add__(self, other: int):
        return Ptr(self.runtime_context, self.offset + other)

    def __repr__(self):
        return f"<Ptr {hex(self.offset)}>"


class HPySlot_Slot(Enum):
    HPy_nb_absolute = 6
    HPy_nb_add = 7
    HPy_nb_and = 8
    HPy_nb_bool = 9
    HPy_nb_divmod = 10
    HPy_nb_float = 11
    HPy_nb_floor_divide = 12
    HPy_nb_index = 13
    HPy_nb_inplace_add = 14
    HPy_nb_inplace_and = 15
    HPy_nb_inplace_floor_divide = 16
    HPy_nb_inplace_lshift = 17
    HPy_nb_inplace_multiply = 18
    HPy_nb_inplace_or = 19
    HPy_nb_inplace_power = 20
    HPy_nb_inplace_remainder = 21
    HPy_nb_inplace_rshift = 22
    HPy_nb_inplace_subtract = 23
    HPy_nb_inplace_true_divide = 24
    HPy_nb_inplace_xor = 25
    HPy_nb_int = 26
    HPy_nb_invert = 27
    HPy_nb_lshift = 28
    HPy_nb_multiply = 29
    HPy_nb_negative = 30
    HPy_nb_or = 31
    HPy_nb_positive = 32
    HPy_nb_power = 33
    HPy_nb_remainder = 34
    HPy_nb_rshift = 35
    HPy_nb_subtract = 36
    HPy_nb_true_divide = 37
    HPy_nb_xor = 38
    HPy_sq_ass_item = 39
    HPy_sq_concat = 40
    HPy_sq_contains = 41
    HPy_sq_inplace_concat = 42
    HPy_sq_inplace_repeat = 43
    HPy_sq_item = 44
    HPy_sq_length = 45
    HPy_sq_repeat = 46
    HPy_tp_init = 60
    HPy_tp_new = 65
    HPy_tp_repr = 66
    HPy_nb_matrix_multiply = 75
    HPy_nb_inplace_matrix_multiply = 76
    HPy_tp_destroy = 1000
