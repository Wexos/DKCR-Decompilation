import struct
import util

SECTION_TO_ADDRESS = {
     1: 0x80004000, # .text0 (.init)
     2: 0x800068E0, # .text1 (.text)
     5: 0x80544580, # .data4 (.rodata)
     6: 0x805650e0, # .data5 (.data)
     7: 0x805a7f80, # .uninitialized0 (.bss)
     8: 0x805A7F80, # .uninitialized0, seems weird....
     9: 0x8061fc20, # .data7 (.sdata2)
    11: 0x8061EA80, # .uninitialized1 (.sbss)
}

SECTIONS_TO_IGNORE = {
    65521
}

def get_u32(data, offset):
    data, = struct.unpack_from(">I", data, offset)
    return data

def read_nt_string(data: bytes, offset: int):
    end = data.find(b'\x00', offset)

    if end == -1:
        raise ValueError("Null terminator not found.")

    return data[offset:end].decode('utf-8')

def main():
    RSO_PATH = "Y:\\Wii\\Donkey Kong Country Returns\\v1.1 USA\\Data\\files\\RSO\\wii_production\\selfile.sel"
    
    with open(RSO_PATH, "rb") as input:
        rso_data = input.read()

        export_sym_table_offset = get_u32(rso_data, 0x40)
        export_sym_count = get_u32(rso_data, 0x44) // 0x10
        export_sym_name_offset = get_u32(rso_data, 0x48)

        lines = []

        for i in range(export_sym_count):
            export_sym_offset = export_sym_table_offset + i * 0x10

            name_offset = get_u32(rso_data, export_sym_offset + 0)
            sym_offset = get_u32(rso_data, export_sym_offset + 4)
            section_index = get_u32(rso_data, export_sym_offset + 8)

            sym_name = read_nt_string(rso_data, export_sym_name_offset + name_offset)

            if section_index in SECTIONS_TO_IGNORE:
                continue

            if not section_index in SECTION_TO_ADDRESS:
                print(f"Invalid section index: {section_index}")
                return

            section_address = SECTION_TO_ADDRESS[section_index]
            address = section_address + sym_offset

            lines.append(f"{util.hex32(address)} {util.hex32(section_index)} {sym_name}")

        for line in sorted(lines):
            print(line)

if __name__ == "__main__":
    main()
