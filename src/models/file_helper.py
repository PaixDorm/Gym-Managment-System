import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

def full_path(filename):
    return os.path.join(DATA_DIR, filename)

def read_lines(filename):
    path = full_path(filename)

    if not os.path.exists(path):
        return []
    
    with open(path, "r", encoding = "UTF-8") as file:
        lines = []

        for line in file:
            line = line.strip()
            if line != "":
                lines.append(line)

        return lines

def write_lines(filename, lines):
    os.makedirs(DATA_DIR, exist_ok = True)
    path = full_path(filename)

    with open(path, "w", encoding = "UTF-8") as file:
        for line in lines:
            file.write(f"{line}\n")

def append_line(filename, line):
    os.makedirs(DATA_DIR, exist_ok = True)
    path = full_path(filename)

    with open(path, "a", encoding = "UTF-8") as file:
        file.write(f"{line}\n")