import os
from os import path as Path
from cluster import Cluster
from modules.computer import Computer
from colorama import Fore, Style, Back

class SmartRebalancer:
    def __init__(self, path : str, parent : Cluster):
        self.parent = parent

        self.sorted_computer_list = []
        self.sorted_program_list = []

        self.sort_computers()
        self.sort_programs()

    def sort_computers(self) -> None:
        sorted_computers = sorted(self.parent.computers.items(), key=lambda x: (-x[1].cores, x[1].memory))
        self.sorted_computer_list = sorted_computers

    def sort_programs(self) -> None:
        sorted_processes = sorted(self.parent.processes.items(), key=lambda x: (-int(x[1]['cores']), -int(x[1]['memory'])))
        
        self.sorted_processes_list = sorted_processes

        
"""
(rb = rebalancer)

FEATURES WE NEED:
- every cluster should store a reference to their own rebalancer module ------------------------------ DONE
- the rb should be able to reference its own cluster to use its resources such as the computer_list and create delete functions
- the rabalancing program should be rerun every time the clusters file structure updates. 
- the rb should be able to be called from the cluster that owns it.
- the list of programs and their specs should be stored on the cluster instead of the rb for ease of understanding. (FOR NOW) the pc shouldnt store a list of their own programs


Inside The Rebalancing algorithm:
1. Sort the computerlist and save a copy of it based on the resources TOTAL cores.
    if there are computers with the same amount cores we sort by memory.

2. Sort the programlist and save a copy of it based on their cores taken for them to run.
    if there are programs with the same amount of cores taken to run them we sort by the memory taken to run them.

a)-----------------------------------A Last Resort----------------------------------------- Load Balancing Algo.

Heuristic Load Balancing
3. Assign a score to all computers based that shows us how well they utalize their resources. (A higher score means the computer is heavily loaded)
4. Assign programs to the lowest scoring computer that can still fit the program. (lowest scoring) (has enough core and memory)
    if no computer can fit the program, move to the next program.
5. Reduce the available resources of the computer accordingly.
6. Update the scores to reflect the changes.
7. Repeat steps 3-7 until all programs are sorted

--- Slowest, Evenly distributes the load leaving no computer overloaded.

b)-----------------------------------No Space Left Behind----------------------------------------- Efficient Packing Algo.

Greedy Best Fit Decreasing
3. Find the best-fitting computer, which is the one with the least remaining resources after placing the program (but still enough to fit the program).
    if no computer can fit it, move to the next program.
4. Assign the program to the computer.
5. Reduce the available resources of the computer accordingly.
6. Repeat steps 3-6 until all programs are sorted.

--- Balanced speed, Doesn`t leave gaps on the computer in resources 

c)-----------------------------------The Fast Lane----------------------------------------- Speed Prioritizing Algo.

First Fit 
3. Iterate through the programs and put the on the first computer they fit on
    if no computer can fit it, move to the next program.
4. Repeat steps 3-4 until all programs are sorted.

--- Fastest, Leads to inefficient packing (best used if the computers are similar in resources)

"""