import os
import pathlib

ROOT_PATH = pathlib.Path(__file__).parent.parent

def hex8(number):
    return "{:02X}".format(number)

def hex24(number):
    return "{:06X}".format(number)

def hex32(number):
    return "{:08X}".format(number)

def is_hex_string(string):
    for c in string.upper():
        if (c < '0' or c > '9') and (c < 'A' or c > 'F'):
            return False

    return True

def is_windows():
    return os.name == "nt"

def is_right_align_cell(value):
    if not isinstance(value, bool):
        try:
            int(str(value))
            return True
        except:
            pass
    
        try:
            float(str(value))
            return True
        except:
            pass
    
    if isinstance(value, str) and is_hex_string(value):
        return True
    
    return False

def print_table(column_names, rows):
    PAD_SIZE = 2
    nr_columns = len(column_names)
    nr_rows = len(rows)

    column_sizes = []
    column_align_left = []

    for column in range(nr_columns):
        column_sizes.append(len(column_names[column]))

        is_left = False

        for row in range(nr_rows):
            value = rows[row][column]
            
            if not is_right_align_cell(value):
                is_left = True
                break
        
        column_align_left.append(is_left)
        
    for column in range(nr_columns):
        for row in range(nr_rows):
            element = str(rows[row][column])
            if len(element) > column_sizes[column]:
                column_sizes[column] = len(element)
            
    line_size = 0

    for column in range(nr_columns):
        line_size += column_sizes[column]

        if column < nr_columns - 1:
            line_size += PAD_SIZE
    
    for column in range(nr_columns):
        pad_size = PAD_SIZE if column < nr_columns - 1 else 0
        print_element(column_names[column], column_sizes[column], pad_size, True)

    print()

    for i in range(line_size):
        print("-", end="")

    print()
    
    for row in range(nr_rows):
        for column in range(nr_columns):
            pad_size = PAD_SIZE if column < nr_columns - 1 else 0
            print_element(rows[row][column], column_sizes[column], pad_size, column_align_left[column])

        print()

def print_element(element, size, pad_size, is_left):
    element = str(element)
    value_pad_size = (size - len(element))

    if not is_left:
        for i in range(value_pad_size):
            print(" ", end="")

    print(element, end="")

    if is_left:
        for i in range(value_pad_size):
            print(" ", end="")

    for i in range(pad_size):
        print(" ", end="")
    