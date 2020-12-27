#include "pyconfig.h"
#include "hpy.h"
#include <stdio.h>
#include "pyport.h"

extern void PyUUDebug__impl(const char *value);
extern void PyUUDebug ( const char * format, ... )
{
  char buffer[1024];
  va_list args;
  va_start(args, format);
  vsprintf(buffer, format, args);
  PyUUDebug__impl (buffer);
  va_end (args);
}

extern HPy PyUUGetContext(void){
    HPyContext ctx = calloc(1, sizeof *ctx);
    #include "wasm/autogen_wasm_vtable.h"
    return (HPy){(long)ctx};
}


// Exception handling???
extern void test_print() {
    PyUUDebug("Print worked");
}

extern HPy PyUU_Call_HPyFunc_NOARGS(HPyContext ctx, HPyFunc_noargs func, HPy self){
    return func(ctx, self);
}

extern HPy PyUU_Call_HPyFunc_O(HPyContext ctx, HPyFunc_o func, HPy self, HPy obj){
    return func(ctx, self, obj);
}

extern HPy PyUU_Call_HPyFunc_VARARGS(HPyContext ctx, HPyFunc_varargs func, HPy self, HPy args[], int nargs){
    return func(ctx, self, args, nargs);
}

extern HPy PyUU_Call_HPyFunc_KEYWORDS(HPyContext ctx, HPyFunc_keywords func, HPy self, HPy *args, HPy_ssize_t nargs, HPy kw){
    return func(ctx, self, args, nargs, kw);
}
