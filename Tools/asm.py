from capstone import *
from capstone.ppc import *
import struct
import util

def create_cs_obj():
    cs = Cs(CS_ARCH_PPC, CS_MODE_32 | CS_MODE_BIG_ENDIAN)
    cs.detail = True
    cs.imm_unsigned = False

    return cs

def disassemble_code(cs, data):
    # Capstone doesn't support some instructions such as psq_l and fcmpo
    # Therefore we disassemle one instruction at a time, and use the raw
    # instruction value if it's not supported
    instructions = []

    for i in range(0, len(data), 4):
        instr_data = data[i:i + 4]
        instruction = list(cs.disasm(instr_data, 0))

        raw = (instr_data[0] << 24) | (instr_data[1] << 16) | (instr_data[2] << 8) | instr_data[3]

        if len(instruction) == 0:
            instr = None
        elif len(instruction) == 1:
            instr = instruction[0]
        else:
            assert False

        instructions.append((instr, raw))

    return instructions

def is_branch_instruction(instr):
    return instr.id >= PPC_INS_B and instr.id <= PPC_INS_BLRL;

def get_branch_address(instr, rel_address):
    # This whole function might not be correct,
    # it is based on instructions found in SMG2.
    type1 = {
        PPC_INS_BCLR, PPC_INS_BCTR, PPC_INS_BCTRL,
        PPC_INS_BLR, PPC_INS_BLRL
    }

    type2 = {
        PPC_INS_B, PPC_INS_BA, PPC_INS_BCCTR, PPC_INS_BCL,
        PPC_INS_BCLRL,
        PPC_INS_BDNZ, PPC_INS_BDNZA, PPC_INS_BDNZL, PPC_INS_BDNZLA, PPC_INS_BDNZLR, PPC_INS_BDNZLRL,
        PPC_INS_BDZ, PPC_INS_BDZA, PPC_INS_BDZL, PPC_INS_BDZLA, PPC_INS_BDZLR, PPC_INS_BDZLRL,
        PPC_INS_BL, PPC_INS_BLA
    }

    type3 = {
        PPC_INS_BC
    }

    def get(index):
        disp, = struct.unpack('>i', bytes.fromhex(util.hex32(instr.operands[index].mem.base)))

        return disp

    disp_address = None

    if instr.id in type1:
        assert len(instr.operands) in { 0, 1 }

        return None

    if instr.id in type2:
        assert len(instr.operands) == 1
        
        disp_address = get(0)

    if instr.id in type3:
        assert len(instr.operands) in { 1, 2 }
        
        disp_address = get(-1)

    if disp_address == None:
        return None
        
    return rel_address + disp_address
