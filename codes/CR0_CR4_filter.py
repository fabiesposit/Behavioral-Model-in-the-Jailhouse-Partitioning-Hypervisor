# Mapping dictionary
map_dict = {
    "0x80050033 0x172ea0": "A1",
    "0x30 0x2000": "B",
    "0x31 0x2020": "C",
    "0x80010031 0x2020": "D1",
    "0x80010031 0x2220": "D2",
    "0x80010031 0x42220": "D3",
    "0x10031 0x42220": "E",
    "0x80000031 0x2020": "F1",
    "0x80000031 0x20a0": "F2",
    "0x80050033 0x20a0": "A2",
    "0x80050033 0x26a0": "A3",
    "0x80050033 0x426a0": "A4",
    "0x80050033 0x42620": "A5",
    "0x80050033 0x626b0": "A6",
    "0x80050033 0x162e30": "A7",
    "0x80050033 0x162eb0": "A8"
}

# Input file
input_file_path = "vmcs_dump.txt"

# Variable for last CR0 value
last_cr0_value = "0x80050033"

# List for mapping results
mapped_results = []

# File opening
with open(input_file_path, 'r') as input_file:
    for line in input_file:
        if "guest_cr4:" in line:
            cr4_value = line.split(" ")[1].strip()
        elif "guest_cr0:" in line:
            last_cr0_value = line.split(" ")[1].strip()
        elif "EXIT NUM" in line and 'cr4_value' in locals():
            mapping_key = f"{last_cr0_value} {cr4_value}"
            mapped_char = map_dict.get(mapping_key, "?")
            mapped_results.append(mapped_char)
            # Variable reset for next iteration
            if 'cr4_value' in locals():
                del cr4_value

# Transitions dictionary
transitions_dict = {}

# Transitions counter
for i in range(len(mapped_results) - 1):
    transition_pair = mapped_results[i] + " -> " + mapped_results[i + 1]
    transitions_dict[transition_pair] = transitions_dict.get(transition_pair, 0) + 1

# Output file
output_file_path = "fsm2.txt"

# Writing results
with open(output_file_path, 'w') as output_file:
    for transition, count in transitions_dict.items():
        output_file.write(f"{transition}: {count}\n")

print(f"Results saved in {output_file_path}")