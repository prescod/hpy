#ifndef HPY_UNIVERSAL_H
#define HPY_UNIVERSAL_H

#include <stdlib.h>
#include <stdint.h>
#include <stdarg.h>

#ifdef __GNUC__
#define _HPy_HIDDEN  __attribute__((visibility("hidden")))
#else
#define _HPy_HIDDEN
#endif /* __GNUC__ */

#if defined(__clang__) || \
    (defined(__GNUC__) && \
     ((__GNUC__ >= 3) || \
      (__GNUC__ == 2) && (__GNUC_MINOR__ >= 5)))
#  define _HPy_NO_RETURN __attribute__((__noreturn__))
#elif defined(_MSC_VER)
#  define _HPy_NO_RETURN __declspec(noreturn)
#else
#  define _HPy_NO_RETURN
#endif

#define HPyAPI_RUNTIME_FUNC(restype) _HPy_HIDDEN restype

/* HPy types */
typedef intptr_t HPy_ssize_t;
typedef intptr_t HPy_hash_t;

/* The following types, when compiled with the present universal-mode header,
   are each just a pointer-sized integer.  What this integer (or pointer)
   means is up to the implementation.  For example, on both CPython and PyPy,
   the HPy structure contains an index in a global array. */
typedef struct _HPy_s { HPy_ssize_t _i; } HPy;
typedef struct { HPy_ssize_t _lst; } HPyListBuilder;
typedef struct { HPy_ssize_t _tup; } HPyTupleBuilder;
typedef struct { HPy_ssize_t _i; } HPyTracker;

typedef struct _HPyContext_s *HPyContext;

/* compatibility CPython types */
#include "common/cpy_types.h"


/* misc stuff, which should probably go in its own header */
#define HPy_NULL ((HPy){0})
#define HPy_IsNull(x) ((x)._i == 0)

// XXX: we need to decide whether these are part of the official API or not,
// and maybe introduce a better naming convention. For now, they are needed for
// ujson
static inline HPy HPy_FromVoidP(void *p) { return (HPy){(HPy_ssize_t)p}; }
static inline void* HPy_AsVoidP(HPy h) { return (void*)h._i; }

// include runtime functions
#include "common/macros.h"
#include "common/runtime/argparse.h"

#include "common/hpyfunc.h"
#include "common/hpydef.h"
#include "common/hpytype.h"
#include "common/hpymodule.h"

#include "wasm/autogen_api_decls.h"
#include "universal/autogen_ctx.h"



#endif /* HPY_UNIVERSAL_H */
