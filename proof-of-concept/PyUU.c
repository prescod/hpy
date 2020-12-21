#include "hpy.h"
#include <stdio.h>

extern int PyUUModule_Create__impl(unsigned int ctx, const char *name);
HPy PyUUModule_Create(HPyContext ctx, HPyModuleDef *mdef){
    return (HPy){PyUUModule_Create__impl((int)ctx, mdef->m_name)};
}

extern int PyUUType_FromSpec__impl(HPyContext ctx, const char *name);
HPy PyUUType_FromSpec(HPyContext ctx, HPyType_Spec *spec, HPyType_SpecParam *params){
    return (HPy){PyUUType_FromSpec__impl(ctx, spec->name)};
}

extern int PyUUSetAttr_s__impl(HPyContext ctx, HPy obj, const char *name, HPy value);
int PyUUSetAttr_s(HPyContext ctx, HPy obj, const char *name, HPy value){
    return PyUUSetAttr_s__impl(ctx, obj, name, value);
}

extern HPy PyUUGetContext(void){
    HPyContext ctx = calloc(1, sizeof *ctx);
    ctx->ctx_Module_Create = PyUUModule_Create;
    ctx->ctx_Type_FromSpec = PyUUType_FromSpec;
    ctx->ctx_SetAttr_s = PyUUSetAttr_s;
    return (HPy){(long)ctx};
}

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

extern void test_print() {
    PyUUDebug("ABCD");
}
