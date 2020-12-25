from PyUU.extension_wrapper import initialize_module

module = initialize_module("./tmp/pof.wasm")
print(module)
print(module.Point)
point = module.Point()
print(point)
assert module.do_nothing() is None
# print()