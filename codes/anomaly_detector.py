# SECTION 1

# mapping dictionary
mapping = {
"80050033 172ea0": "A1",
"30 2000": "B",
"31 2020": "C",
"80010031 2020": "D1",
"80010031 2220": "D2",
"80010031 42220": "D3",
"10031 42220": "E",
"80000031 2020": "F1",
"80000031 20a0": "F2",
"80050033 20a0": "A2",
"80050033 26a0": "A3",
"80050033 426a0": "A4",
"80050033 42620": "A5",
"80050033 626b0": "A6",
"80050033 162e30": "A7",
"80050033 162eb0": "A8"
}

# expected transitions between exit-states, within the same state or substate
internal_transitions = {
    'A1': {'CPUID': ['CPUID', 'MSR_WRITE'], 'MSR_WRITE': ['CPUID', 'MSR_WRITE', 'IO_INSTRUCTION', 'EPT_VIOLATION', 'VMCALL', 'EXCEPTION_NMI'], 
           'IO_INSTRUCTION': ['IO_INSTRUCTION','MSR_WRITE'], 'EPT_VIOLATION': ['MSR_WRITE', 'EPT_VIOLATION'], 'VMCALL': ['MSR_WRITE', 'VMCALL'],'EXCEPTION_NMI':[]},
    'A2': {'CPUID': ['CPUID']},
    'A3': {'CPUID': []},
    'A4': {'CPUID': ['CPUID', 'MSR_READ'], 'XSETBV': ['CPUID'], 'MSR_READ': ['CR_ACCESS'],'CR_ACCESS':[]},
    'A5': {'MSR_READ': ['MSR_WRITE'], 'MSR_WRITE': ['MSR_READ', 'MSR_WRITE', 'CR_ACCESS'],'CR_ACCESS':[]},
    'A6': {'EPT_VIOLATION': ['EPT_VIOLATION', 'XSETBV', 'CPUID'], 'CPUID': ['CPUID'], 'XSETBV': ['EPT_VIOLATION']},
    'A7': {'MSR_WRITE': ['MSR_WRITE', 'CR_ACCESS'], 'MSR_READ': ['MSR_WRITE'],'CR_ACCESS':[]},
    'A8': {'IO_INSTRUCTION': ['IO_INSTRUCTION', 'CPUID'], 'CPUID': ['IO_INSTRUCTION', 'CPUID', 'CR_ACCESS'],'CR_ACCESS':[]},
    'B': {'EXCEPTION_NMI': ['EXCEPTION_NMI', 'PREEMPTION_TIMER'],'PREEMPTION_TIMER':[]},
    'C': {'MSR_READ': ['MSR_WRITE'], 'MSR_WRITE': ['CR_ACCESS'], 'CR_ACCESS':[]},
    'D1': {'CPUID': ['CPUID']},
    'D2': {'CPUID': []},
    'D3': {'CPUID': ['CPUID', 'XSETBV'], 'XSETBV': ['CPUID']},
    'E': {'CR_ACCESS': []},
    'F1': {'CPUID': ['CR_ACCESS','CPUID'],'CR_ACCESS':[]},
    'F2': {'CPUID': ['CR_ACCESS'],'CR_ACCESS':[]}
}

# expected transitions among states/substates
external_transitions = {
    'A1': {'EXCEPTION_NMI': [('B', 'EXCEPTION_NMI')]},
    'A2': {'CPUID': [('A3', 'CPUID')]},
    'A3': {'CPUID': [('A4', 'XSETBV')]},
    'A4': {'CR_ACCESS': [('A5', 'MSR_READ')],
           'MSR_READ': [('A6', 'EPT_VIOLATION')]},
    'A5': {'CR_ACCESS': [('A4', 'MSR_READ')]},
    'A6': {'CPUID': [('A8', 'CPUID')]},
    'A7': {'CR_ACCESS': [('A8', 'CPUID')]},
    'A8': {'CR_ACCESS': [('A7', 'MSR_READ')]},
    'B': {'PREEMPTION_TIMER': [('C', 'MSR_READ')]},
    'C': {'CR_ACCESS': [('D1', 'CPUID')]},
    'D1': {'CPUID': [('D2', 'CPUID')]},
    'D2': {'CPUID': [('D3', 'CPUID')]},
    'D3': {'CPUID': [('E', 'CR_ACCESS')]},
    'E': {'CR_ACCESS': [('F1', 'CPUID')]},
    'F1': {'CR_ACCESS': [('F2', 'CPUID')]},
    'F2': {'CR_ACCESS': [('A2', 'CPUID')]}
}

# SECTION 2

# information extracting from a single SEED block
def extract_info(seed_lines, last_field_6800, last_field_6804):
    field_6800, field_6804, exit_reason = last_field_6800, last_field_6804, None
    for line in seed_lines:
        if "FIELD(6804)," in line:
            field_6804 = line.split("VALUE(")[1].split(")")[0].strip()
        elif "EXIT REASON" in line:
            exit_reason = line.split(":")[1].strip().split(".")[0]
        elif "FIELD(6800)," in line:
            field_6800 = line.split("VALUE(")[1].split(")")[0].strip()
    return field_6800, field_6804, exit_reason

# state identification based on CR0, CR4
def identify_state(cr0, cr4):
    key = f"{cr0} {cr4}"
    return mapping.get(key, None)

def is_valid_internal_transition(prev_state, next_state, prev_reason, next_reason):
    # internal transition verify
    if prev_state == next_state:
        return next_reason in internal_transitions.get(prev_state, {}).get(prev_reason, [])
    return False

def is_valid_external_transition(prev_state, next_state, prev_reason, next_reason):
    valid_transitions = external_transitions.get(prev_state, {}).get(prev_reason, [])
    # check if new transition is included
    return any(transition == (next_state, next_reason) for transition in valid_transitions)

def is_valid_state_exit_reason(state, exit_reason):
    # check if state is valid
    return exit_reason in internal_transitions.get(state, {})

# SECTION 3

# file analysis function
def analyze_seeds(file_path, output_file_path):

    with open(file_path, 'r') as file:
        # every block is delimited by "SEED #xxxx."
        seeds_list = file.read().strip().split("SEED #")[1:]

    # anomalies list
    anomalies = []
    # default value for CR0 is 80050033 (i.e., Protected Mode) and for CR4 is 172ea0 -> state A1 
    prev_vm_exit, prev_state, prev_reason, last_field_6800, last_field_6804 = None, None, None, "80050033", "172ea0"

    for seed_block in seeds_list:
        # every block’s first line is seed number
        lines = seed_block.split("\n")
        vm_exit = lines[0].split(" ")[0]
        # extract info to identify current state (CR0, CR4, exit reason)
        cr0, cr4, exit_reason = extract_info(lines, last_field_6800, last_field_6804)
        current_state = identify_state(cr0, cr4)
        print(f"SEED #{vm_exit}     cr0:{cr0}     cr4:{cr4}     exit_reason:{exit_reason}   current state:{current_state}")
        current_reason = exit_reason

        # check if state is valid
        if current_reason is not None and not is_valid_state_exit_reason(current_state, current_reason):
            anomalies.append(f"Detected unknown state at exit #{vm_exit} (state: {current_state}, exit reason: {current_reason})")

        # if prev state is none, there is no transition (starting seed of file)
        if prev_state is not None:
            # check internal transition (prev state is equal to current state, only exit reason differs)
            if prev_state == current_state:
                if not is_valid_internal_transition(prev_state, current_state, prev_reason, current_reason):
                        anomalies.append(f"Detected unknown internal transition from exit #{prev_vm_exit} (state: {prev_state}, exit reason: {prev_reason}) to exit #{vm_exit} (state: {current_state}, exit reason: {current_reason})")
            else:
                # check external transition
                if not is_valid_external_transition(prev_state, current_state, prev_reason, current_reason):
                    anomalies.append(f"Detected unknown external transition from exit #{prev_vm_exit} (state: {prev_state}, exit reason: {prev_reason}) to exit #{vm_exit} (state: {current_state}, exit reason: {current_reason})")

            last_field_6800 = cr0  # CR0 value must be updated with current seed CR0 value since not all seeds present field 6800 content 
            last_field_6804 = cr4  # CR4 value must be updated with current seed CR4 value since not all seeds present field 6804 content 
            prev_vm_exit, prev_state, prev_reason = vm_exit, current_state, current_reason  # current state becomes prev state for next cycle

    # anomalies writing for output file
    with open(output_file_path, 'w') as output_file:
        for anomaly in anomalies:
            output_file.write(anomaly + "\n")

file_path1 = 'meta_boot_31_boot_CR_ACCESS_boot_4012_bit_0.txt'
file_path2 = 'meta_boot_31_boot_MSR_WRITE_boot_681e_bit_0.txt'
file_path3 = 'meta_boot_80010031_boot_CPUID_boot_6006_bit_0.txt'
file_path4 = 'meta_boot_80010031_boot_XSETBV_boot_6804_bit_0.txt'
file_path5 = 'meta_boot_80050033_boot_CR_ACCESS_boot_2806_bit_0.txt'

output_file_path = 'anomalies_report.txt'
analyze_seeds(file_path2, output_file_path)