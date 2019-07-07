import sys
import asdl


t = asdl.parse(sys.argv[1])
for dfn in t.dfns:
    #print("#", dfn.value)
    if isinstance(dfn.value, asdl.Sum):
        print("class %s(AST): pass" % dfn.name)
        for typ in dfn.value.types:
            print("class %s(%s):" % (typ.name, dfn.name))
            print("    _fields = %s" % repr(tuple([f.name for f in typ.fields])))
    elif isinstance(dfn.value, asdl.Product):
        print("class %s(AST):" % dfn.name)
        print("    _fields = %s" % repr(tuple([f.name for f in dfn.value.fields])))
    else:
        assert 0
