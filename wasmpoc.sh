# pushd proof-of-concept
# export PYTHONPATH=../wasmapy
/usr/local/Cellar/llvm@9/9.0.1_2/bin/clang \
    --target=wasm32-unknown-wasi \
    --sysroot /Users/pprescod/code/open_source/wasi-libc/sysroot \
    -nostartfiles \
    -Wl,--export-table \
    -Wl,--no-entry \
    -Wl,--export-all \
    -fno-common \
    -Wall \
    -DNDEBUG -g -fwrapv -O3 \
    -DPy_LIMITED_API \
    -DHPY_UNIVERSAL_ABI \
    -IPyUU/include \
    -I/Users/pprescod/code/open_source/hpy/venv/wheel_builder_universal/lib/python3.8/site-packages/hpy/devel/include \
    -I/Users/pprescod/code/open_source/hpy/venv/wheel_builder_universal/lib/python3.8/site-packages/hpy/devel/include \
    -I/Users/pprescod/code/open_source/hpy/hpy/universal/src \
    -I./hpy/devel/include/universal/ \
    -I./hpy/devel/include/ \
    -I/Users/pprescod/code/open_source/hpy/venv/wheel_builder_universal/include \
    -I/usr/local/Cellar/python@3.8/3.8.6_2/Frameworks/Python.framework/Versions/3.8/include/python3.8 \
    -Wl,--allow-undefined-file=PyUU.syms \
    ./proof-of-concept/pof.c ./proof-of-concept/PyUU.c\
    hpy/devel/src/runtime/argparse.c \
    -o tmp/pof.wasm && python wasmplay.py
# clang -Wno-unused-result -Wsign-compare -Wunreachable-code \
#     --target=wasm32-unknown-wasi \
#     -nostartfiles   \
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
