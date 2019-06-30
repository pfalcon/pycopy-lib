import sys
import asdl


t = asdl.parse(sys.argv[1])
for dfn in t.dfns:
    print("class %s(AST): pass" % dfn.name)
    #print("#", dfn.value)
    if isinstance(dfn.value, asdl.Sum):
        for typ in dfn.value.types:
            print("class %s(%s): pass" % (typ.name, dfn.name))
    elif isinstance(dfn.value, asdl.Product):
        pass
    else:
        assert 0
