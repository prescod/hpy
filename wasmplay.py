from PyUU.extension_wrapper import initialize_module

module = initialize_module("./tmp/pof.wasm")
print(module)
print("Nothing", module.do_nothing())
print("Twice Seven", module.double(7))
print("Twice Zero", module.double(0))
print("Twice Big", module.double(10 ** 50))
print("Add Ints", module.add_ints(20, 30))
print("Add Ints KW", module.add_ints_kw(b=20, a=20))
print(module.Point)
point = module.Point(3, 4)
print(point)
# print()