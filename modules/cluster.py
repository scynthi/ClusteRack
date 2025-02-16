import os
import shutil
import random
import string
import time
from os import path as Path
from datetime import datetime
from modules.computer import Computer
from colorama import Fore, Style, Back
from modules.rebalancer import *

rebalancing_algos : list = ["load_balance", "best_fit", "fast"]

class Cluster:
    def __init__(self, path: str, parent):
        path = Path.normpath(fr"{path}")
        self.path = path

        cluster_name = path.split(os.sep)[-1]
        self.name = cluster_name
        self.root = parent
        
        self.computers = {}
        self._load_computers()

        # Ignore if `.klaszter` file is missing
        self.config_path = Path.join(path, ".klaszter")
        if not Path.exists(self.config_path):
            self.print(f"{Fore.YELLOW}Skipping {cluster_name}: No .klaszter file found.")
            return

        if not hasattr(self, "initialized"):
            self.initialized = False
            self.programs = {}  # Stores program details (name, instance count, cores, memory)
            self.instances = {}  # Stores instance details (id, running, date_started)
            self.distributable_instances = []

        self._load_programs()

        self.rebalancer = Rebalancer(self)
        self.set_rebalance_algo(0)
        self.run_rebalancer()

        self.print(f"{Fore.BLACK}{Back.GREEN}Cluster ({self.name}) initialized succesfully with {len(self.computers)} computer(s) and {len(self.programs)} program(s).{Back.RESET+Fore.RESET}\n")
        self.initialized = True


    def _load_computers(self):
        """Update the computer references"""
        self.computers = {}
        files: list = os.listdir(self.path)

        if ".klaszter" in files:
            files.remove(".klaszter")

        for file in files:
            self.computers[file] = Computer(Path.join(self.path, file), self)

        self._check_duplicate_computer_names()

    def _load_programs(self):
        """Load programs from cluster config file and from instance list"""

        with open(Path.join(self.path, ".klaszter"), "r", encoding="utf8") as file:
            lines = file.readlines()  # Read first
        lines = [line.strip() for line in lines]

        self.programs = {}

        # DO NOT RESET self.instances—this prevents losing knowledge of past instances!
        if not hasattr(self, "instances"):
            self.instances = {}

        self.distributable_instances = []

        for i in range(0, len(lines), 4):
            try:
                program_name = lines[i]
                required_count = int(lines[i + 1])
                cores = int(lines[i + 2])
                memory = int(lines[i + 3])

                # Store program requirements
                self.programs[program_name] = {
                    "required_count": required_count,
                    "cores": cores,
                    "memory": memory
                }

                skip_program = False
                if not self._validate_instance_placement(program_name, required_count):
                    while True:
                        user_input = self.user_input(
                            f"Not enough resources to fit {required_count} '{program_name}' instances! \n"
                            f"Enter a lower instance count (or type '0' to cancel): ").strip()
                        
                        if user_input.isdigit():
                            new_count = int(user_input)
                            if new_count == 0:
                                self.print(f"{Fore.RED}Skipping program ({program_name}) due to insufficient resources.")
                                skip_program = True
                                break

                            if self._validate_instance_placement(program_name, new_count):
                                required_count = new_count
                                break

                        print("Invalid input. Enter a valid number.")

                if skip_program: continue

                # Find and update ALL instances of this program
                all_instances = self._get_all_program_instances(program_name)
                
                # Validate and save them
                valid_instances = self._validate_and_update_instances(
                    program_name, cores, memory, all_instances
                )

                # Ensure program exists in self.instances
                if program_name not in self.instances:
                    self.instances[program_name] = {}

                # Update self.instances to reflect the changes
                for instance in valid_instances:
                    instance_id = instance["id"]

                    if instance_id not in self.instances[program_name]:
                        # New instance: Save it as if we just read it from the cluster
                        self.instances[program_name][instance["id"]] = {"status" : instance["status"],
                                                                        "cores" : instance["cores"], 
                                                                        "memory" : instance["memory"], 
                                                                        "computer" : instance["computer"],
                                                                        "date_started" : instance["date_started"]}
                    else:
                        # Existing instance: Just update computer info
                        self.instances[program_name][instance_id]["computer"] = instance["computer"]

                # Identify instances missing from the cluster but known in `self.instances`
                missing_instances = [
                    inst_id for inst_id in self.instances[program_name]
                    if inst_id not in [inst["id"] for inst in valid_instances]
                ]

                # If a missing instance exists, keep it but mark as unassigned
                for inst_id in missing_instances:
                    self.instances[program_name][inst_id]["computer"] = None  # Unassigned


                # Split valid instances into active and inactive
                active_valid_instances = []
                inactive_valid_instances = []
                for id, instance in self.instances[program_name].items():
                    instance["id"] = id
                    if instance.get("status") == True:
                        active_valid_instances.append(instance)
                    elif instance.get("status") == False:
                        inactive_valid_instances.append(instance)

                # If we dont have enough active instances
                if (len(active_valid_instances) < required_count) and inactive_valid_instances:
                    while True:
                        user_input = self.user_input(
                                                    f"Not enough active '{program_name}' instances to fulfill quota : {required_count}! \n"
                                                    f"{Fore.GREEN}Inactive instances found.{Fore.WHITE + Style.BRIGHT} Would you like to start them?{Style.RESET_ALL}\n"
                                                    f"1 - Yes\n"
                                                    f"2 - Cancel >> ").strip()
                        if user_input == '1':
                            while (len(active_valid_instances) < required_count) and inactive_valid_instances: 
                                instance_to_activate = inactive_valid_instances.pop(0) # Get oldest inactive instance
                                active_valid_instances.append(instance_to_activate) # Activate and move to active list
                                
                                self.instances[program_name][instance_to_activate['id']]["status"] = True # Update tracking data
                            break

                        if user_input == '2':
                            break

                        self.print(f"{Style.BRIGHT + Fore.RED}Please input a valid choice!")

                # Generate new instances as needed
                new_needed = required_count - len(active_valid_instances)
                if new_needed > 0:
                    while True:
                        user_input = self.user_input(
                                                    f"Not enough active '{program_name}' instances to fulfill quota : {required_count}! \n"
                                                    f"{Fore.WHITE + Style.BRIGHT} Would you like to start {Fore.GREEN}new ones?{Fore.RESET + Style.RESET_ALL}\n"
                                                    f"1 - Yes\n"
                                                    f"2 - Cancel >> ").strip()
                        if user_input == '1':
                            for _ in range(new_needed):
                                instance_id = self._generate_instance_id()
                                full_id = f"{program_name}-{instance_id}"
                                
                                self.instances[program_name][instance_id] = {"status" : True,
                                                                            "cores" : self.programs[program_name]["cores"], 
                                                                            "memory" : self.programs[program_name]["memory"], 
                                                                            "computer" : None,
                                                                            "date_started" : datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                                # Add to active list
                                active_valid_instances.append({"status" : self.instances[program_name][instance_id]["status"],
                                                                "cores" : self.instances[program_name][instance_id]["cores"], 
                                                                "memory" : self.instances[program_name][instance_id]["memory"], 
                                                                "computer" : self.instances[program_name][instance_id]["computer"],
                                                                "date_started" : self.instances[program_name][instance_id]["date_started"]})
                            break

                        if user_input == '2':
                            break

                        self.print(f"{Style.BRIGHT + Fore.RED}Please input a valid choice!")



                # Handle excess instances
                extra_instances_count = len(active_valid_instances) - required_count

                if extra_instances_count > 0: 
                    self.print(f"{Fore.YELLOW}Warning: extra '{program_name}' instances found!")

                    extra_instances = []
                    for i in range(extra_instances_count):
                        extra_instances.append(active_valid_instances[-(i+1)])


                    while True:
                        user_input = self.user_input(
                            f"{Style.BRIGHT}Do you want to\n"
                            f"(1) Deactivate extra instances\n"
                            f"(2) Delete them? (1/2): "
                        ).strip()
                        
                        if user_input == '1':
                            for instance in extra_instances:
                                instance_id = instance['id']
                        
                                # Only deactivate if currently active
                                if instance["status"]:
                                    active_valid_instances.remove(instance)

                                    # Deactivate and move to active list
                                    inactive_valid_instances.append(instance)
                                    self.instances[program_name][instance['id']]["status"] = False   
                            break

                        if user_input == '2':
                            for instance in extra_instances:
                                instance_id = instance['id']
                                try:
                                    if instance["status"]:
                                        active_valid_instances.remove(instance)
                                        del self.instances[program_name][instance['id']]

                                except Exception as e:
                                    self.print(f"{Fore.RED}Failed to delete {f"{program_name}-{instance_id}"}: {str(e)}")
                            break

                        self.print(f"{Style.BRIGHT + Fore.RED}Please input a valid choice!")

                print(active_valid_instances)
                print(inactive_valid_instances)

            except (IndexError, ValueError) as e:
                self.print(f"{Fore.RED}Error loading program: {str(e)}")
                continue

        # Recalculate after all changes
        self._check_duplicate_instance_ids()
        self._update_distributable_instances()

        # self.print("================================")
        # self.print(self.programs)
        # self.print(self.instances)
        # self.print(self.distributable_instances)
        # self.print("================================")


    def _get_all_program_instances(self, program_name):
        """Get all instances of a program regardless of specs"""
        instances = []
        for computer in self.computers.values():
            for filename, details in computer.get_prog_instances().items():
                if details["name"] == program_name:

                    instances.append({
                        "id": filename.split("-")[-1],
                        "status": details["status"],
                        "date_started": details["date_started"],
                        "computer": computer.name,
                        "cores": details["cores"],
                        "memory": details["memory"]
                        })
        return instances
                 
    def _validate_and_update_instances(self, program_name, req_cores, req_mem, instances):
        """Update instances to match program specs"""
        valid = []
        for instance in instances:
            computer = self.computers.get(instance["computer"])
            if not computer:
                continue

            # Update specs if needed
            needs_update = False
            if instance["cores"] != req_cores:
                self.edit_instance(
                    f"{program_name}-{instance['id']}",
                    "cores",
                    req_cores
                )
                needs_update = True
                
            if instance["memory"] != req_mem:
                self.edit_instance(
                    f"{program_name}-{instance['id']}",
                    "memory",
                    req_mem
                )
                needs_update = True

            # Re-validate after updates
            if needs_update:
                new_details = computer.get_prog_instance_info(
                    f"{program_name}-{instance['id']}"
                )
                if new_details:
                    valid.append({
                        "id": instance['id'],
                        "status": new_details["status"],
                        "date_started": new_details["date_started"],
                        "computer": computer.name,
                        "cores": new_details["cores"],
                        "memory": new_details["memory"]
                    })
            else:
                valid.append(instance)
        return valid

    def _validate_instance_placement(self, program_name, required_count):
        """Check if the cluster has enough space to fit the required amount of a program"""
        # 1️ Get available resources from all computers
        total_free_cores = sum(comp.free_cores for comp in self.computers.values())
        total_free_memory = sum(comp.free_memory for comp in self.computers.values())

        # Get individual computer resource availability
        available_computers = sorted(
            self.computers.values(),
            key=lambda c: (-c.free_cores, -c.free_memory)  # Sort by max resources
        )

        # Get program requirements
        req_cores = self.programs[program_name]["cores"]
        req_memory = self.programs[program_name]["memory"]

        # Check if we even have enough total cluster resources
        if required_count * req_cores > total_free_cores or required_count * req_memory > total_free_memory:
            return False  # Not enough resources overall

        # Try placing instances one by one
        instance_count = 0
        for computer in available_computers:
            while (computer.free_cores >= req_cores and computer.free_memory >= req_memory
                    and instance_count < required_count):
                # Place an instance on this computer
                computer.free_cores -= req_cores
                computer.free_memory -= req_memory
                instance_count += 1

            # Stop once all instances are placed
            if instance_count == required_count:
                return True

        # If we couldn't place all instances, return False
        return False  

    def _generate_instance_id(self) -> str:
        """Generates a unique 6-character instance ID that does not exist anywhere in the cluster."""
        existing_ids = set()

        # Collect all existing IDs from instances
        for program_instances in self.instances.values():
            existing_ids.update(program_instances.keys())

        while True:
            new_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            
            if new_id not in existing_ids:
                return new_id 

    def _check_duplicate_instance_ids(self):
        """Detects duplicate instance IDs and resolves conflicts by user input."""
        seen_ids = {}  # Maps IDs to program names

        for program_name, instances in self.instances.items():
            for instance_id in list(instances.keys()):  # Convert to list for safe modification
                instance_suffix = instance_id  # This is already the 6-char unique ID

                if instance_suffix in seen_ids:
                    existing_program = seen_ids[instance_suffix]
                    self.print(f"{Fore.RED}Duplicate instance ID detected: {program_name}-{instance_id} "
                            f"{Style.BRIGHT + Fore.RED}(Conflict between {program_name} and {existing_program})")

                    while True:
                        user_choice = self.user_input(
                            f"{Style.BRIGHT}Would you like to:\n"
                            f"1) Rename {program_name}-{instance_id} manually\n"
                            f"2) Generate a new unique ID automatically\n"
                            f"Enter choice (1/2): "
                        ).strip()

                        if user_choice == "1":
                            new_id = self.user_input("Enter new unique ID (6 characters): ").strip()
                            if len(new_id) == 6 and new_id.isalnum() and new_id not in seen_ids:
                                new_instance_id = new_id  # Just store the new ID, program name is already mapped
                                self.instances[program_name][new_instance_id] = self.instances[program_name].pop(instance_id)
                                seen_ids[new_id] = program_name  # Update tracking
                                break
                            else:
                                self.print(f"{Style.BRIGHT + Fore.RED}Invalid ID. Ensure it is 6 alphanumeric characters and unique.")
                        
                        elif user_choice == "2":
                            new_id = self._generate_instance_id()
                            new_instance_id = new_id  # Just store the unique ID
                            self.instances[program_name][new_instance_id] = self.instances[program_name].pop(instance_id)
                            seen_ids[new_id] = program_name  # Update tracking
                            break

                        else:
                            self.print(f"{Style.BRIGHT + Fore.RED}Please input a valid choice! Please enter 1 or 2")


                else:
                    seen_ids[instance_suffix] = program_name  # No conflict save ID as seen

    def _check_duplicate_computer_names(self):
        """Ensures all computers in the cluster have unique names."""
        seen_names = set()
        duplicates = []

        for name in list(self.computers.keys()):  # Iterate over a copy
            if name in seen_names:
                duplicates.append(name)
            else:
                seen_names.add(name)

        for duplicate in duplicates:
            while duplicate in self.computers:
                self.print(f"{Fore.RED}Duplicate computer name detected: {duplicate}")

                user_input = self.user_input(
                    f"{Style.BRIGHT}Would you like to:\n"
                    f"1) Rename {duplicate} manually\n"
                    f"2) Ignore this computer\n"
                    f"Enter choice (1/2): "
                ).strip()

                if user_input == "1":
                    new_name = self.user_input("Enter a new unique name: ").strip()
                    if new_name and new_name not in self.computers:
                        self.rename_computer(duplicate, new_name)
                    else:
                        print("Invalid name or already exists. Try again.")
                elif user_input == "2":
                    self.print(f"{Fore.YELLOW}Ignoring computer '{duplicate}' from cluster.")
                    del self.computers[duplicate]
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2.")

    def _update_distributable_instances(self):
        """Include ALL instances for redistribution"""
        self.distributable_instances = []
        for program_name in self.instances:
            for instance_id, data in self.instances[program_name].items():

                self.distributable_instances.append(
                    {
                        "id": instance_id,
                        "program": program_name,
                        "date_started": data["date_started"],
                        "cores": self.instances[program_name][instance_id]["cores"],
                        "memory": self.instances[program_name][instance_id]["memory"],
                        "current_computer": data.get("computer"),
                        "status" : self.instances[program_name][instance_id]["status"]
                    }
                )


#========Public========
# Cluster
    def reload_cluster(self):
        self._load_computers()
        self._load_programs()
        self.run_rebalancer()

        self.print(f"{Back.BLUE + Fore.WHITE}Successfully reloaded cluster")


# Rebalancer
    def set_rebalance_algo(self, new_algo_id: int = 0):
        self.rebalancer.default_rebalance_algo = rebalancing_algos[new_algo_id]

    def run_rebalancer(self):
        self.rebalancer.run_default_rebalance_algo()


# Computers
    def create_computer(self, computer_name: str, cores: int, memory: int) -> Computer:
        full_path: str = Path.join(self.path, computer_name)

        if Path.exists(full_path):
            self.print(f"{Fore.RED}Computer ({computer_name}) already exists and will NOT be created.")
            return self.computers[computer_name]
        
        try:
            os.mkdir(full_path)
            with open(Path.join(full_path, ".szamitogep_config"), "w", encoding="utf8") as config_file:
                config_file.write(f"{cores}\n{memory}")

            self.print(f"{Fore.GREEN}Computer ({computer_name}) created successfully.")
            
            self._load_computers()
            return self.computers.get(computer_name)
        except:
            self.print(f"{Fore.RED}Error while creating computer '{computer_name}'.")
            return

    def delete_computer(self, computer_name: str, mode: str = "try"):
        """Deletes computers either with soft mode('try') or force mode('f')"""

        full_path: str = Path.join(self.path, computer_name)

        if not Path.exists(full_path):
            self.print(f"{Fore.RED}Computer ({computer_name}) does not exist! Check the name and retry.")
            return False
        
        if mode == "f":
            try:
                shutil.rmtree(full_path)

                self.print(f"{Fore.GREEN}Successfully force deleted computer ({computer_name}).")
                
                self.reload_cluster()
                return True
            
            except Exception as e:
                self.print(f"{Back.RED}{Fore.BLACK}CRITICAL ERROR DETECTED: force deletion failed for computer {computer_name} : {e}.")
                return False

        elif mode == "try":
            try:
                computer : Computer = self.computers[computer_name]
                if computer.get_prog_instances():
                    self.print(f"{Fore.RED}Unable to delete computer '{computer_name}'. It has processes, try using delete_computer(computer_name, 'f').")
                    return False
                
                shutil.rmtree(full_path, ignore_errors=True)

                self.print(f"{Fore.GREEN}Computer '{computer_name}' deleted successfully.")
                self.reload_cluster()
                return True

            except:
                self.print(f"{Fore.RED}Unable to delete computer ({computer_name}).")
                return False

        else:
            self.print(f"{Fore.RED}Can not delete computer ({computer_name}) please specify a valid mode")
            return False

    def rename_computer(self, old_name: str, new_name: str) -> bool:
        """Attempts to rename a computer, ensuring the new name is unique."""
        if not self.initialized:
            self.print(f"{Fore.RED}Cluster failed to initialize, renaming not possible.")
            return False

        if not new_name.isalnum():
            self.print(f"{Fore.RED}The new computer name must be an alfanumerical value! Correct the name and retry.")

        if new_name in self.computers:
            self.print(f"{Fore.RED}A computer named '{new_name}' already exists. Choose another name.")
            return False

        old_path = Path.join(self.path, old_name)
        new_path = Path.join(self.path, new_name)

        if not Path.exists(old_path):
            self.print(f"{Fore.RED}Computer '{old_name}' does not exist.")
            return False

        try:
            os.rename(old_path, new_path)

            # Update self.computers reference without reloading everything
            self.computers[new_name] = self.computers.pop(old_name)
            self.computers[new_name].name = new_name
            self.computers[new_name].path = new_path

            self.print(f"{Fore.GREEN}Computer '{old_name}' successfully renamed to '{new_name}'.")

            return True
        
        except Exception as e:
            self.print(f"{Fore.RED}Error renaming '{old_name}': {e}")
            return False

    def edit_computer_resources(self, computer_name: str, cores: int, memory: int) -> bool:
        """Edits a computer's resources while ensuring it can still support running instances."""

        if computer_name not in self.computers:
            self.print(f"{Fore.RED}Computer ({computer_name}) does not exist!")
            return False

        computer: Computer = self.computers[computer_name]

        # Get resource usage before making changes
        usage = computer.calculate_resource_usage()
        min_required_cores = computer.memory - computer.free_memory  # Running instances' memory usage
        min_required_memory = computer.cores - computer.free_cores  # Running instances' core usage

        # Check if new resources are valid
        if cores < min_required_cores:
            self.print(f"{Fore.RED}Can't set core count to {cores} on ({computer.name}). It needs at least {min_required_cores} cores.")
            return False
            
        if memory < min_required_memory:
            self.print(f"{Fore.RED}Can't set memory size to {memory} on ({computer.name}). It needs at least {min_required_memory} memory.")
            return False

        # Update attributes
        prev_cores, prev_memory = computer.cores, computer.memory
        computer.cores = cores
        computer.memory = memory

        # Validate new resources
        computer.calculate_resource_usage()
        if not computer.validate_computer():
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR: Computer ({computer.name}) cannot support running instances. Reverting resources.")
            computer.cores, computer.memory = prev_cores, prev_memory
            computer.calculate_resource_usage()
            return False

        # Update .szamitogep_config file
        config_path = Path.join(computer.path, ".szamitogep_config")
        with open(config_path, "w", encoding="utf-8") as file:
            file.write(f"{computer.cores}\n{computer.memory}")

        self.print(f"{Fore.GREEN}Successfully edited resources on ({computer.name}). Memory: {prev_memory} -> {memory}, Cores: {prev_cores} -> {cores}")

        return True


# Programs
    def add_program(self, program_name: str, instance_count : int, cores: int, memory: int):
        """Adds programs to the cluster config file and reloads the cluster."""

        if program_name in self.programs:
            self.print(f"{Fore.RED}There is alrady a program named {program_name}")
            return False
        
        data = f"{program_name}\n{instance_count}\n{cores}\n{memory}\n"
    
        cluster_config_path = Path.join(self.path, ".klaszter")
        with open(cluster_config_path, "a", encoding="utf8") as config_file:
            config_file.write(data)

        self._load_programs()
        self.run_rebalancer()
        return True

    def kill_program(self, program_name : str):
        """Kills programs by removing all of its instances then deleting itself from the programs and from the config file."""
        
        if program_name not in self.programs:
            self.print(f"{Fore.RED}There is no program named {program_name} in the cluster. Check name and try again!")
            return False
        
        instances_to_kill = []
        for instance_id in self.instances[program_name]:
            instances_to_kill.append(instance_id)
        
        for id in instances_to_kill:
            self.kill_instance(id, reload=False)
        
        del self.programs[program_name]
    
        data = f""
        with open(self.config_path, "w+", encoding="utf8") as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]

            for prog_name, details in self.programs.items():
                data += f"{prog_name}\n{details["required_count"]}\n{details["cores"]}\n{details["memory"]}\n"
            
            file.write("")
            file.write(data)

        self._load_programs()
        return True

    def stop_program(self, program_name : str):
        """Deactivates all instances of a program and sets instance count to 0"""
        if program_name not in self.programs:
            self.print(f"{Fore.RED}There is no program named {program_name} in the cluster. Check name and try again!")
            return False
        
        instances_to_stop = []
        for instance_id in self.instances[program_name]:
            instances_to_stop.append(instance_id)

        for instance_id in instances_to_stop:
            self.edit_instance_status(instance_id, False, reload=False)
        
        self.programs[program_name]["required_count"] = 0
        
        self._load_programs()
        self.run_rebalancer()
        return True

    def edit_program_resources(self, program_name: str, property_to_edit:str, new_value):
        """Can edit the instance count, the cores and the memory required"""
        # Check if the modification can be made eg. we have enough space on the cluster to do it(applies to all 3 properties)
        # We will need to take the and program change its property in the .klaszter file
        # reload the programs

        


        pass

    def rename_program(self, program_name : str, new_program_name: str):
        """Edit the name of a program without effecting the state of its instances"""

        if program_name not in self.programs:
            self.print(f"{Fore.RED}There is no a program named {program_name} in the cluster. Check name and try again!")
            return False
        
        if new_program_name in self.programs:
            self.print(f"{Fore.RED}There is already a program named {new_program_name} in the cluster. Check name and try again!")
            return False
        
        # Remove old instnace files from file system
        target_instance_ids = []
        for instance_id in self.instances[program_name]:
            target_instance_ids.append(instance_id)
        
        for instance_id in target_instance_ids:
            full_name = f"{program_name}-{instance_id}"

            for computer in self.computers:
                comp : Computer = self.computers[computer]
                for file in os.listdir(comp.path):
                    if file == full_name:
                        full_path = Path.join(comp.path, file)
                        os.remove(full_path)
                    
        # Rename in self.programs and self.instances
        self.programs[new_program_name] = self.programs.pop(program_name)
        self.instances[new_program_name] = self.instances.pop(program_name)
        
        # Update name in config file
        data = f""
        with open(self.config_path, "w+", encoding="utf8") as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]

            for prog_name, details in self.programs.items():
                data += f"{prog_name}\n{details["required_count"]}\n{details["cores"]}\n{details["memory"]}\n"
            
            file.write("")
            file.write(data)

        self._load_programs()
        self.run_rebalancer()
        return True


#Instances
    def add_instance(self, program_name : str, instance_id : str):
        # Check if the cluster has enough space for it
        # If it oversteps the instance count the of the program we need to ask the user
        # 1 We add the one to the instance count that and then put the instance on
            # here we need to use a function that is not yet created which will be the edit program function with it we can change the name instance count and resources of a program and then reload the programs
        
        # 2 We add the instance as an inactive instance 
        # 3 the user should be able to abort the process
        # then save it to the self.instances dict 
        # reload the programs
        pass

    def edit_instance_status(self, instance_id: str, new_status: str, reload : bool = True) -> bool:
        """Edit instance status to true or false"""
        
        target_program, instance_to_stop = self.get_instance_by_id(instance_id)

        if not instance_to_stop:
            self.print(f"{Fore.RED}Could not find instance to stop.")
            return False
        
        self.instances[target_program][instance_id]["status"] = new_status
        
        full_name = f"{target_program}-{instance_id}"
        self.print(f"{Fore.GREEN}Instance {full_name} stopped successfully.")

        if reload:
            self._load_programs()
        return True

    def kill_instance(self, instance_id : str, reload : bool = True):
        """Kills an instance and removes references, can be used for batch removal is reload is turned off."""

        target_program = ""
        target_computer = ""
        
        target_program, instance_to_kill = self.get_instance_by_id(instance_id)

        if not instance_to_kill:
            self.print(f"{Fore.RED}Could not find instance to kill.")
            return False

        full_name = f'{target_program}-{instance_id}'
        for computer in self.computers:
            instances = self.computers[computer].get_prog_instances()

            if full_name in instances.keys():
                target_computer = computer
        
        del self.instances[target_program][instance_id]

        target_path = Path.join(self.path, target_computer, full_name)
        if Path.exists(target_path):
            os.remove(target_path)

        self.print(f"{Fore.GREEN}Instance {full_name} killed successfully.")
        
        if reload:
            self._load_programs()
        return True

        
        # if instance_id in self.instances: 
            

        # this function should take in the instance id and then kill the instance by deleting it from the filesystem
        # It should also remove itself from the self.instances dict so that we dont have it on reload 
        # Then it should reload the programs
        pass

    def change_instance_id(self, instance_id : str, new_instnace_id : str):
        #This function should take in the instance id  and then change the id of the instance from the old id to the new one
        # It should also save itself to the self.instances dict to keep it 
        # We should reload the programs
        pass


#UTILS
    def get_instance_by_id(self, id : str) -> tuple:
        for program in self.instances:
            target_program = program
            program : dict = self.instances[program]

            for instance in program:
                if instance == id:
                    return (target_program, program[id])

    def user_input(self, input_question : str) -> str:
        if self.root.ui == None:
            user_input = input(input_question)
            return user_input
        else:
            pass

    def print(self, text: str):
        """Debugging print method."""
        print(f"{Fore.BLACK}{Back.CYAN}[{Back.WHITE}{self.name}{Back.CYAN}]{Back.RESET}{Fore.CYAN}: {text}{Style.RESET_ALL}")