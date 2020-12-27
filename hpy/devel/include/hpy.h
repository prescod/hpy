#ifndef HPy_H
#define HPy_H

#ifdef HPY_WASM_ABI
#    include "wasm/hpy.h"
#elif HPY_UNIVERSAL_ABI
#    include "universal/hpy.h"
#    error "B"
#else
#    include "cpython/hpy.h"
#    error "C"
#endif

#endif /* HPy_H */
