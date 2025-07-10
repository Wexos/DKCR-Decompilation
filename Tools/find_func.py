import asm
import db
import struct
import pathlib
from capstone import *
from capstone.ppc import *

def get_u32(data, offset):
    data, = struct.unpack_from(">I", data, offset)

    return data

func_db = db.SymbolDB()
func_db.load()

invalid_functions = {
    0x805b3f20
}

with open(pathlib.Path("../main.dol"), "rb") as input:
    data = input.read()

    txt1_offset = get_u32(data, 0x04)
    txt1_size = get_u32(data, 0x94)
    txt1_address = get_u32(data, 0x4C)
    
    txt1_address_end = txt1_address + txt1_size
        
    cs = asm.create_cs_obj()
        
    print("Doing functions...")

    func_addresses = []

    for address in func_db.get_all_functions():
        func_addresses.append(address)

        
    for i in range(len(func_addresses)):
        func_address = func_addresses[i]

        if func_address < txt1_address or func_address >= txt1_address_end:
            continue

        if func_db.is_marked_decompiled(func_address):
            continue

        func_offset = func_address - txt1_address + txt1_offset
        #func_size = func_db.get_size(func_address)
        
        if i == len(func_addresses) - 1:
            next_func_address = txt1_address_end
        else:
            next_func_address = func_addresses[i + 1]

        # Stored function size may be too small
        func_size = next_func_address - func_address

        assert func_size % 4 == 0 and func_size != 0

        instr_data = data[func_offset:func_offset + func_size]
        instructions = []

        assert len(instr_data) == func_size
        min_size = 0
        max_size = 0

        for j in range(0, len(instr_data), 4):
            raw = (instr_data[j] << 24) | (instr_data[j + 1] << 16) | (instr_data[j + 2] << 8) | instr_data[j + 3]

            if raw == 0:
                break

            max_size += 4

        assert max_size >= 4

        max_size = min(max_size, func_size)

        for j in range(0, len(instr_data), 4):
            i_data = instr_data[j:j + 4]
            instruction = list(cs.disasm(i_data, 0))

            raw = (i_data[0] << 24) | (i_data[1] << 16) | (i_data[2] << 8) | i_data[3]

            if raw == 0:
                break

            if len(instruction) != 1:
                continue

            instr = instruction[0]

            if asm.is_branch_instruction(instr):
                if instr.id == PPC_INS_BLR:
                    temp_size = 4 + j

                    if temp_size >= min_size and temp_size < max_size:
                        next_address = func_address + temp_size
                        
                        if next_address % 0x10 == 0 and not func_db.does_address_exist(next_address):
                            func_db.add_function(next_address, 0)

                        break                        
                    continue

                abs_address = asm.get_branch_address(instr, func_address + j)

                if abs_address == None:
                    continue

                assert abs_address >= 0x80000000

                if instr.id == PPC_INS_BL:
                    if not func_db.does_address_exist(abs_address):
                        assert abs_address % 0x10 == 0
                        func_db.add_function(abs_address, 0)
                elif abs_address >= next_func_address or abs_address < func_address:
                    assert instr.id == PPC_INS_B

                    # Here we should add the function to the db, but some functions are incorrect
                    # so we ignore this
                    #assert func_db.does_address_exist(abs_address)
                else:
                    min_size = max(min_size, abs_address - func_address + 4)

    print("Doing sizes...")
    
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

        func_db.set_size(func_address, min(max_size, test_size))

func_db.save()
