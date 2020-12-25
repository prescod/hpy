from typing import Union, List
from types import FunctionType as PythonFunction

import traceback
import functools

from wasmer import Memory, Store
from wasmer import Function as WasmerFunction , FunctionType as WasmerFunctionType


def split_array(
    memory_or_view: Union[memoryview, Memory], base: int, size_t: int
) -> List[memoryview]:
    if hasattr(memory_or_view, "buffer"):
        view = memoryview(memory_or_view.buffer)
    else:
        view = memory_or_view

    parts = []

    pointer = base

    while any(view[pointer:pointer + size_t]):
        parts.append(view[pointer:pointer + size_t])
        pointer += size_t

    return parts


def utf_decode(memory_or_view: Union[memoryview, Memory], base: int):
    byts = split_array(memory_or_view, base, 1)
    bytestring = b"".join(byts)
    return bytestring.decode("utf-8")


class WasmFunctions:
    def __init__(self):
        self.functions = {}

    def add(self, functype: WasmerFunctionType = None, *args, **kwargs):
        def decorator(function: PythonFunction):
            self.functions[function.__name__] = function
            function.wasm_type = functype
            return function

        return decorator

    def bind(self, store: Store, context):
        return {
            name: wasmfunc(store, func, context)
            for name, func in self.functions.items()
        }


# exception handling would be nice but its a pain to implement
# until I have a version of clang with multi-value support.
# I'm building with llvm@9 for "reasons"
def wasmfunc(store: Store, func: PythonFunction, context) -> WasmerFunction:
    @functools.wraps(func)
    def wrapped_func(*args, **kwargs):
        try:
            return func(context, *args, **kwargs)
        except Exception:
            traceback.print_exc()

    return WasmerFunction(store, wrapped_func, func.wasm_type)
