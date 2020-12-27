#ifndef HPy_H
#define HPy_H

#ifdef HPY_WASM_ABI
#    include "wasm/hpy.h"
#elif HPY_UNIVERSAL_ABI
#    include "universal/hpy.h"
#else
#    include "cpython/hpy.h"
#endif

#endif /* HPy_H */
