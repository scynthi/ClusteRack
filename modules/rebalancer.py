import os
import time
import random
import string
from datetime import datetime
from os import path as Path
from modules.computer import Computer
from colorama import Fore, Style, Back

class Rebalancer:
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
        for name, details in self.parent.active_processes.items():
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

        process_filename = f"{process_name}-{process_id}"

        file_path = Path.join(computer.path, process_filename)
        with open(file_path, "w", encoding="utf8") as file:
            file.write(f"{process["date_started"]}\n")
            file.write(f"AKTÍV\n")
            file.write(f"{process['cores']}\n")
            file.write(f"{process['memory']}\n")
        file.close()


    def calculate_computer_score(self, computer: Computer) -> float:
        core_utilization = (computer.cores - computer.free_cores) / computer.cores
        memory_utilization = (computer.memory - computer.free_memory) / computer.memory
        return core_utilization + memory_utilization  # Simple heuristic score


    # def process_fits(computer: Computer, process: dict) -> bool:
    #     return (
    #         computer.free_cores >= int(process["cores"])
    #         and computer.free_memory >= int(process["memory"])
    #     )


    # Only for debugging purposes
    def print_computer_scores(self):
        print(Fore.CYAN + "Current Computer Scores:" + Style.RESET_ALL)
        for name, computer in self.sorted_computer_list:
            score = self.calculate_computer_score(computer)
            print(f"{Style.BRIGHT + Fore.CYAN}[{Fore.WHITE}{name}{Fore.CYAN}] -> {Fore.WHITE}Score: {Style.BRIGHT+Fore.GREEN}{score:.2f} {Style.NORMAL+Fore.WHITE}(Cores: {computer.free_cores}/{computer.cores}, Memory: {computer.free_memory}/{computer.memory})")

    # Only for debugging purposes
    def print_assignments(self, assignments):
        if assignments == {}: 
            print(Fore.MAGENTA + Style.BRIGHT  + "\nNo assignments happened ---------" + Style.RESET_ALL + Back.RESET)
            return

        print(Fore.CYAN + Style.BRIGHT + "\nProcess Assignments:" + Style.RESET_ALL)
        for process_name, computers in assignments.items():
            assigned_to = [comp.name for comp in computers]
            # print(f"{Style.BRIGHT + Fore.CYAN}[{Fore.WHITE}{Fore.CYAN}] -> {Fore.WHITE}")
            print(f"{Style.BRIGHT + Fore.CYAN}[{Fore.YELLOW}{process_name}{Fore.CYAN}] -> {Fore.WHITE}{', '.join(assigned_to)}{Style.RESET_ALL}")



    def distribute_processes_balanced(self) -> None:
        print(Fore.BLUE + Style.BRIGHT + "\nBALANCED ALGO." + Style.RESET_ALL)
        #Step 1
        self.sort_computers()
        self.sort_programs()

        assignments = {}

        print(Fore.YELLOW + "\nBefore Distribution:" + Style.RESET_ALL)
        self.print_computer_scores()

        # Step 2: Clear current processes from all computers before checking availability
        for name, computer in self.sorted_computer_list:
            self.clear_computer_processes(computer)

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

        print(Fore.GREEN + Style.BRIGHT + "\nAfter Distribution:" + Style.RESET_ALL)
        self.print_computer_scores()

        self.print_assignments(assignments)
    

    def distribute_processes_efficient_packing(self) -> None:
        print(Fore.BLUE + Style.BRIGHT + "\nEFFICIENT PACKING ALGO." + Style.RESET_ALL)

        # Step 1: Sort computers and programs
        self.sort_computers()
        self.sort_programs()

        assignments = {}

        print(Fore.YELLOW + "\nBefore Distribution:" + Style.RESET_ALL)
        self.print_computer_scores()

        # Step 2: Clear current processes from all computers before checking availability
        for name, computer in self.sorted_computer_list:
            self.clear_computer_processes(computer)

        # Step 3: Recalculate free resources for each computer after clearing old processes
        for name, computer in self.sorted_computer_list:
            computer.calculate_resource_usage()

        # Step 4: Assign processes using **Greedy Best-Fit Decreasing**
        for process_name, process in self.sorted_process_list:
            required_cores = int(process["cores"])
            required_memory = int(process["memory"])
            best_computer = None
            min_remaining_resources = float("inf")  # Start with the worst possible fit

            # Find the best-fitting computer
            for name, computer in self.sorted_computer_list:
                if computer.free_cores >= required_cores and computer.free_memory >= required_memory:
                    remaining_cores = computer.free_cores - required_cores
                    remaining_memory = computer.free_memory - required_memory
                    total_remaining = remaining_cores + remaining_memory  # Compute remaining resources

                    if total_remaining < min_remaining_resources:
                        min_remaining_resources = total_remaining
                        best_computer = computer

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

        print(Fore.GREEN + Style.BRIGHT +"\nAfter Distribution:" + Style.RESET_ALL)
        self.print_computer_scores()

        self.print_assignments(assignments)



    def distribute_processes_speedy(self) -> None:
        print(Fore.BLUE + Style.BRIGHT + "\nSPEEDY ALGO." + Style.RESET_ALL)

        # Step 1: Sort computers and programs
        self.sort_computers()
        self.sort_programs()

        assignments = {}

        print(Fore.YELLOW + "\nBefore Distribution:" + Style.RESET_ALL)
        self.print_computer_scores()

        # Step 2: Clear current processes from all computers before checking availability
        for name, computer in self.sorted_computer_list:
            self.clear_computer_processes(computer)

        # Step 3: Recalculate free resources for each computer after clearing old processes
        for name, computer in self.sorted_computer_list:
            computer.calculate_resource_usage()

        # Step 4: Assign processes using **First Fit**
        for process_name, process in self.sorted_process_list:
            required_cores = int(process["cores"])
            required_memory = int(process["memory"])
            assigned = False  # Track if process is assigned

            for name, computer in self.sorted_computer_list:
                if computer.free_cores >= required_cores and computer.free_memory >= required_memory:
                    if process_name not in assignments:
                        assignments[process_name] = []
                    assignments[process_name].append(computer)

                    # Reduce available resources
                    computer.free_cores -= required_cores
                    computer.free_memory -= required_memory

                    # Write the process to the computer's directory
                    self.write_process_file(computer, process_name, process)

                    assigned = True
                    break

            if not assigned:
                print(Fore.RED + f"Skipping {process_name}: Not enough resources on any computer!" + Style.RESET_ALL)

        print(Fore.GREEN + Style.BRIGHT +"\nAfter Distribution:" + Style.RESET_ALL)
        self.print_computer_scores()

        self.print_assignments(assignments)