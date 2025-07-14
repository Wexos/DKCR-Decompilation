import asm
import db
import struct
import pathlib
import util
from capstone import *
from capstone.ppc import *

def get_u32(data, offset):
    data, = struct.unpack_from(">I", data, offset)
    return data

func_db = db.SymbolDB()
func_db.load()

invalid_functions = { }

with open(pathlib.Path(util.ROOT_PATH / "main.dol"), "rb") as input:
    data = input.read()

    txt1_offset = get_u32(data, 0x04)
    txt1_size = get_u32(data, 0x94)
    txt1_address = get_u32(data, 0x4C)
    
    txt1_address_end = txt1_address + txt1_size
        
    cs = asm.create_cs_obj()
        
    print("Doing functions...")
    
    current_address = 0x80006F40 # txt1_address

    while current_address < txt1_address_end:
        func_address = current_address
        func_offset = txt1_offset + current_address - txt1_address

        if func_db.does_address_exist(func_address):
            # Function already exists
            current_address += max(func_db.get_size(func_address), 4)
            continue

        first_instr = get_u32(data, func_offset)

        if first_instr == 0:
            # Not a function
            current_address += 4
            continue

        # Get the upper limit of the function size, which is when we hit a padding (0)
        max_func_size = 4

        while True:
            raw = get_u32(data, func_offset + max_func_size)

            if raw == 0:
                break

            max_func_size += 4

        # The function may be multiple functions (alignment by 4 instead of 0x10, function size multiple of 0x10, etc)
        func_data = data[func_offset:func_offset + max_func_size]
        max_branch_address = 0
        func_size = max_func_size

        for j in range(0, len(func_data), 4):
            i_data = func_data[j:j + 4]
            instruction = list(cs.disasm(i_data, 0))

            raw = (i_data[0] << 24) | (i_data[1] << 16) | (i_data[2] << 8) | i_data[3]

            assert raw != 0            
            assert len(instruction) <= 1

            if len(instruction) != 1:
                continue

            instr = instruction[0]

            if not asm.is_branch_instruction(instr):
                continue

            if instr.id == PPC_INS_BLR:
                if max_branch_address <= func_address + j:
                    func_size = j + 4
                    break

            abs_address = asm.get_branch_address(instr, func_address + j)

            if abs_address == None:
                continue            

            assert abs_address >= 0x80000000

            if abs_address < func_address or abs_address > func_address + max_func_size:
                if not func_db.does_address_exist(abs_address):
                    func_db.add_function(abs_address, 0)

            max_branch_address = max(max_branch_address, abs_address)

        assert func_size > 0

        if func_db.does_address_exist(func_address):
            func_db.set_size(func_address, func_size)
        else:
            func_db.add_function(func_address, func_size)

        current_address += func_size

    """print("Doing sizes...")
    
    func_addresses = []

    for address in func_db.get_all_functions():
        func_addresses.append(address)

    # Sizes
    for i in range(len(func_addresses)):
        func_address = func_addresses[i]

        if func_address < txt1_address or func_address >= txt1_address_end:
            continue

        if func_db.is_marked_decompiled(func_address):
            continue

        func_offset = func_address - txt1_address + txt1_offset

        if i == len(func_addresses) - 1:
            next_func_address = txt1_address_end
        else:
            next_func_address = func_addresses[i + 1]

        max_size = next_func_address - func_address
        test_size = 4
        
        if next_func_address != txt1_address_end:
            while True:
                if get_u32(data, func_offset + test_size) == 0:
                    break

                test_size += 4
        else:
            test_size = max_size

        func_db.set_size(func_address, min(max_size, test_size))"""

func_db.save()
