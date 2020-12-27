import types
import traceback

from ctypes import c_int32

from .wasm_helpers import WasmFunctions
from .PyCTypes import HPyModuleDef, SIZEOF_POINTER, PyMethod
from .PyCTypes import HPyDef_Kind, SIZEOF_KIND, HPyMeth
from .PyCTypes import voidptr, HPyType_Spec, handle, strptr
functions = WasmFunctions()


@functions.add()
def PyUUModule_Create(runtime_context, ctx: int, module_def: int) -> int:
    rt = runtime_context
    module_struct = rt.Ptr(module_def).deref_to_struct(HPyModuleDef)
    name = rt.Ptr(module_struct.m_name).deref_to_str()
    doc = rt.Ptr(module_struct.m_doc).deref_to_str()
    module_defines = rt.Ptr(module_struct.defines)
    pointer_views = rt.split_array(module_defines.offset, SIZEOF_POINTER)
    pointers_as_ints = [c_int32.from_buffer_copy(ptr).value for ptr in pointer_views]

    pointer_objs = [rt.Ptr(ptr) for ptr in pointers_as_ints]
    module = types.ModuleType(name, doc=doc)
    parse_methods(rt, ctx, module, pointer_objs)
    return rt.new_handle(module)


def parse_methods(runtime_context, ctx, module, pointer_objs):
    for pointer in pointer_objs:
        kind = pointer.deref_to_int()

        if kind == HPyDef_Kind.HPyDef_Kind_Meth.value:
            sub_struct_pointer = pointer + SIZEOF_KIND
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
def PyUUType_FromSpec(runtime_context, ctx: int, spec: voidptr, 
                      params: voidptr) -> int:
    type_struct = runtime_context.Ptr(spec).deref_to_struct(HPyType_Spec)
    nameptr = runtime_context.Ptr(type_struct.name)
    name = nameptr.deref_to_str()

    return runtime_context.new_handle(type(name, (), {}))


@functions.add()
def PyUUDup(runtime_context, ctx: handle, obj: handle) -> handle:
    real_obj = runtime_context.resolve_handle(obj)
    return runtime_context.new_handle(real_obj)


@functions.add()
def PyUUAdd(runtime_context, ctx: int, obj1: int, obj2: int) -> int:
    real_obj1 = runtime_context.resolve_handle(obj1)
    real_obj2 = runtime_context.resolve_handle(obj2)
    rc = real_obj1 + real_obj2
    return runtime_context.new_handle(rc)


@functions.add()
def PyUULong_AsLong(runtime_context, ctx: int, num: handle) -> int:
    number = runtime_context.resolve_handle(num)
    return number


@functions.add()
def PyUULong_FromLong(runtime_context, ctx: int, long: int) -> handle:
    number = runtime_context.new_handle(long)
    return number


@functions.add()
def PyUUDebug__impl(runtime_context, ptr: strptr):
    print(runtime_context.decode(ptr))


@functions.add()
def PyUUSetAttr_s(runtime_context, ctx: int, obj: int, 
                  name: strptr, value: int) -> int:
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
def PyUULong_AsUnsignedLongLong(runtime_context, ctx: int) -> int:
    print("PyUULong_AsUnsignedLongLong is not implemented")
