# pushd proof-of-concept

clang \
    --target=wasm32-unknown-wasi \
    --sysroot wasi-libc/ \
    -isysroot wasi-libc/ \
    -nostartfiles \
    -Wl,--import-memory \
    -Wl,--no-entry \
    -Wl,--export-all \
    -o tmp/pof.wasm \
    -fno-common \
    -Wall \
    -DNDEBUG -g -fwrapv -O3 \
    -DPy_LIMITED_API \
    -DHPY_UNIVERSAL_ABI -I/Users/pprescod/code/open_source/hpy/venv/wheel_builder_universal/lib/python3.8/site-packages/hpy/devel/include \
    -I/Users/pprescod/code/open_source/hpy/venv/wheel_builder_universal/lib/python3.8/site-packages/hpy/devel/include \
    -I/usr/local/include \
    -I/Users/pprescod/code/open_source/hpy/hpy/universal/src \
    -I/Users/pprescod/code/open_source/hpy/venv/wheel_builder_universal/include \
    -I/usr/local/Cellar/python@3.8/3.8.6_2/Frameworks/Python.framework/Versions/3.8/include/python3.8 \
    ./proof-of-concept/pof.c hpy/devel/src/runtime/argparse.c ./proof-of-concept/PyUU.c\
    -Wl,--allow-undefined-file=PyUU.syms

python wasmplay.py
# clang -Wno-unused-result -Wsign-compare -Wunreachable-code \
#     --target=wasm32-unknown-wasi \
#     -nostartfiles   \
#     -fno-common \
#     -Wl,--import-memory -Wl,--no-entry -Wl,--export-all  \
#     -DNDEBUG -g -fwrapv -O3 \
#     --sysroot ../wasi-libc/ \
#     -Wall \
#     -DHPY_UNIVERSAL_ABI \
#     -I/Users/pprescod/code/open_source/hpy/venv/wheel_builder_universal/lib/python3.8/site-packages/hpy/devel/include \
#     -I/usr/local/include \
#     -I/usr/local/opt/openssl@1.1/include -I/usr/local/opt/sqlite/include \
#     -I/Users/pprescod/code/open_source/hpy/venv/wheel_builder_universal/include \
#     -I/usr/local/Cellar/python@3.8/3.8.6_2/Frameworks/Python.framework/Versions/3.8/include/python3.8 \
#     -c pofpackage/foo.c \
#     -o build/temp.wasm-32-3.8/pofpackage/foo.wasm
# popd
