import types
import traceback

from ctypes import c_int32

from .wasm_helpers import WasmFunctions
from .PyCTypes import HPyModuleDef, SIZEOF_POINTER, PyMethod
from .PyCTypes import HPyDef_Kind, SIZEOF_ENUM, HPyMeth
from .PyCTypes import voidptr, HPyType_Spec, handle, strptr
from wasmer import Value, FunctionType, Type


functions = WasmFunctions()


@functions.add()
def HPyModule_Create(runtime_context, ctx: int, module_def: int) -> int:
    rt = runtime_context
    module_struct = rt.Ptr(module_def).deref_to_struct(HPyModuleDef)
    name = rt.Ptr(module_struct.m_name).deref_to_str()
    doc = rt.Ptr(module_struct.m_doc).deref_to_str()
    module_defines = rt.Ptr(module_struct.defines)
    pointer_views = rt.split_array(module_defines.offset, SIZEOF_POINTER)
    pointers_as_ints = [
        c_int32.from_buffer_copy(ptr).value for ptr in pointer_views
    ]

    pointer_objs = [rt.Ptr(ptr) for ptr in pointers_as_ints]
    module = types.ModuleType(name, doc=doc)
    parse_methods(rt, ctx, module, pointer_objs)
    return rt.new_handle(module)


def parse_methods(runtime_context, ctx, module, pointer_objs):
    for pointer in pointer_objs:
        kind = pointer.deref_to_int()

        if kind == HPyDef_Kind.HPyDef_Kind_Meth.value:
            sub_struct_pointer = pointer + SIZEOF_ENUM
            func = create_function(runtime_context, ctx, sub_struct_pointer)
            setattr(module, func.name, func)
        else:
            print("Can't handle", HPyDef_Kind(kind).name)


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


@functions.add()
def HPyType_FromSpec(
    runtime_context, ctx: int, spec: voidptr, params: voidptr
) -> int:
    type_struct = runtime_context.Ptr(spec).deref_to_struct(HPyType_Spec)
    defines = type_struct.defines_as_list(ctx)
    defines = {define.name: define for define in defines}
    defines["__struct__"] = type_struct
    newtype = type(type_struct.name_as_str, (), defines)
    return runtime_context.new_handle(newtype)


@functions.add()
def HPy_Dup(runtime_context, ctx: handle, obj: handle) -> handle:
    real_obj = runtime_context.resolve_handle(obj)
    rc = runtime_context.new_handle(real_obj)
    return rc


@functions.add()
def HPy_Add(runtime_context, ctx: int, obj1: int, obj2: int) -> int:
    real_obj1 = runtime_context.resolve_handle(obj1)
    real_obj2 = runtime_context.resolve_handle(obj2)
    rc = real_obj1 + real_obj2
    return runtime_context.new_handle(rc)


@functions.add()
def HPy_Long_AsLong(runtime_context, ctx: int, num: handle) -> int:
    number = runtime_context.resolve_handle(num)
    return number


@functions.add()
def HPy_Long_FromLong(runtime_context, ctx: int, long: int) -> handle:
    number = runtime_context.new_handle(long)
    return number


@functions.add()
def PyUUDebug__impl(runtime_context, ptr: strptr):
    print(runtime_context.decode(ptr))


@functions.add()
def HPy_SetAttr_s(
    runtime_context, ctx: int, obj: int, name: strptr, value: int
) -> int:
    try:
        obj = runtime_context.unwrap(obj)
        name = runtime_context.decode(name)
        value = runtime_context.unwrap(value)
        setattr(obj, name, value)
        return 0
    except Exception:
        traceback.print_exc()
        return -1


@functions.add()
def HPyLong_AsLong(runtime_context, ctx: int, num_handle: handle) -> int:
    number = runtime_context.resolve_handle(num_handle)
    return number


@functions.add()
def HPyLong_FromLong(runtime_context, ctx: int, num: int) -> int:
    number = runtime_context.new_handle(num)
    return number


@functions.add()
def HPy_GetItem_s(runtime, ctx: int, obj: handle, key: handle) -> handle:
    obj = runtime.resolve_handle(obj)
    key = runtime.decode(key)
    return runtime.new_handle(obj[key])


@functions.add()
def HPy_Close(runtime, ctx: int, h: handle):
    runtime.release_handle(h)


def PyUULong_AsUnsignedLongLong(runtime_context, ctx: int) -> int:
    assert 0, "PyUULong_AsUnsignedLongLong is not implemented"


@functions.add(
    functype=FunctionType(params=[Type.I32, Type.I32], results=[Type.I64])
)
def HPyLong_AsLongLong(
    runtime_context, ctx: int, num_handle: int
) -> Value.i64:
    number = runtime_context.resolve_handle(num_handle)
    return Value.i64(number)


@functions.add(
    functype=FunctionType(params=[Type.I32, Type.I64], results=[Type.I32])
)
def HPyLong_FromLongLong(
    runtime_context, ctx: int, num_handle: int
) -> Value.i64:
    number = runtime_context.resolve_handle(num_handle)
    return Value.i64(number)


@functions.add(
    functype=FunctionType(params=[Type.I32, Type.I32], results=[Type.I64])
)
def HPyLong_AsUnsignedLongLongMask(
    runtime_context, ctx: int, num_handle: int
) -> Value.i64:
    assert 0, "Not yet implemented"


@functions.add(
    functype=FunctionType(params=[Type.I32, Type.I32], results=[Type.I64])
)
def HPyLong_AsUnsignedLongLong(
    runtime_context, ctx: int, num_handle: int
) -> Value.i64:
    assert 0, "Not yet implemented"


@functions.add(
    functype=FunctionType(params=[Type.I32, Type.I64], results=[Type.I32])
)
def HPyLong_FromUnsignedLongLong(
    runtime_context, ctx: int, num_handle: int
) -> Value.i64:
    assert 0, "Not yet implemented"


@functions.add(
    functype=FunctionType(params=[Type.I32, Type.I32], results=[Type.F64])
)
def HPyFloat_AsDouble(runtime_context, ctx: int, num_handle: int) -> Value.i64:
    assert 0, "Not yet implemented"


@functions.add(
    functype=FunctionType(params=[Type.I32, Type.F64], results=[Type.I32])
)
def HPyFloat_FromDouble(
    runtime_context, ctx: int, num_handle: int
) -> Value.i64:
    assert 0, "Not yet implemented"


@functions.add()
def HPyUnicode_FromString(runtime_context, ctx: int, utf8: int) -> handle:
    data = runtime_context.decode(utf8)
    return runtime_context.new_handle(data)


# void HPyErr_SetString(HPyContext ctx, HPy h_type, const char *message)
@functions.add()
def HPyErr_SetString(runtime, ctx: int, h_type: int, message: int):
    data = runtime.decode(message)

    print("ERROR! Exception handling not implemented: ", data, h_type)


class BlankObject:
    pass


@functions.add()
def _HPy_New(runtime, ctx: int, h_type: handle, data: int) -> handle:
    tp = runtime.resolve_handle(h_type)
    assert isinstance(
        tp, type
    ), f"HPy_New arg 1 must be a type, not {tp}, {type(tp)}"
    obj_in_c = runtime.malloc(tp.__struct__.basicsize)
    obj_in_python = BlankObject()
    obj_in_python.__class__ = tp
    obj_in_python.__wasm_obj__ = obj_in_c
    assert data % 4 == 0
    view = runtime.memory.int32_view(offset=data // 4)
    view[0] = obj_in_c.offset
    new_handle = runtime.new_handle(obj_in_python)
    return new_handle


@functions.add()  # void *_HPy_Cast(HPyContext ctx, HPy h)
def _HPy_Cast(runtime, ctx: int, h: handle) -> voidptr:
    real_host_obj = runtime.resolve_handle(h)
    assert real_host_obj   # temporary
    if real_host_obj is None:
        return 0
    real_extension_object = real_host_obj.__wasm_obj__
    return real_extension_object.offset
