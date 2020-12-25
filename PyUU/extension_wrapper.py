from enum import Enum
import traceback
import types
from typing import NamedTuple
import ctypes
from ctypes import Structure, c_char_p, c_void_p, c_int32, c_uint32

# from wasmapy import (
#     get_implementation,
#     WasmStore
# )
from wasmer import Store, Memory, Module, wasi, Instance, MemoryType

from .wasm_helpers import utf_decode, WasmFunctions, split_array

voidptr = strptr = ptr = int


class HPyType_Spec(Structure):
    _fields_ = [
        ("name", c_int32),
        ("basicsize", c_int32),
        ("itemsize", c_int32),
        ("flags", c_uint32),
        ("legacy_slots", c_void_p),
        ("defines", c_void_p),
    ]


class HPyDef_Kind(Enum):
    HPyDef_Kind_Slot = 1
    HPyDef_Kind_Meth = 2
    HPyDef_Kind_Member = 3
    HPyDef_Kind_GetSet = 4


class CInt:
    size = 4

    @staticmethod
    def from_view(value_view):
        return int.from_bytes(value_view[0:4], "little")


class ZeroTermStr:
    size = 4

    @staticmethod
    def from_view(value_view):
        target_str_ptr = CInt.from_view(value_view[0:4])
        return utf_decode(value_view, target_str_ptr)


PyMethodDef = {
    "name": ZeroTermStr,
    "doc": ZeroTermStr,
    "meth": CInt,
    "flags": CInt,
}


class RuntimeContext:
    def __init__(self, store, memory):
        self.store = store
        self.memory = memory
        self.interop_handles = [None]  # make this a dict one day
        self.instance = None

    def bind_instance(self, instance):
        self.instance = instance

    def unwrap(self, item: int):
        return self.interop_handles[item]

    def decode(self, pointer: int):
        print(chr(memoryview(self.memory.buffer)[pointer]))
        return utf_decode(self.memory, pointer)

    def new_handle(self, item):
        handle_num = len(self.interop_handles)
        self.interop_handles.append(item)
        return handle_num

    def release_handle(self, handle_num):
        self.interop_handles[handle_num] = None

    def split_array(self, array_start, sizeof_pointer):
        return split_array(self.memory, array_start, sizeof_pointer)

    def split_struct(self, view, spec):
        p = {}
        pointer = 0
        for name, typ in spec.items():
            subview = view[pointer : pointer + typ.size]
            p[name] = typ.from_view(subview)
            pointer += typ.size
        return p

    def Ptr(self, address: int):
        return Ptr(self, address)


class PyMethod(NamedTuple):
    runtime: RuntimeContext
    name: str
    doc: str
    addr: int

    def call(self, args, kwargs):
        print("CALLING", self.name)
        args_handle = self.runtime.new_handle(args)
        kwargs_handle = self.runtime.new_handle(kwargs)
        res = self.runtime.instance.exports.PyUU_Call_PyMethod(
            self.addr, args_handle, kwargs_handle
        )
        self.runtime.release_handle(args_handle)
        self.runtime.release_handle(kwargs_handle)
        return res

    def __call__(self, *args, **kwargs):
        self.call(*args, **kwargs)


class Ptr:
    def __init__(self, runtime_context: RuntimeContext, offset: int):
        self.runtime_context = runtime_context
        self.offset = offset
        self.buffer = self.runtime_context.memory.buffer

    def deref_to_view(self):
        return memoryview(self.buffer)[self.offset :]

    def deref_to_str(self):
        return self.runtime_context.decode(self.offset)

    def deref_to_int(self):
        return CInt.from_view(self.deref_to_view())

    def deref_to_ptr(self):
        return Ptr(self.runtime_context, self.deref_to_int())

    def __add__(self, other: int):
        return Ptr(self.runtime_context, self.offset + other)

    def __repr__(self):
        return f"<Ptr {hex(self.offset)}>"


functions = WasmFunctions()


@functions.add()
def PyUUModule_Create__impl(
    runtime_context,
    ctx: int,
    name: strptr,
    doc: strptr,
    module_defines: ptr,
    sizeof_pointer: int,
    sizeof_kind: int,
) -> int:
    name = runtime_context.decode(name)
    doc = runtime_context.decode(doc)
    module = types.ModuleType(name, doc=doc)
    pointer_views = runtime_context.split_array(module_defines, sizeof_pointer)
    pointers_as_ints = [CInt.from_view(ptr) for ptr in pointer_views]
    pointer_objs = [runtime_context.Ptr(ptr) for ptr in pointers_as_ints]

    for pointer in pointer_objs:
        kind = pointer.deref_to_int()

        if kind == HPyDef_Kind.HPyDef_Kind_Meth.value:
            sub_struct_pointer = pointer + sizeof_kind
            func = create_function(runtime_context, sub_struct_pointer)
            setattr(module, func.__name__, func)

    return runtime_context.new_handle(module)


def create_function(runtime_context, sub_struct_pointer):
    size_of_pointer = 4  # FIXME
    impl_addr = sub_struct_pointer.offset
    name = sub_struct_pointer.deref_to_ptr().deref_to_str()

    sub_struct_pointer = sub_struct_pointer + size_of_pointer
    doc = sub_struct_pointer.deref_to_ptr().deref_to_str()

    sub_struct_pointer = sub_struct_pointer + size_of_pointer
    method = PyMethod(runtime_context, name, doc, impl_addr)

    def proxy(*args, **kwargs):
        # todo: add *args, **kwargs
        return method.call(args, kwargs)

    proxy.__name__ = name
    proxy.__doc__ = doc
    print("SETTING", name, proxy)
    return proxy


@functions.add()
def PyUUType_FromSpec(runtime_context, ctx: int, spec: voidptr, params: voidptr) -> int:
    sizeof_spec = ctypes.sizeof(HPyType_Spec)
    struct_view = runtime_context.Ptr(spec).deref_to_view()[0:sizeof_spec]
    struct_obj = HPyType_Spec.from_buffer_copy(struct_view)
    nameptr = runtime_context.Ptr(struct_obj.name)
    name = nameptr.deref_to_str()

    return runtime_context.new_handle(type(name, (), {}))


@functions.add()
def PyUUDebug__impl(runtime_context, ptr: strptr):
    print(runtime_context.decode(ptr))


@functions.add()
def PyUUSetAttr_s(runtime_context, ctx: int, obj: int, name: strptr, value: int) -> int:
    try:
        obj = runtime_context.unwrap(obj)
        print("NAME", name)
        name = runtime_context.decode(name)
        value = runtime_context.unwrap(value)
        print("Setting", name, "to", value, "on", obj)
        setattr(obj, name, value)
        return 0
    except Exception:
        traceback.print_exc()
        return -1


def initialize_module(wasm_file, store: Store = None):
    # wasm = get_implementation("wasmer")
    # print(wasm)
    # Let's define the store, that holds the engine, that holds the compiler.
    store = store or Store()

    # add in some memory
    memory = Memory(store, MemoryType(minimum=2, shared=False))

    runtime_context = RuntimeContext(store, memory)

    # Let's compile the module to be able to execute it
    # Note that this is a WebAssembly module which COULD
    # export more than one Python modules.
    module = Module(store, open(wasm_file, "rb").read())

    wasi_version = wasi.get_version(module, strict=False)
    wasi_env = wasi.StateBuilder(wasm_file).finalize()
    import_object = wasi_env.generate_import_object(store, wasi_version)
    import_object.register(
        "env", {"memory": memory, **functions.bind(store, runtime_context)}
    )
    instance = Instance(module, import_object)
    runtime_context.bind_instance(instance)
    runtime_context.memory = instance.exports.memory

    ctx = instance.exports.PyUUGetContext()
    instance.exports.test_print()
    module = runtime_context.unwrap(instance.exports.HPyInit_pof(ctx))
    return module
