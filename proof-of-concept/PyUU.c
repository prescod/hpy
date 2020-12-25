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

extern int PyUUModule_Create__impl(unsigned int ctx, const char *name, const char *doc, HPyDef *module_defines[], int sizeof_pointer, int sizeof_kind);
HPy PyUUModule_Create(HPyContext ctx, HPyModuleDef *mdef){
    PyUUDebug("FIRST DEFINITION: %p, NAME POINTER %p", &mdef->defines[0]->kind, mdef->defines[0]->meth.name);
    return (HPy){PyUUModule_Create__impl((int)ctx, mdef->m_name, mdef->m_doc, mdef->defines, sizeof(HPyDef *), sizeof(HPyDef_Kind))};
}

extern HPy PyUUType_FromSpec(HPyContext ctx, HPyType_Spec *spec, HPyType_SpecParam *params);

extern int PyUUSetAttr_s(HPyContext ctx, HPy obj, const char *name, HPy value);

extern HPy PyUUGetContext(void){
    HPyContext ctx = calloc(1, sizeof *ctx);
    ctx->ctx_Module_Create = PyUUModule_Create;
    ctx->ctx_Type_FromSpec = PyUUType_FromSpec;
    ctx->ctx_SetAttr_s = PyUUSetAttr_s;
    return (HPy){(long)ctx};
}

extern int PyUU_Call_PyMethod(int addr, int args, int kwargs){
    HPyMeth *method = (HPyMeth *)addr;
    PyUUDebug("Mocking call to func %s with %p and %p ", method->name, args, kwargs);
    // method->impl()
    return 10;
}

extern void test_print() {
    PyUUDebug("AAAA, BBBB, %d %d %d %ld", LONG_BIT, SIZEOF_LONG, sizeof(long), LONG_MAX );
}

// extern PyUUMethod_Call(HPy *function, HPy *args, HPy *kwargs){
//     PyUUDebug("%p %p %p", function, args, kwargs);
// }

