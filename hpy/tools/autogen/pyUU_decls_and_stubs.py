from .autogenfile import AutoGenFile
from .parse import toC


class autogen_decls_h_PyUU(AutoGenFile):
    PATH = "hpy/devel/include/PyUU/autogen_trampolines.h"

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
    PATH = "hpy/devel/include/PyUU/pyuu.syms"

    def generate(self):
        names = [func.name for func in self.api.functions]
        return "\n".join(names)


class autogen_python_fallbacks(AutoGenFile):
    PATH = "hpy/devel/include/PyUU/pyuu_fallbacks.py"

    NO_TRAMPOLINES = set([])

    def generate(self):
        lines = []
        w = lines.append

        w("""
def API():
    
    """)

        # generate stubs for all the API functions
        for func in self.api.functions:
            w(self.stub(func))
        return "\n".join(lines)

    def stub(self, func):
        signature = toC(func.node)
        if func.is_varargs():
            return "# %s" % signature

        def cleanup(n):
            if n == "def":
                return "_def"
            return n

        argnames = [cleanup(p.name) for p in func.node.type.args.params]
        lines = []
        w = lines.append
        w(f"@API.func()  # {signature}")
        rettype = toC(func.node.type.type)
        if rettype == "void":
            rc = "None"
        else:
            rc = "int"
        argnames = ", ".join(argnames)
        w(f"def {func.name}({argnames}) -> {rc}:")
        w(f"    raise NotImplementedError({func.name})")
        w("")
        return "\n".join(lines)
