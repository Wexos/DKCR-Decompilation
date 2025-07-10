import sys
import util

SPECIAL_NAME_TABLE = {
    "__pl": "operator+",
    "__mi": "operator-",
    "__ml": "operator*",
    "__dv": "operator/",
    "__md": "operator%",
    "__er": "operator^",
    "__adv": "operator/=",
    "__ad": "operator&",
    "__or": "operator|",
    "__co": "operator~",
    "__nt": "operator!",
    "__as": "operator=",
    "__lt": "operator<",
    "__gt": "operator>",
    "__apl": "operator+=",
    "__ami": "operator-=",
    "__amu": "operator*=",
    "__amd": "operator%=",
    "__aer": "operator^=",
    "__aad": "operator&=",
    "__aor": "operator|=",
    "__ls": "operator<<",
    "__rs": "operator>>",
    "__ars": "operator>>=",
    "__als": "operator<<=",
    "__eq": "operator==",
    "__ne": "operator!=",
    "__le": "operator<=",
    "__ge": "operator>=",
    "__aa": "operator&&",
    "__oo": "operator||",
    "__pp": "operator++",
    "__mm": "operator--",
    "__cl": "operator()",
    "__vc": "operator[]",
    "__rf": "operator->",
    "__cm": "operator,",
    "__rm": "operator->*",
    "__vt": "VTable"
}

PRIMITIVE_TYPES = {
    "b": "bool",
    "c": "char",
    "w": "wchar_t",
    "s": "short",
    "i": "int",
    "l": "long",
    "x": "long long",
    "f": "float",
    "d": "double",
    "v": "void",
    "e": "..."
}

NODE_PREFIXES = {
    "C": "const",
    "U": "unsigned",
    "S": "signed"
}

NODE_SUFFIXES = {
    "P": "*",
    "R": "&"
}

class DemanglerException(Exception):
    pass

def is_integral(node):
    if not node:
        return False

    for c in node:
        if c != "-" and (c < "0" or c > "9"):
            return False

    return True

def separate_template(node):
    template_start = node.find("<")

    if template_start == -1:
        return node, ""

    return node[0:template_start], node[template_start:]

def try_demangle_templates(node):
    name, template = separate_template(node)

    if not template:
        return name
    
    types = []
    level = 0
    current_type = ""

    for c in template:                
        if c == "<":
            level += 1

            if level == 1:
                continue

        if c == ">":
            if level == 1:
                types.append(current_type)
                current_type = ""
                continue

            level -= 1

        if c == "," and level == 1:
            types.append(current_type)
            current_type = ""
            continue
 
        current_type += c            

    types_str = []
    
    for type_name in types:
        if is_integral(type_name):
            types_str.append(type_name)
        else:
            type_node, rest = demangle_node(type_name)
            assert len(rest) == 0

            types_str.append(type_node)

    result = name

    result += "<"
    result += ", ".join(types_str)
    result += ">"            

    return result

def demangle_func_args(rest):
    args = []
    return_type = None

    while len(rest) > 0:
        if rest[0] == "_":
            rest = rest[1:]
            return_type, rest = demangle_node(rest)

            break

        arg, rest = demangle_node(rest)
        args.append(arg)

    return args, return_type, rest

def demangle_node(rest):
    pre = []
    post = []

    while True:
        if rest[0] in NODE_PREFIXES:
            pre.append(NODE_PREFIXES[rest[0]])
        elif rest[0] in NODE_SUFFIXES:
            post.append(NODE_SUFFIXES[rest[0]])
        else:
            break
        
        rest = rest[1:]

    if rest[0] in PRIMITIVE_TYPES:
        node = PRIMITIVE_TYPES[rest[0]]
        rest = rest[1:]
    elif rest[0] == "Q":
        depth = int(rest[1])
        rest = rest[2:]

        components = []

        for _ in range(depth):
            inner_node, rest = demangle_node(rest)
            components.append(inner_node)

        node = "::".join(components)
    elif rest[0] == "A":
        rest = rest[1:]
        count_str = ""

        while rest[0] != "_":
            count_str += rest[0]
            rest = rest[1:]

        rest = rest[1:]

        count = int(count_str)
        type_name, rest = demangle_node(rest)
        
        node = f"{type_name}[{count}]"
    elif rest[0] == "F":
        rest = rest[1:]

        args, return_type, rest = demangle_func_args(rest)
        args_str = ", ".join(args)

        node = ""

        if return_type is not None:
            node += f"{return_type} "

        node += f"()({args_str})"

        if pre == ["const"]:
            pre = []
            post.append(" const")

    elif rest[0] == "M":
        rest = rest[1:]
        namespace, rest = demangle_node(rest)
        is_const_func = False
        
        if rest[0] == "C":
            is_const_func = True
            rest = rest[1:]

        if rest[0] != "F":
            raise DemanglerException("Error! Expection F after member.")

        rest = rest[1:]

        args, return_type, rest = demangle_func_args(rest)
        args_str = ", ".join(args)

        node = ""

        if return_type is not None:
            node += f"{return_type} "

        node += f"({namespace}::*)({args_str})"

        if is_const_func:
            node += " const"
    elif rest[0].isdigit():
        node_length_str = ""

        while rest[0].isdigit():
            node_length_str += rest[0]
            rest = rest[1:]

        node_length = int(node_length_str)
        node = rest[0:node_length]
        node = try_demangle_templates(node)

        rest = rest[node_length:]
    else:
        raise DemanglerException(f"Error! Invalid node: {rest}")
        
    result = ""

    if len(pre) > 0:
        result += " ".join(pre)
        result += " "

    result += node

    if len(post) > 0:
        result += "".join(post)

    return result, rest

def demangle_name(name, namespace):
    name = try_demangle_templates(name)
    name, template = separate_template(name)
    
    if name in SPECIAL_NAME_TABLE:
        name = SPECIAL_NAME_TABLE[name]
    elif name in { "__ct", "__dt" }:
        class_index = namespace.rfind("::")

        if class_index == -1:
            class_name = namespace
        else:
            class_name = namespace[class_index + len("::"):]
            
        class_name, _ = separate_template(class_name)

        if name == "__ct":
            name = class_name
        elif name == "__dt":
            name = f"~{class_name}"

    return f"{name}{template}"

def demangle_symbol(symbol):
    name_end = symbol.rfind("__")

    if name_end <= 0:
        return symbol

    name_mangled = symbol[0:name_end]
    rest = symbol[name_end + 2:]

    is_const_func = False
    has_func = False
    namespace = None

    while len(rest) > 0:
        if rest[0] == "F":
            has_func = True
            rest = rest[1:]
            break
        elif rest[0] == "C":
            is_const_func = True
            rest = rest[1:]
        else:
            namespace, rest = demangle_node(rest)

    arguments = []
    return_type = None

    if has_func:
        arguments, return_type, rest = demangle_func_args(rest)
        assert len(rest) == 0

    result = ""

    if return_type is not None:
        result += f"{return_type} "

    if namespace is not None:
        result += f"{namespace}::"

    result += demangle_name(name_mangled, namespace)

    if has_func:
        result += "("
        result += ", ".join(arguments)
        result += ")"

        if is_const_func:
            result += " const"

    return result

def main(args):
    for symbol in args:
        demangled = demangle_symbol(symbol)
        print(demangled)

def run_tests():
    TESTS = {
        "__ct__Q214NrvTakeOutStar18TakeOutStarNrvAnimFv":                                           "NrvTakeOutStar::TakeOutStarNrvAnim::TakeOutStarNrvAnim(void)",
        "__dt__18MorphItemNeoTeresaFv":                                                             "MorphItemNeoTeresa::~MorphItemNeoTeresa(void)",
        "execute__Q214NrvDemoStarter18DemoStarterNrvTermCFP5Spine":                                 "NrvDemoStarter::DemoStarterNrvTerm::execute(Spine*) const",
        "ARCOpen":                                                                                  "ARCOpen",
        "setAllAnimFrameAtEnd__2MRFPC9LiveActorPCc":                                                "MR::setAllAnimFrameAtEnd(const LiveActor*, const char*)",
        "makeMtxRotate__2MRFPA4_ffff":                                                              "MR::makeMtxRotate(float[4]*, float, float, float)",
        "clone__Q22MR63FunctorV0M<P18SimpleBreakableObj,M18SimpleBreakableObjFPCvPv_v>CFP7JKRHeap": "MR::FunctorV0M<SimpleBreakableObj*, void (SimpleBreakableObj::*)(const void*, void*)>::clone(JKRHeap*) const",
        "__ct__20NPCParameterRange<f>FPCcPfff":                                                     "NPCParameterRange<float>::NPCParameterRange(const char*, float*, float, float)",
        "JPASetLineWidth__FP18JPAEmitterWorkData":                                                  "JPASetLineWidth(JPAEmitterWorkData*)",
        "findElement<l>__8JMapInfoCFPCcli_12JMapInfoIter":                                          "JMapInfoIter JMapInfo::findElement<long>(const char*, long, int) const",
        "end__Q27JGadget27TLinkList<10JUTConsole,-24>Fv":                                           "JGadget::TLinkList<JUTConsole, -24>::end(void)",
        "__ct<i>__Q29JGeometry8TVec3<f>Fiii_Pv":                                                    "void* JGeometry::TVec3<float>::TVec3<int>(int, int, int)",

        "__vt__11TalkBalloon":                                                                      "TalkBalloon::VTable",
        "__vt__Q219NrvTalkBalloonEvent24TalkBalloonEventNrvClose":                                  "NrvTalkBalloonEvent::TalkBalloonEventNrvClose::VTable",
        "sCameraTable__12CameraHolder":                                                             "CameraHolder::sCameraTable"
    }

    result = []
    
    for value, expected in TESTS.items():
        demangled = demangle_symbol(value)

        result.append([expected, demangled, expected == demangled])

    util.print_table(["Expected", "Actual", "Passed"], result)
    
if __name__ == "__main__":
    if "--test" in sys.argv:
        run_tests()
    else:
        main(sys.argv[1:])
