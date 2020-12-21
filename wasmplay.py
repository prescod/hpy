import types
import traceback
import functools

from wasmer import engine, Store, Module, Instance, Memory, MemoryType, ImportObject, Uint8Array, wasi, Function
from wasmer_compiler_cranelift import Compiler


def decode(memory, base):
    view = memoryview(memory.buffer)
    cursor = base
    result = ''

    while (view[cursor] != 0):
        result += chr(view[cursor])
        cursor += 1

    return result

in_handles = [None]

# this could be written
unwrap = in_handles.__getitem__

# Let's define the store, that holds the engine, that holds the compiler.
store = Store(engine.JIT(Compiler))

# add in some memory
MEMORY = Memory(store, MemoryType(2, shared=False))

# Let's compile the module to be able to execute it!
module = Module(store, open('tmp/pof.wasm', 'rb').read())

def wasmfunc(func):
    @functools.wraps(func)
    def wrapped_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            
    return Function(store, wrapped_func)

@wasmfunc
def PyUUModule_Create__impl(ctx: int, name: int) -> int:
    print("XXX")
    handle = len(in_handles)
    print("YYY", handle)
    name = decode(MEMORY, name)
    in_handles.append(types.ModuleType(name))
    print("ZZZ", in_handles)
    return handle

@wasmfunc
def PyUUType_FromSpec__impl(ctx: int, name: int) -> int:
    print("XXX")
    handle = len(in_handles)
    print("YYY", handle)
    name = decode(MEMORY, name)
    in_handles.append(types.ModuleType(name))
    print("ZZZ", in_handles)
    return handle

@wasmfunc
def PyUUDebug__impl(base: int):
    print(decode(MEMORY, base))

@wasmfunc
def PyUUSetAttr_s__impl(ctx: int, obj: int, name: int, value: int)->int:
    print("HERE")
    try:
        print("A")
        obj = unwrap(obj)
        print("B")
        name = decode(MEMORY, name)
        print("C")
        value = unwrap(value)
        print("Setting", name, "to", value, "on", obj)
        setattr(obj, name, value)
        print("THERE")
        return 0
    except Exception:
        traceback.print_exc()
        return -1

wasi_version = wasi.get_version(module, strict=False)
wasi_env = wasi.StateBuilder('test-program').finalize()
import_object = wasi_env.generate_import_object(store, wasi_version)
import_object.register(
    "env",
    {
        "memory": MEMORY,
        "PyUUModule_Create__impl": PyUUModule_Create__impl,
        "PyUUDebug__impl": PyUUDebug__impl,
        "PyUUType_FromSpec__impl": PyUUType_FromSpec__impl,
        "PyUUSetAttr_s__impl": PyUUSetAttr_s__impl,
    }
)

# Now the module is compiled, we can instantiate it.
instance = Instance(module, import_object)
# print([(exp.name, exp.type) for exp in module.exports])
ctx = instance.exports.PyUUGetContext()
module = unwrap(instance.exports.HPyInit_pof(ctx))
print(module)
print(module.Point)

# print()