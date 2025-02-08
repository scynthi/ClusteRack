import os
import time
import random
import string
from datetime import datetime
from os import path as Path
from modules.computer import Computer
from colorama import Fore, Style

class SmartRebalancer:
    def __init__(self, path: str, parent):
        self.parent = parent
        self.sorted_computer_list = []
        self.sorted_process_list = []

        self.distribute_processes_balanced()


    def sort_computers(self) -> None:
        self.sorted_computer_list = sorted(
            self.parent.computers.items(),
            key=lambda x: (-x[1].cores, x[1].memory)
        )


    def sort_programs(self) -> None:
        expanded_processes = []
        for name, details in self.parent.processes.items():
            instance_count = int(details["instance_count"])
            for _ in range(instance_count):
                expanded_processes.append((name, details.copy()))

        self.sorted_process_list = sorted(
            expanded_processes,
            key=lambda x: (-int(x[1]['cores']), -int(x[1]['memory']))
        )

        self.assign_process_id()


    def assign_process_id(self) -> None:
        used_ids = set()

        for process in self.sorted_process_list:
            if 'instance_count' in process[1]:
                del process[1]['instance_count']

            while True:
                new_id = ''.join(random.choices(string.ascii_lowercase, k=6))
                if new_id not in used_ids:
                    used_ids.add(new_id)
                    break
            process[1]['id'] = new_id


    def clear_computer_processes(self, computer: Computer) -> None:     #This ensures that every rerun is the same nomatter the starting conditions.
        for file in os.listdir(computer.path):
            file_path = Path.join(computer.path, file)
            if file != ".szamitogep_config" and Path.isfile(file_path):
                os.remove(file_path)


    def write_process_file(self, computer: Computer, process_name: str, process: dict) -> None:
        process_id = process["id"]

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        process_filename = f"{process_name}-{process_id}"

        file_path = Path.join(computer.path, process_filename)
        with open(file_path, "w", encoding="utf8") as file:
            file.write(f"{timestamp}\n")
            file.write(f"AKTÍV\n")                      #Activity system still to be implamented
            file.write(f"{process['cores']}\n")
            file.write(f"{process['memory']}\n")
        file.close()


    def calculate_computer_score(self, computer: Computer) -> float:
        core_utilization = (computer.cores - computer.free_cores) / computer.cores
        memory_utilization = (computer.memory - computer.free_memory) / computer.memory
        return core_utilization + memory_utilization  # Simple heuristic score


    def process_fits(computer: Computer, process: dict) -> bool:
        return (
            computer.free_cores >= int(process["cores"])
            and computer.free_memory >= int(process["memory"])
        )


    # Only for debugging purposes
    def print_computer_scores(self):
        print(Fore.CYAN + "\nCurrent Computer Scores:" + Style.RESET_ALL)
        for name, computer in self.sorted_computer_list:
            score = self.calculate_computer_score(computer)
            print(f"{name} -> Score: {score:.2f} (Cores: {computer.free_cores}/{computer.cores}, Memory: {computer.free_memory}/{computer.memory})")

    # Only for debugging purposes
    def print_assignments(self, assignments):
        print(Fore.GREEN + "\nProcess Assignments:" + Style.RESET_ALL)
        for process_name, computers in assignments.items():
            assigned_to = [comp.name for comp in computers]
            print(f"{process_name} -> {', '.join(assigned_to)}")



    def distribute_processes_balanced(self) -> None:
        #Step 1
        self.sort_computers()
        self.sort_programs()

        assignments = {}

        print(Fore.YELLOW + "\nBefore Distribution:" + Style.RESET_ALL)
        self.print_computer_scores()

        # Step 2: Clear current processes from all computers before checking availability
        for name, computer in self.sorted_computer_list:
            self.clear_computer_processes(computer)  # Always clears processes

        # Step 3: Recalculate free resources for each computer after clearing old processes
        for name, computer in self.sorted_computer_list:
            computer.calculate_resource_usage()  

        # Step 4: Assign processes
        for process_name, process in self.sorted_process_list:
            best_computer = None
            best_score = float("inf")
            required_cores = int(process["cores"])
            required_memory = int(process["memory"])

            # Find the least loaded computer that can handle the process
            for name, computer in self.sorted_computer_list:
                if computer.free_cores >= required_cores and computer.free_memory >= required_memory:
                    score = self.calculate_computer_score(computer)

                    if score < best_score:
                        best_computer = computer
                        best_score = score

            if best_computer:
                # Assign process
                if process_name not in assignments:
                    assignments[process_name] = []
                assignments[process_name].append(best_computer)

                # Reduce available resources
                best_computer.free_cores -= required_cores
                best_computer.free_memory -= required_memory

                # Write the process to the computer's directory
                self.write_process_file(best_computer, process_name, process)

            else:
                print(Fore.RED + f"Skipping {process_name}: Not enough resources on any computer!" + Style.RESET_ALL)

        print(Fore.GREEN + "\nAfter Distribution:" + Style.RESET_ALL)
        self.print_computer_scores()

        self.print_assignments(assignments)






"""
Inside The Rebalancing algorithm:
1. Sort the computerlist and save a copy of it based on the resources TOTAL cores.               DONE
    if there are computers with the same amount cores we sort by memory.

2. Sort the programlist and save a copy of it based on their cores taken for them to run.
    if there are programs with the same amount of cores taken to run them we sort by the memory taken to run them.               DONE

a)-----------------------------------A Last Resort----------------------------------------- Load Balancing Algo.               DONE

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