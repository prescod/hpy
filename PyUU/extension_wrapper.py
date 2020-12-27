import ctypes

from PyUU.API import functions

from wasmer import (
    Store,
    Memory,
    Module,
    wasi,
    Instance,
    MemoryType,
)

from .wasm_helpers import utf_decode, split_array

handle = voidptr = strptr = ptr = int


class UNUSED:
    "Repesents a free handle."
    pass


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
        return utf_decode(self.memory, pointer)

    def new_handle(self, item):
        handle_num = len(self.interop_handles)
        self.interop_handles.append(item)
        return handle_num

    def release_handle(self, handle_num):
        self.interop_handles[handle_num] = None

    def resolve_handle(self, handle_num):
        return self.interop_handles[handle_num]

    def has_handle(self, handle_num):
        return (
            handle_num < len(self.interop_handles)
            and self.resolve_handle(handle_num) != UNUSED
        )

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
        assert isinstance(address, int)
        return Ptr(self, address)


class Ptr:
    def __init__(self, runtime_context: RuntimeContext, offset: int):
        self.runtime_context = runtime_context
        assert isinstance(offset, int)
        self.offset = offset
        self.buffer = self.runtime_context.memory.buffer

    def deref_to_view(self):
        return memoryview(self.buffer)[self.offset :]

    def deref_to_str(self):
        return self.runtime_context.decode(self.offset)

    def deref_to_int(self):
        view = self.deref_to_view()
        i = ctypes.c_int32.from_buffer_copy(view)
        return i.value

    def deref_to_ptr(self):
        return Ptr(self.runtime_context, self.deref_to_int())

    def deref_to_struct(self, struct_type):
        sizeof_spec = ctypes.sizeof(struct_type)
        struct_view = self.deref_to_view()[0:sizeof_spec]
        return struct_type.from_buffer_copy(struct_view)

    def __add__(self, other: int):
        return Ptr(self.runtime_context, self.offset + other)

    def __repr__(self):
        return f"<Ptr {hex(self.offset)}>"



def initialize_module(wasm_file, store: Store = None):
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
    runtime_context.table = instance.exports.__indirect_function_table

    ctx = instance.exports.PyUUGetContext()
    instance.exports.test_print()
    module = runtime_context.unwrap(instance.exports.HPyInit_pof(ctx))
    return module
