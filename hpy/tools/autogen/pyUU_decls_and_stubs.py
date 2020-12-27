from .autogenfile import AutoGenFile
from .parse import toC


class autogen_decls_h_PyUU(AutoGenFile):
    PATH = "hpy/devel/include/wasm/autogen_wasm_trampoline.h"
    LANGUAGE = "C"
    NO_TRAMPOLINES = set([])

    def generate(self):
        lines = []
        for func in self.api.functions:
            trampoline = self.gen_trampoline(func)
            if trampoline:
                lines.append(trampoline)
                lines.append("")
        return "\n".join(lines)

    def gen_trampoline(self, func):
        # static inline HPy HPyModule_Create(
        #               HPyContext ctx, HPyModuleDef *def);
        if func.name in self.NO_TRAMPOLINES:
            return None
        parts = []
        w = parts.append
        w("extern")
        w(toC(func.node))
        w(";")
        return " ".join(parts)


class autogen_linker_symbols_h_PyUU(AutoGenFile):
    PATH = "hpy/devel/include/wasm/API.syms"

    def generate(self):
        extra_syms = [
            "PyUUDebug__impl",
            "PyUUType_FromSpec",
            "PyUUSetAttr_s",
            "PyUUDup",
            "PyUUAdd",
            "PyUULong_AsLong",
            "PyUULong_FromLong",
            "PyUULong_AsUnsignedLongLong",
        ]
        names = [func.name for func in self.api.functions] + extra_syms
        return "\n".join(names)


class autogen_python_fallbacks(AutoGenFile):
    PATH = "PyUU/PyUU_fallbacks.py"
    LANGUAGE = "Python"

    NO_TRAMPOLINES = set([])

    def generate(self):
        lines = []
        w = lines.append

        w(
            """
from wasmer import Type

from PyUU.wasm_helpers import WasmFunctions


fallback_functions = WasmFunctions()

    """
        )

        # generate stubs for all the API functions
        for func in self.api.functions:
            w(self.stub(func))
        return "\n".join(lines)

    def stub(self, func):
        signature = toC(func.node)
        if func.is_varargs():
            return "# %s" % signature

        def argdecl(name):
            if name == "def":
                name = "_def"
            return f"{name}: int"

        argnames = [argdecl(p.name) for p in func.node.type.args.params]
        argnames.insert(0, "runtime")
        lines = []
        w = lines.append
        w(f"@fallback_functions.add()  # {signature}")
        rettype = toC(func.node.type.type)
        if rettype == "void":
            rc = ""
        elif "long long" in rettype:
            return f"## not supported for now {func}"
        else:
            rc = " -> int"
        argnames = ", ".join(argnames)
        w(f"def {func.name}({argnames}){rc}:")
        w(f"    raise NotImplementedError({func.name})")
        w("")
        return "\n".join(lines)


class autogen_ctx_vtable(AutoGenFile):
    PATH = "hpy/devel/include/wasm/autogen_wasm_vtable.h"
    LANGUAGE = "C"

    NO_TRAMPOLINES = set([])

    def generate(self):
        lines = []
        w = lines.append
        for func in self.api.functions:
            name = func.name
            if name.startswith("_"):
                continue
            ctx_name = name.replace("HPy_", "ctx_")
            ctx_name = ctx_name.replace("HPy", "ctx_")
            
            w(f"ctx->{ctx_name} = {name};")

        return "\n".join(lines)
