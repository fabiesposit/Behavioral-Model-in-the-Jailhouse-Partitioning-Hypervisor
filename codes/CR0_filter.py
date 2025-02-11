map_dict = {
    "0x80050033": "A",
    "0x30": "B",
    "0x31": "C",
    "0x80010031": "D",
    "0x10031": "E",
    "0x80000031": "F"
}


file_path_input = "vmcs_dump.txt"  


cr0_last_val = "0x80050033"


mapped_chars = []


with open(file_path_input, 'r') as file_input:
    for line in file_input:
        if "guest_cr0:" in line:
            cr0_last_val = line.split(" ")[1].strip()
        elif "EXIT NUM" in line:
            char = map_dict.get(cr0_last_val)
            mapped_chars.append(char)


trans_dict = {}


for i in range(len(mapped_chars) - 1):
    pair_transition = mapped_chars[i] + " -> " + mapped_chars[i + 1]
    trans_dict[pair_transition] = trans_dict.get(pair_transition, 0) + 1


file_path_output = "fsm1.txt"


with open(file_path_output, 'w') as file_output:
    for transition, count in trans_dict.items():
        file_output.write(f"{transition}: {count}\n")

print(f"Results saved in {file_path_output}")