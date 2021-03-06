#!/bin/bash
set -e
ROOT=`pwd` # we expect this script to be run from the repo root

_install_hpy() {
    echo "Installing hpy"
    # at the moment this install hpy.devel and hpy.universal. Eventually, we
    # will want to split those into two separate packages
    PYTHON="$1"
    pushd ${ROOT}
    ${PYTHON} -m pip install wheel
    ${PYTHON} -m pip install .
    popd
}

_test_pof() {
    echo "==== testing pof ===="
    # this assumes that pof is already installed, e.g. after calling
    # wheel or setup_py_install
    python3 -m pip install pytest pytest-azurepipelines
    cd proof-of-concept
    python3 -m pytest
}

_build_wheel() {
    HPY_ABI="$1"
    VENV="venv/wheel_builder_$HPY_ABI"
    # we use this venv just to build the wheel, and then we install the wheel
    # in the currently active virtualenv
    echo "Create venv: $VENV"
    python3 -m venv "$VENV"
    PY_BUILDER="`pwd`/$VENV/bin/python3"
    echo
    echo "Installing hpy and requirements"
    _install_hpy ${PY_BUILDER}
    pushd proof-of-concept
    ${PY_BUILDER} -m pip install -r requirements.txt
    echo
    echo "Building wheel"
    ${PY_BUILDER} setup.py --hpy-abi="$HPY_ABI" bdist_wheel
    popd
}

_myrm() {
    if [ -d "$1" ]
    then
        echo "rm $1"
        rm -rf "$1"
    else
        echo "skipping $1"
    fi
}

clean() {
    echo "=== cleaning up old stuff ==="
    _myrm ${ROOT}/venv/wheel_builder_cpython
    _myrm ${ROOT}/venv/wheel_builder_universal
    _myrm ${ROOT}/venv/wheel_runner_cpython
    _myrm ${ROOT}/venv/wheel_runner_universal
    _myrm ${ROOT}/venv/setup_py_install_cpython
    _myrm ${ROOT}/venv/setup_py_install_universal
    _myrm ${ROOT}/build
    _myrm ${ROOT}/proof-of-concept/build
    _myrm ${ROOT}/proof-of-concept/dist
    echo
}

wheel() {
    # build a wheel, install and test
    HPY_ABI="$1"
    VENV="venv/wheel_runner_$HPY_ABI"
    clean
    echo "=== testing setup.py bdist_wheel ==="
    _build_wheel "$HPY_ABI"
    WHEEL=`ls proof-of-concept/dist/*.whl`
    echo "Wheel created: ${WHEEL}"
    echo
    echo "Create venv: $VENV"
    python3 -m venv "$VENV"
    source "$VENV/bin/activate"
    echo "Installing wheel"
    python3 -m pip install $WHEEL
    echo
    _test_pof
}

setup_py_install() {
    # install proof-of-concept using setup.py install and run tests
    HPY_ABI="$1"
    VENV="venv/setup_py_install_$HPY_ABI"
    clean
    echo "=== testing setup.py --hpy-abi=$HPY_ABI install ==="
    echo "Create venv: $VENV"
    python3 -m venv "$VENV"
    source "$VENV/bin/activate"
    _install_hpy python
    echo
    echo "Running setup.py"
    pushd proof-of-concept
    python3 setup.py --hpy-abi="$HPY_ABI" install
    popd
    echo
    _test_pof
}

# ======== main code =======

# call the function mentioned as the first arg
COMMAND="$1"
shift
$COMMAND "$@"
