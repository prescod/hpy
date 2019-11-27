
/*
   DO NOT EDIT THIS FILE!

   This file is automatically generated by tools/autogen.py from tools/public_api.h.
   Run this to regenerate:
       make autogen

*/

struct _HPyContext_s {
    int ctx_version;
    HPy h_None;
    HPy h_True;
    HPy h_False;
    HPy h_ValueError;
    HPy h_TypeError;
    HPy (*ctx_Module_Create)(HPyContext ctx, HPyModuleDef *def);
    HPy (*ctx_Dup)(HPyContext ctx, HPy h);
    void (*ctx_Close)(HPyContext ctx, HPy h);
    HPy (*ctx_Long_FromLong)(HPyContext ctx, long value);
    long (*ctx_Long_AsLong)(HPyContext ctx, HPy h);
    HPy (*ctx_Float_FromDouble)(HPyContext ctx, double v);
    int (*ctx_Arg_Parse)(HPyContext ctx, HPy *args, HPy_ssize_t nargs, const char *fmt, va_list _vl);
    HPy (*ctx_Number_Add)(HPyContext ctx, HPy x, HPy y);
    void (*ctx_Err_SetString)(HPyContext ctx, HPy type, const char *message);
    int (*ctx_Bytes_Check)(HPyContext ctx, HPy o);
    HPy_ssize_t (*ctx_Bytes_Size)(HPyContext ctx, HPy o);
    HPy_ssize_t (*ctx_Bytes_GET_SIZE)(HPyContext ctx, HPy o);
    char *(*ctx_Bytes_AsString)(HPyContext ctx, HPy o);
    char *(*ctx_Bytes_AS_STRING)(HPyContext ctx, HPy o);
    HPy (*ctx_Unicode_FromString)(HPyContext ctx, const char *utf8);
    int (*ctx_Unicode_Check)(HPyContext ctx, HPy o);
    HPy (*ctx_Unicode_AsUTF8String)(HPyContext ctx, HPy o);
    HPy (*ctx_Unicode_FromWideChar)(HPyContext ctx, const wchar_t *w, HPy_ssize_t size);
    HPy (*ctx_List_New)(HPyContext ctx, HPy_ssize_t len);
    int (*ctx_List_Append)(HPyContext ctx, HPy list, HPy item);
    HPy (*ctx_Dict_New)(HPyContext ctx);
    int (*ctx_Dict_SetItem)(HPyContext ctx, HPy dict, HPy key, HPy val);
    HPy (*ctx_FromPyObject)(HPyContext ctx, struct _object *obj);
    struct _object *(*ctx_AsPyObject)(HPyContext ctx, HPy h);
    struct _object *(*ctx_CallRealFunctionFromTrampoline)(HPyContext ctx, struct _object *self, struct _object *args, void *func, int ml_flags);
};
