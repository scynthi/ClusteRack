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
    def __init__(self, path: str):
        path = Path.normpath(fr"{path}")
        self.path = path

        cluster_name = path.split(os.sep)[-1]
        self.name = cluster_name
        
        self.computers = {}
        self._load_computers()

        # Ignore if `.klaszter` file is missing
        config_path = Path.join(path, ".klaszter")
        if not Path.exists(config_path):
            self.print(f"{Fore.YELLOW}Skipping {cluster_name}: No .klaszter file found.")
            return

        if not hasattr(self, "initialized"):
            self.initialized = False
            self.programs = {}  # Stores program details (name, instance count, cores, memory)
            self.instances = {}  # Stores instance details (id, running, date_started)
            self.distributable_instances = []

        self._load_programs(config_path)

        self.rebalancer = Rebalancer(self)
        self.set_rebalance_algo(0)
        self.run_rebalancer()

        self.print(f"{Fore.BLACK}{Back.GREEN}Cluster ({self.name}) initialized succesfully with {len(self.computers)} computer(s) and {len(self.programs)} program(s).{Back.RESET+Fore.RESET}\n")
        self.initialized = True

        #Debug
        # self.print("================================")
        # self.print(self.programs)
        # self.print(self.instances)
        # self.print(self.distributable_instances)
        # self.print("================================")

    def _load_computers(self):
        """Update the computer references"""
        files: list = os.listdir(self.path)

        if ".klaszter" in files:
            files.remove(".klaszter")

        computer_dict: dict = {}

        for file in files:
            computer_dict[file] = Computer(Path.join(self.path, file))
        
        self.computers : dict = computer_dict

    def _load_programs(self, cluster_path):
        """Load programs with accurate state tracking"""

        with open(cluster_path, "r", encoding="utf8") as file:
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
                        user_input = input(
                            f"Not enough resources to fit {required_count} '{program_name}' instances! \n"
                            f"Enter a lower instance count (or type '0' to cancel): "
                        ).strip()
                        
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
                while (len(active_valid_instances) < required_count) and inactive_valid_instances: 
                    instance_to_activate = inactive_valid_instances.pop(0) # Get oldest inactive instance
                    active_valid_instances.append(instance_to_activate) # Activate and move to active list
                    
                    self.instances[program_name][instance_to_activate['id']]["status"] = True # Update tracking data

                # Generate new instances as needed
                new_needed = required_count - len(active_valid_instances)
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


                # Handle excess instances
                extra_instances_count = len(active_valid_instances) - required_count

                if extra_instances_count > 0: 
                    self.print(f"{Fore.YELLOW}Warning: extra '{program_name}' instances found!")

                    extra_instances = []
                    for i in range(extra_instances_count):
                        extra_instances.append(active_valid_instances[-(i+1)])


                    while True:
                        user_choice = input(
                            f"Do you want to (1) Deactivate excess instances or (2) Delete them? (1/2): "
                        ).strip()

                        if user_choice in {"1", "2"}:
                            break
                        print("Invalid choice. Please enter 1 or 2.")

                    for instance in extra_instances:
                        instance_id = instance['id']
                        
                        if user_choice == "1":
                            # Only deactivate if currently active

                            if instance["status"]:
                                active_valid_instances.remove(instance)

                                # Deactivate and move to active list
                                inactive_valid_instances.append(instance)
                                self.instances[program_name][instance['id']]["status"] = False
                        else:
                            try:
                                if instance["status"]:
                                    active_valid_instances.remove(instance)
                                    del self.instances[program_name][instance['id']]

                            except Exception as e:
                                self.print(f"{Fore.RED}Failed to delete {f"{program_name}-{instance_id}"}: {str(e)}")

                # Recalculate after all changes
                self._update_distributable_instances()

            except (IndexError, ValueError) as e:
                self.print(f"{Fore.RED}Error loading program: {str(e)}")
                continue
# |
# |
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
        # 1️ Get available resources from all computers
        total_free_cores = sum(comp.free_cores for comp in self.computers.values())
        total_free_memory = sum(comp.free_memory for comp in self.computers.values())

        # Get individual computer resource availability
        available_computers = sorted(
            self.computers.values(),
            key=lambda c: (-c.free_cores, -c.free_memory)  # Sort by max resources
        )

        # 2 Get program requirements
        req_cores = self.programs[program_name]["cores"]
        req_memory = self.programs[program_name]["memory"]

        # 3️ Check if we even have enough total cluster resources
        if required_count * req_cores > total_free_cores or required_count * req_memory > total_free_memory:
            return False  # Not enough resources overall

        # 4️ Try placing instances one by one
        instance_count = 0
        for computer in available_computers:
            while (computer.free_cores >= req_cores and computer.free_memory >= req_memory
                    and instance_count < required_count):
                # "Place" an instance on this computer
                computer.free_cores -= req_cores
                computer.free_memory -= req_memory
                instance_count += 1

            # Stop once all instances are placed
            if instance_count == required_count:
                return True

        # 5️ If we couldn't place all instances, return False
        return False  



    def _get_valid_existing_instances(self, program_name, req_cores, req_mem):
        """Get valid instances matching exact specifications"""
        instances = []
        for computer in self.computers.values():
            for filename, details in computer.get_prog_instances().items():
                if (details["name"] == program_name and
                    details["cores"] == req_cores and
                    details["memory"] == req_mem):
                    instances.append({
                        "id": filename.split("-")[-1],  # Extract unique ID part
                        "status": details["status"],
                        "date_started": details["date_started"],
                        "computer": computer.name
                    })
        return instances

    def _generate_instance_id(self):
        """Generates a unique 6-character instance ID."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    def _update_distributable_instances(self):
        """Include ALL instances for redistribution"""
        self.distributable_instances = [
            {
                "id": instance_id,
                "program": program_name,
                "date_started": data["date_started"],
                "cores": self.programs[program_name]["cores"],
                "memory": self.programs[program_name]["memory"],
                "current_computer": data.get("computer"),
                "status" : self.instances[program_name][instance_id]["status"]
            }
            for program_name in self.instances
            for instance_id, data in self.instances[program_name].items()
        ]

#================
    def reload_cluster(self):
        self._load_computers()
        self._load_programs(Path.join(self.path, ".klaszter"))
        self.run_rebalancer()

        self.print(f"{Back.BLUE + Fore.WHITE}Successfully reloaded cluster")


    def set_rebalance_algo(self, new_algo_id: int = 0):
        self.rebalancer.default_rebalance_algo = rebalancing_algos[new_algo_id]

    def run_rebalancer(self):
        self.rebalancer.run_default_rebalance_algo()


    def create_computer(self, computer_name: str, cores: int, memory: int) -> Computer:
        full_path: str = Path.join(self.path, computer_name)

        if Path.exists(full_path):
            self.print(f"{Fore.RED}Computer ({computer_name}) already exists and will NOT be created.")
            return self.computers[computer_name]
        
        try:
            os.mkdir(full_path)
            config_file = open(Path.join(full_path, ".szamitogep_config"), "w", encoding="utf8")
            config_file.write(f"{cores}\n{memory}")
            config_file.close()

            self.print(f"{Fore.GREEN}Computer ({computer_name}) created successfully.")
            
            self._load_computers()
            return Computer(full_path)
        except:
            self.print(f"{Fore.RED}Error while creating computer '{computer_name}'.")
            return

    def delete_computer(self, computer_name: str, mode: str = "try"):
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
                    self.print(f"{Fore.RED}Unable to delete computer '{computer_name}'. It has processes, try using force_delete_computer().")
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

    def rename_computer(self, computer_name : str, new_name : str) -> bool:
        if not self.initialized:
            self.print(f"{Fore.RED}Cluster failed to initialize so renaming can't be done.")
            return False
        
        try:
            computer_dir: str = Path.join(self.path, computer_name)
            
            if not Path.exists(computer_dir):
                self.print(f"{Fore.RED}Computer with the name {computer_dir} does not exist.")
                return False
            
            new_path: str = Path.join(self.path, new_name)

            os.rename(computer_dir, new_path)
            self.print(f"{Fore.GREEN}Computer folder renamed to '{new_name}' successfully.")

            self.reload_cluster()

            return True
            
        except Exception as e:
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: Error renaming computer: {e}")
            return False

    def edit_computer_resources(self, computer_name: str, cores: int, memory: int) -> bool:
        computer : Computer = self.computers[computer_name]    
        
        min_cores: int = computer.cores - computer.free_cores
        min_memory: int = computer.memory - computer.free_memory

        if cores < min_cores:
            self.print(f"{Fore.RED}Can't set core count to {cores} on computer ({computer.name}). Required minimum cores: {min_cores} ")
            return False
            
        if memory < min_memory:
            self.print(f"{Fore.RED}Can't set memory size to {memory} on computer ({computer.name}). Required minimum memory size: {min_memory} ")
            return False

        prev_cores: int = computer.cores
        prev_memory: int = computer.memory

        computer.cores = cores
        computer.memory = memory
            
        if computer.validate_computer():
            computer.calculate_resource_usage()

            with open(Path.join(computer.path, ".szamitogep_config"), "w", encoding="utf-8") as file:
                file.write(f"{computer.cores}\n{computer.memory}")

            self.print(f"{Fore.GREEN}Succesfully edited resources on computer ({computer.name}). Memory: {prev_memory} -> {memory}, cores: {prev_cores} -> {cores}")
            self.reload_cluster()

            return True
        
        else:
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: can't validate computer ({computer.name}). Setting back previus resources.")
            computer.cores = prev_cores
            computer.memory = memory
            computer.calculate_resource_usage()
            return False


    def edit_instance(self, instance_id: str, property_name: str, new_value: str) -> bool:
        """Edit instance with full state synchronization"""
        # Find target computer using full instance ID
        target_computer = next(
            (comp for comp in self.computers.values() 
             if instance_id in comp.get_prog_instances()), 
            None
        )

        if not target_computer:
            self.print(f"{Fore.RED}Instance {instance_id} not found")
            return False

        # Validate property
        valid_props = ["status", "cores", "memory", "computer"]
        if property_name not in valid_props:
            self.print(f"{Fore.RED}Invalid property: {property_name}")
            return False

        # Special handling for status
        if property_name == "status":
            new_value = "AKTÍV" if new_value else "INAKTÍV"

        # Perform edit
        if target_computer.edit_instance(instance_id, property_name, new_value):
            program = instance_id.split("-")[0]
            instance_data = self.instances.get(program, {}).get(instance_id)
            
            if instance_data:
                # Update local state
                if property_name == "status":
                    instance_data["active"] = (new_value == "AKTÍV")
                elif property_name == "computer":
                    instance_data["computer"] = new_value
                else:
                    instance_data[property_name] = int(new_value)
                
                # Update distributable list
                self._update_distributable_instances()
            
            return True
        return False


    def print(self, text: str):
        """Debugging print method."""
        print(f"{Fore.BLACK}{Back.CYAN}[{Back.WHITE}{self.name}{Back.CYAN}]{Back.RESET}{Fore.CYAN}: {text}{Style.RESET_ALL}")