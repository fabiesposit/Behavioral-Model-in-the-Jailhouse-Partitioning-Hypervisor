This work is part of the development of my bachelor’s thesis. The objective of this project is to develop a behavioral model of the Jailhouse static partitioning hypervisor, which is highly relevant in the industrial domain. This model allows us to address various challenges, such as spatial and temporal isolation, resource allocation and utilization, and the security guarantees that hypervisors must provide when executing multiple software systems with different levels of criticality.

To achieve this, I leveraged several cutting-edge technologies, including nested virtualization, which allows to treat the target hypervisor as a virtual machine within KVM (Kernel Virtual Machine), and Intel’s virtualization technologies (Intel VT-x), which provide hardware support for processor virtualization.

Additionally, the framework COSMOS, developed by the DESSERT LAB at Federico II University, played a crucial role in this study. In particular, I utilized two key features:
	•	Recording, which enables the logging of reads and writes performed during a VM Exit, storing them in a VM Exit trace—i.e., the sequence of VM exits occurring during the execution of a workload.
	•	Injection, which allows bit-flipping on any field of the VMCS during a tagged VM Exit, thereby enabling fault injection via software.

This approach allowed us to analyze both the nominal behavior of Jailhouse and its behavior under fault conditions. Specifically, the submitted workload was the Linux OS bootstrap.

Starting from a VMCS dump (located in the input_files folder), I extracted relevant information from each VM Exit to characterize the CPU’s operating modes, such as the values of the CR0 and CR4 control registers and the exit reason.

From this analysis, I inferred a nominal (fault-free) finite state machine (FSM) describing the evolution of the target hypervisor. Each state is identified by a combination of these three values, and I defined a state transition as the moment when at least one of these values changes during execution.

To accomplish this, I developed Python scripts (available in the codes folder), including three different filters that describe the FSM states at varying levels of granularity:
	1.	The first filter considers only the CR0 values.
	2.	The second filter takes into account both CR0 and CR4 values.
	3.	The third filter further includes the exit reason in the state representation.

At this point, I developed a Python-based anomaly detector (codes folder) capable of identifying behavioral anomalies in faulty traces. Using COSMOS, several faulty traces were generated and provided for testing. These can be found in the input_files folder.

Each faulty trace filename encodes the following information:
	1.	The vCPU operating mode (e.g., 31, 80010031…)
	2.	The workload type (e.g., boot in our case)
	3.	The target VM Exit (e.g., CR_ACCESS, MSR_WRITE…)
	4.	The VMCS field modified by the COSMOS injection component (e.g., 4012, 681e…)
	5.	The bit position modified within the field (e.g., bit_0 means that bit 0 was flipped)

I classified anomalies into two categories:
	•	Unknown states, i.e., state triples that were not observed in the nominal execution.
	•	Unknown state transitions, i.e., transitions between states that were never encountered during fault-free execution.

An example anomaly report can be found in the output_files folder.

