import demangler
import random
import symbols
import sys
import util
from collections import OrderedDict

def fix_fields_read(fields):
    for i in range(len(fields)):
        fields[i] = fields[i].replace("&#44;", ",")

def fix_fields_write(fields):
    for i in range(len(fields)):
        fields[i] = fields[i].replace(",", "&#44;")

class SymbolInfo:
    def __init__(self):
        self.size = 0
        self.matches = False
        self.type = "F"
        self.library = None
        self.obj = None
        self.symbol = None

class SymbolDB:
    def __init__(self):
        self.file_name = util.ROOT_PATH / "Symbols" / "v1.1" / "USA" / "Symbols.csv"
        self.symbols = OrderedDict()

    def load(self):
        self.symbols.clear()

        with open(self.file_name, "r") as input:
            is_first_line = True

            for line in input:
                if is_first_line:
                    is_first_line = False
                    continue
                
                line_split = line.rstrip().split(",")
                fix_fields_read(line_split)

                if len(line_split) != 7:
                    print(f"Invalid line: \"{line}\"")
                    sys.exit()

                symbol = SymbolInfo()

                address = int(line_split[0], 16)
                symbol.size = int(line_split[1], 16)
                symbol.type = line_split[2]
                symbol.matches = line_split[3] == "T"
                symbol.library = line_split[4]
                symbol.obj = line_split[5]
                symbol.symbol = line_split[6]

                self.symbols[address] = symbol

    def save(self):
        self.sort()
        
        with open(self.file_name, "w") as output:
            output.write("Address,Size,Type,Decompiled,Library,Obj,Name\n")

            for address, info in self.symbols.items():
                s_address = util.hex32(address)
                s_size = util.hex24(info.size)
                s_type = info.type
                s_matches = 'T' if info.matches else 'F'
                s_lib = info.library
                s_obj = info.obj
                s_symbol = info.symbol

                fields = [s_address, s_size, s_type, s_matches, s_lib, s_obj, s_symbol]
                fix_fields_write(fields)
                                                    
                line = ",".join(fields)
                output.write(f"{line}\n")
           
    def sort(self):
        self.symbols = OrderedDict(sorted(self.symbols.items()))

    def does_address_exist(self, address):
        return address in self.symbols;

    def does_symbol_exist(self, symbol):
        for info in self.symbols.values():
            if info.symbol == symbol:
                return True

        return False
    
    def get_address_from_symbol(self, symbol):
        for address, info in self.symbols.items():
            if info.symbol == symbol:
                return address

        return None

    def get_size(self, address):
        if address in self.symbols:
            return self.symbols[address].size
            
        return 0

    def get_symbol(self, address):
        if address in self.symbols:
            return self.symbols[address].symbol
            
        return None

    def get_demangled_symbol(self, address):
        if address in self.symbols:
            mangled = self.symbols[address].symbol

            if not mangled:
                return ""

            try:
                return demangler.demangle_symbol(mangled)
            except demangler.DemanglerException:
                return None
            
        return None

    def get_sym_type(self, address):
        if address in self.symbols:
            return self.symbols[address].type
            
        return None

    def get_obj(self, address):
        if address in self.symbols:
            return self.symbols[address].obj
            
        return None

    def get_library(self, address):
        if address in self.symbols:
            return self.symbols[address].library
            
        return None

    def get_library(self, address):
        if address in self.symbols:
            return self.symbols[address].type
            
        return None

    def is_marked_decompiled(self, address):
        if address in self.symbols:
            return self.symbols[address].matches

        return False
        
    def add_function(self, address, size):
        assert not address in self.symbols
        
        info = SymbolInfo()

        info.size = size
        info.symbol = ""
        info.type = "F"
        info.obj = ""
        info.library = ""
        info.matches = False

        self.symbols[address] = info

    def set_size(self, address, size):
        self.symbols[address].size = size

    def mark_function_decompiled(self, address, decompiled):
        self.symbols[address].matches = decompiled
        
    def get_functions_marked_as_decompiled(self):
        for address, info in self.symbols.items():
            if info.matches:
                yield address

    def get_all_functions(self):
        for address in self.symbols.keys():
            yield address

    def search_functions(self, pattern):
        pattern = pattern.lower()

        for address, info in self.symbols.items():
            mangled = info.symbol

            if not mangled:
                continue

            try:
                demangled = demangler.demangle_symbol(mangled)
            except:
                continue

            if pattern in demangled.lower():
                yield address

def get_obj_display_name(obj):
    if obj:
        return f"{obj}.o"
    
    return "?"

def get_lib_display_name(lib):
    if lib:
        return lib

    return "?"

def print_help_and_exit():
    print("Usage: db.py <command> [addition flags]")
    print()

    print("To add a new function, use:")
    print("db.py add-data <address> <symbol>")
    print()

    print("To add a new function, use:")
    print("db.py add-func <address> <size> <obj> <lib>")
    print()

    print("To display this help, use:")
    print("db.py help")
    print()

    print("To print information about a function, use:")
    print("db.py func <address>")
    print()

    print("To generate a symbol map, use:")
    print("db.py gen-map <type> <path>")
    print()

    print("To print all library names, use:")
    print("db.py list-lib")
    print()

    print("To print all object file names in a specific library, use:")
    print("db.py list-obj <lib>")
    print()

    print("To print all functions in an object file, use:")
    print("db.py list-func <obj>")
    print()

    print("To move a function to a new library and object file, use:")
    print("db.py move <address> <obj> <lib>")

    print("To move multiple functions to a new library and object file, use:")
    print("db.py move-multi <first-address> <last-address> <obj> <lib>")
    print()

    print("To display random functions, use:")
    print("db.py rand-func [<n>]")
    print()

    print("To display random objects, use:")
    print("db.py rand-obj [<n>]")
    print()

    print("To rename an obj file, use:")
    print("db.py rename-obj <old-obj> <old-lib> <new-obj> <new-lib>")
    print()

    print("To search for functions, use:")
    print("db.py search-func <pattern>")
    print()

    print("To set the symbol of a function, use:")
    print("db.py set-symbol <address> <symbol>")
    print()

    print("To set the size of a function, use:")
    print("db.py set-size <address> <size>")
    print()

    print("To print a tree over all objects, use:")
    print("db.py tree")
    print()

    print("To unmark a function as decompiled, use:")
    print("db.py unmark <address>")
    print()

    print("To unset the symbol of a funtion, use:")
    print("db.py unset-symbol <address>")
    print()

    print("To validate the databases, use:")
    print("db.py validate")
    print()


    sys.exit()

def add_data(data_db, args):
    if len(args) != 2:
        print_help_and_exit()
        
    address = int(args[0], 16)
    symbol = args[1]

    if data_db.does_address_exist(address):
        print("Address already exists.")
        return

    print("Not implemented")
    #data_db.add_symbol(address, symbol)

def func_info(sym_db, args):
    if len(args) != 1:
        print_help_and_exit()

    address = int(args[0], 16)

    if not sym_db.does_address_exist(address):
        print("Function does not exist.")
        return

    print(f"Declaration:   {sym_db.get_demangled_symbol(address)}")
    print(f"Mangled:       {sym_db.get_symbol(address)}")
    print(f"Address:       {util.hex32(address)}")
    print(f"Size:          {util.hex24(sym_db.get_size(address))}")
    print(f"Library:       {get_lib_display_name(sym_db.get_library(address))}")
    print(f"Obj:           {get_obj_display_name(sym_db.get_obj(address))}")

def gen_map(sym_db, args):
    if len(args) != 2:
        print_help_and_exit()
        
    symbol_type = args[0].lower()
    file_name = args[1]

    TYPES = ["cw", "ghidra", "spacemine"]
    
    with open(file_name, "w") as output:
        if symbol_type == "cw":
            output.write(".text section layout\n")
            output.write("  Starting        Virtual\n")
            output.write("  address  Size   address\n")

            TEXT1_ADDRESS = 0x80006EA0

            for address in sym_db.get_all_functions():
                symbol = sym_db.get_symbol(address)

                if not symbol:
                    continue

                text1_offset = address - TEXT1_ADDRESS
                size = sym_db.get_size(address)

                output.write(f"  {util.hex32(text1_offset)} {util.hex24(size)} {util.hex32(address)} {util.hex32(0)}: {symbol}\n")
        elif symbol_type == "ghidra":
            for address in sym_db.get_all_functions():
                symbol = sym_db.get_symbol(address)

                if not symbol:
                    continue

                try:
                    demangled = demangler.demangle_symbol(symbol)
                    name = demangled.replace(" ", "")
                except:
                    name = symbol

                symbol_type = sym_db.get_sym_type(address)

                if symbol_type == "F":
                    type = "f"
                elif symbol_type == "D":
                    type = "l"
                else:
                    continue

                output.write(f"{name} {util.hex32(address)} {type}\n")

        elif symbol_type == "spacemine":
            for address in sym_db.get_all_functions():
                symbol = sym_db.get_symbol(address)

                if not symbol:
                    continue

                output.write(f"{util.hex32(address)} {symbol}\n")
        else:
            types_string = ", ".join(TYPES)
            print(f"Invalid symbol map type. Must be one of the following: {types_string}")
        
def list_libs(sym_db, args):
    if len(args) > 0:
        print_help_and_exit()

    libs = set()
    lib_objs = dict()
    lib_func = dict()

    for address in sym_db.get_all_functions():
        lib = sym_db.get_library(address)
        obj = sym_db.get_obj(address)

        if lib and obj:
            if lib in libs:
                if not obj in lib_objs[lib]:
                    lib_objs[lib].add(obj)

                lib_func[lib] += 1
            else:
                libs.add(lib)

                lib_objs[lib] = set()
                lib_objs[lib].add(obj)

                lib_func[lib] = 1
                

    libs = sorted(list(libs), key=str.casefold)

    table = []

    for lib in libs:
        table.append((get_lib_display_name(lib), len(lib_objs[lib]), lib_func[lib]))

    util.print_table(("Library", "Obj count", "Function count"), table)

def list_objs(sym_db, args):
    if len(args) != 1:
        print_help_and_exit()

    target_lib = args[0]

    objs = set()
    obj_func = dict()

    for address in sym_db.get_all_functions():
        lib = sym_db.get_library(address)
        obj = sym_db.get_obj(address)

        if lib == target_lib and obj:
            if obj in objs:
                obj_func[obj] += 1
            else:
                objs.add(obj)
                obj_func[obj] = 1

    objs = sorted(list(objs), key=str.casefold)

    table = []

    for obj in objs:
        table.append((get_obj_display_name(obj), obj_func[obj]))

    util.print_table(("Obj", "Function count"), table)


def list_func(sym_db, args):
    if len(args) != 1:
        print_help_and_exit()

    target_obj = args[0]

    addresses = []

    for address in sym_db.get_all_functions():
        obj = sym_db.get_obj(address)

        if obj == target_obj:
            addresses.append(address)

    rows = []

    for address in addresses:
        size = sym_db.get_size(address)
        demangled = sym_db.get_demangled_symbol(address)
        decompiled = sym_db.is_marked_decompiled(address)

        rows.append((util.hex32(address), util.hex24(size), decompiled, demangled))
      
    util.print_table(("Address", "Size", "Decompiled", "Declaration"), rows)

    print()
    print(f"{len(addresses)} function(s) were found in {target_obj}.o.")

def move_func(sym_db, args):
    if len(args) != 3:
        print_help_and_exit()

    address = int(args[0], 16)
    obj = args[1]
    lib = args[2]

    if not sym_db.does_address_exist(address):
        print("Function does not exist.")
        return
        
    old_obj = sym_db.get_obj(address)
    old_lib = sym_db.get_library(address)

    if obj == old_obj and lib == old_lib:
        print("Function is already placed in the specified obj file and library.")
        return

    sym_db.set_obj(address, obj)
    sym_db.set_library(address, lib)
    
    assert sym_db.get_obj(address) == obj
    assert sym_db.get_library(address) == lib

    print(f"Function was successfully moved.")
    print(f"Function: {sym_db.get_demangled_symbol(address)}")
    print(f"Address:  {util.hex32(address)}")
    print(f"Library:  {get_lib_display_name(old_lib)} -> {get_lib_display_name(lib)}")
    print(f"Obj:      {get_obj_display_name(old_obj)} -> {get_obj_display_name(obj)}")
    
def move_multi_func(sym_db, args):
    if len(args) != 4:
        print_help_and_exit()

    first_address = int(args[0], 16)
    last_address = int(args[1], 16)
    obj = args[2]
    lib = args[3]
    
    if first_address > last_address:
        print("Invalid addresses.")
        return

    move_count = 0

    for address in sym_db.get_all_functions():
        if address < first_address or address > last_address:
            continue
                    
        print(f"Moving {sym_db.get_demangled_symbol(address)}...")

        old_obj = sym_db.get_obj(address)
        old_lib = sym_db.get_library(address)

        if obj == old_obj and lib == old_lib:
            print("Function is already placed in the specified obj file and library.")
            print()
            continue
    
        print(f"Obj:     {get_obj_display_name(old_obj)} -> {get_obj_display_name(obj)}")
        print(f"Library: {get_lib_display_name(old_lib)} -> {get_lib_display_name(lib)}")
            
        sym_db.set_obj(address, obj)
        sym_db.set_library(address, lib)

        print()

        move_count += 1

    print(f"{move_count} functions were moved.")

def random_func(sym_db, rest):
    if len(rest) > 1:
        print_help_and_exit()

    nr = int(rest[0]) if len(rest) > 0 else 10

    addresses = []

    for address in sym_db.get_all_functions():
        if not sym_db.is_marked_decompiled(address) and sym_db.get_symbol(address) and sym_db.get_obj(address) and sym_db.get_library(address):
            addresses.append(address)

    func_table = []

    for i in range(nr):
        index = random.randrange(len(addresses))
        address = addresses[index]
        del addresses[index]

        f_address = util.hex32(address)
        f_size = util.hex24(sym_db.get_size(address))
        f_symbol = sym_db.get_demangled_symbol(address)
        f_obj = get_obj_display_name(sym_db.get_obj(address))
        f_lib = get_lib_display_name(sym_db.get_library(address))

        func_table.append((f_address, f_size, f_symbol, f_obj, f_lib))

    util.print_table(("Address", "Size", "Declaration", "Obj", "Library"), func_table)
    
def random_func(sym_db, rest):
    if len(rest) > 1:
        print_help_and_exit()

    nr = int(rest[0]) if len(rest) > 0 else 10

    addresses = []

    for address in sym_db.get_all_functions():
        if not sym_db.is_marked_decompiled(address) and sym_db.get_symbol(address) and sym_db.get_obj(address) and sym_db.get_library(address):
            addresses.append(address)

    func_table = []

    for i in range(nr):
        index = random.randrange(len(addresses))
        address = addresses[index]
        del addresses[index]

        f_address = util.hex32(address)
        f_size = util.hex24(sym_db.get_size(address))
        f_symbol = sym_db.get_demangled_symbol(address)
        f_obj = get_obj_display_name(sym_db.get_obj(address))
        f_lib = get_lib_display_name(sym_db.get_library(address))

        func_table.append((f_address, f_size, f_symbol, f_obj, f_lib))

    func_table.sort(key=lambda x: x[2].lower())

    util.print_table(("Address", "Size", "Declaration", "Obj", "Library"), func_table)
    
def random_obj(sym_db, rest):
    if len(rest) > 1:
        print_help_and_exit()

    nr = int(rest[0]) if len(rest) > 0 else 10

    objs = []
    obj_set = dict()

    for address in sym_db.get_all_functions():
        if not sym_db.is_marked_decompiled(address):
            obj = sym_db.get_obj(address)
            lib = sym_db.get_library(address)

            if obj and lib:
                pair = (obj, lib)

                if pair in obj_set:
                    obj_set[pair] += 1
                else:
                    objs.append(pair)
                    obj_set[pair] = 1
        
    obj_table = []

    for i in range(nr):
        index = random.randrange(len(objs))
        obj = objs[index]
        func_count = obj_set[obj]
        del objs[index]

        obj_table.append((obj[0], obj[1], func_count))

    obj_table.sort(key=lambda x: x[0].lower())

    util.print_table(("Obj", "Library", "Function count"), obj_table)

def rename_obj(sym_db, args):
    if len(args) != 4:
        print_help_and_exit()

    old_obj = args[0]
    old_lib = args[1]
    new_obj = args[2]
    new_lib = args[3]

    if old_obj == new_obj and old_lib == new_lib:
        print("Destination name is the same as source.")
        return

    count = 0

    for address in sym_db.get_all_functions():
        obj = sym_db.get_obj(address)
        lib = sym_db.get_library(address)

        if obj == old_obj and lib == old_lib:
            sym_db.set_obj(address, new_obj)
            sym_db.set_library(address, new_lib)

            count += 1

    print(f"{count} function(s) were moved.")        

def search_func(sym_db, args):
    if len(args) != 1:
        print_help_and_exit()

    pattern = args[0]

    rows = []

    for address in sym_db.search_functions(pattern):
        size = sym_db.get_size(address)
        demangled = sym_db.get_demangled_symbol(address)
        obj = sym_db.get_obj(address)
        lib = sym_db.get_library(address)
        decompiled = sym_db.is_marked_decompiled(address)

        rows.append((util.hex32(address), util.hex24(size), decompiled, demangled, get_obj_display_name(obj), get_lib_display_name(lib)))     

    util.print_table(("Address", "Size", "Decompiled", "Declaration", "Obj", "Library"), rows)
    
def set_symbol(sym_db, args):
    if len(args) != 2:
        print_help_and_exit()
        
    address = int(args[0], 16)
    symbol = args[1]

    if not sym_db.does_address_exist(address):
        print("Function does not exist.")
        return

    if symbol != "":
        if sym_db.get_symbol(address) == symbol:
            print("Symbol is already set the given symbol.")
            return

        if sym_db.does_symbol_exist(symbol):
            print("Symbol already exists.")
            return

    old_demangled = sym_db.get_demangled_symbol(address)

    sym_db.set_symbol(address, symbol)
    
    lib = sym_db.get_library(address)
    obj = sym_db.get_obj(address)

    print("New symbol was set.")
    print(f"Function:     {sym_db.get_demangled_symbol(address)}")
    print(f"Old function: {old_demangled}")
    print(f"Library:      {get_lib_display_name(lib)}")
    print(f"Obj:          {get_obj_display_name(obj)}")

def set_size(sym_db, args):
    if len(args) != 2:
        print_help_and_exit()

    address = int(args[0], 16)
    size = int(args[1], 16)

    if size % 4 != 0:
        print("Size must be a multiple of 4.")
        return

    if not sym_db.does_address_exist(address):
        print("Function does not exist.")
        return

    old_size = sym_db.get_size(address)
    
    if size == old_size:
        print("Size is already set to the given size.")
        return

    sym_db.set_size(address, size)

    print(f"Function: {sym_db.get_demangled_symbol(address)}")
    print(f"Old size: {util.hex24(old_size)}")
    print(f"New size: {util.hex24(size)}")
    
def tree(sym_db, args):
    if len(args) != 0:
        print_help_and_exit()

    prev_lib = None
    prev_obj = None

    for address in sym_db.get_all_functions():
        lib = sym_db.get_library(address)
        obj = sym_db.get_obj(address)

        if lib != prev_lib:
            print(f"| {lib}")

        if obj != prev_obj:
            print(f"|---- {obj}")

        prev_lib = lib
        prev_obj = obj

def unmark_func(sym_db, args):
    if len(args) != 1:
        print_help_and_exit()
        
    address = int(args[0], 16)

    if not sym_db.is_marked_decompiled(address):
        print("Function is already marked as decompiled.")
        return

    sym_db.mark_function_decompiled(address, False)

    print(f"{sym_db.get_demangled_symbol(address)} was unmarked.")
    
def unset_symbol(sym_db, args):
    if len(args) != 1:
        print_help_and_exit()
        
    address = int(args[0], 16)

    if not sym_db.does_address_exist(address):
        print("Function does not exist.")
        return

    old_demangled = sym_db.get_demangled_symbol(address)

    sym_db.set_symbol(address, "")
    
    lib = sym_db.get_library(address)
    obj = sym_db.get_obj(address)

    print("Symbol was removed.")
    print(f"Old function: {old_demangled}")
    print(f"Library:      {get_lib_display_name(lib)}")
    print(f"Obj:          {get_obj_display_name(obj)}")
    
def validate(sym_db, args):
    if len(args) != 0:
        print_help_and_exit()

    for address in sym_db.get_all_functions():
        symbol = sym_db.get_symbol(address)

        if symbol:
            try:
                demangler.demangle_symbol(symbol)
            except demangler.DemanglerException:
                print(f"Failed to demangle symbol at 0x{util.hex32(address)}: {symbol}")

def main(args):
    if len(args) < 1:
        print_help_and_exit()

    sym_db = SymbolDB()
    sym_db.load()

    command = args[0]
    rest = args[1:]

    if command == "help":
        print_help_and_exit()
    elif command == "func":
        func_info(sym_db, rest)
    elif command == "gen-map":
        gen_map(sym_db, rest)
    elif command == "list-lib":
        list_libs(sym_db, rest)
    elif command == "list-obj":
        list_objs(sym_db, rest)
    elif command == "list-func":
        list_func(sym_db, rest)
    elif command == "move":
        move_func(sym_db, rest)
    elif command == "move-multi":
        move_multi_func(sym_db, rest)
    elif command == "rand-func":
        random_func(sym_db, rest)
    elif command == "rand-obj":
        random_obj(sym_db, rest)
    elif command == "rename-obj":
        rename_obj(sym_db, rest)
    elif command == "search-func":
        search_func(sym_db, rest)
    elif command == "set-symbol":
        set_symbol(sym_db, rest)
    elif command == "set-size":
        set_size(sym_db, rest)
    elif command == "tree":
        tree(sym_db, rest)
    elif command == "unmark":
        unmark_func(sym_db, rest)
    elif command == "unset-symbol":
        unset_symbol(sym_db, rest)
    elif command == "validate":
        validate(sym_db, rest)
    else:
        print(f"Invalid command: {command}")
        print()
        print_help_and_exit()

    sym_db.save()

if __name__ == "__main__":
    main(sys.argv[1:])
