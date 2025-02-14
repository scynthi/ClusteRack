import os
import random
import string
from os import path as Path
from datetime import datetime
from modules.computer import Computer
from colorama import Fore, Style, Back
from modules.rebalancer import *

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

        self.programs = {}  # Stores program details (name, instance count, cores, memory)
        self.instances = {}  # Stores instance details (id, running, date_started)
        self.distributable_instances = []

        self._load_programs(config_path)
        self.print(f"{Fore.GREEN}Cluster ({self.name}) initialized with {len(self.programs)} programs.")

        self.print(f"{Fore.BLACK}{Back.GREEN}Cluster ({self.name}) initialized succesfully with {len(self.computers)} computer(s).{Back.RESET+Fore.RESET}\n")

        # self.print(self.programs)
        self.print(self.instances)
        # self.print(self.distributable_instances)


    def _load_programs(self, klaszter_path):
        """Load programs with accurate state tracking"""
        with open(klaszter_path, "r", encoding="utf8") as file:
            lines = [line.strip() for line in file.readlines()]

        self.programs = {}
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

                # Find all valid existing instances
                existing_instances = self._get_valid_existing_instances(
                    program_name, cores, memory
                )

                # Initialize tracking for this program
                self.instances[program_name] = {}
                active_count = 0

                # Process existing instances FIRST
                for idx, instance in enumerate(existing_instances):
                    full_id = f"{program_name}-{instance['id']}"
                    is_active = idx < required_count
                    
                    # Add to tracking FIRST
                    self.instances[program_name][full_id] = {
                        "date_started": instance["date_started"],
                        "computer": instance["computer"],
                        "active": instance["status"]  # Initial state from file
                    }

                    # THEN update status if needed
                    if instance["status"] != is_active:
                        self._set_instance_status(full_id, is_active)
                    
                    if self.instances[program_name][full_id]["active"]:
                        active_count += 1

                # Create new instances if needed
                new_needed = max(required_count - active_count, 0)
                for _ in range(new_needed):
                    instance_id = f"{program_name}-{self._generate_instance_id()}"
                    self.instances[program_name][instance_id] = {
                        "date_started": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "computer": None,
                        "active": True
                    }

                # Update distributable instances
                self._update_distributable_instances()

            except (IndexError, ValueError) as e:
                self.print(f"{Fore.RED}Error loading program: {str(e)}")
                continue


    def _find_matching_instances(self, program_name, req_cores, req_mem):
        """Find all instances matching program specs across cluster"""
        matching = []
        for computer in self.computers.values():
            instances = computer.get_prog_instances()
            for filename, details in instances.items():
                if (details["name"] == program_name and
                    details["cores"] == req_cores and
                    details["memory"] == req_mem):
                    matching.append({
                        "id": details["id"],  # The unique ID part
                        "active": details["status"],
                        "computer": computer.name,
                        "date_started": details["date_started"]
                    })
        return matching


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

    
    def _update_distributable_instances(self):
        """Refresh distributable instances list"""
        self.distributable_instances = [
            {
                "id": instance_id,
                "program": program_name,
                "date_started": data["date_started"],
                "cores": self.programs[program_name]["cores"],
                "memory": self.programs[program_name]["memory"]
            }
            for program_name in self.instances
            for instance_id, data in self.instances[program_name].items()
            if data["computer"] is None
        ]


    def _set_instance_status(self, full_id: str, active: bool):
        """Update instance status with existence check"""
        # Check if instance exists in tracking
        program = full_id.split("-")[0]
        if program not in self.instances or full_id not in self.instances[program]:
            self.print(f"{Fore.RED}Instance {full_id} not in tracking")
            return

        # Rest of the method remains the same
        success = self.edit_instance(full_id, "status", active)
        
        if success:
            self.instances[program][full_id]["active"] = active
            self._update_distributable_instances()


    def _clean_invalid_instances(self):
        """Remove instances that don't match any program requirements"""
        all_program_specs = {
            prog: (self.programs[prog]["cores"], self.programs[prog]["memory"])
            for prog in self.programs
        }

        for computer in self.computers.values():
            instances = computer.get_prog_instances()
            for instance_id, details in instances.items():
                if not details:
                    continue
                
                # Check if instance matches any program requirements
                match_found = any(
                    details["name"] == prog and
                    details["cores"] == spec[0] and
                    details["memory"] == spec[1]
                    for prog, spec in all_program_specs.items()
                )
                
                if not match_found:
                    try:
                        invalid_path = Path.join(computer.path, instance_id)
                        if Path.exists(invalid_path):
                            os.remove(invalid_path)
                            self.print(f"{Fore.YELLOW}Removed orphaned instance {instance_id}")
                    except Exception as e:
                        self.print(f"{Fore.RED}Failed to remove invalid instance: {str(e)}")


    def _load_computers(self):
        """Update the computer references"""
        files: list = os.listdir(self.path)

        if ".klaszter" in files:
            files.remove(".klaszter")

        computer_dict: dict = {}

        for file in files:
            computer_dict[file] = Computer(Path.join(self.path, file))
        
        self.computers : dict = computer_dict


    def _generate_instance_id(self):
        """Generates a unique 6-character instance ID."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


    def _generate_instance_list(self):
        """Creates a flat list of all program instances for the rebalancer."""
        instance_list = []

        for program_name, instances in self.instances.items():
            cores = self.programs[program_name]["cores"]
            memory = self.programs[program_name]["memory"]

            for instance_id, instance_data in instances.items():
                instance_list.append({
                    "name": f"{program_name}-{instance_id}",
                    "running": instance_data["running"],
                    "cores": cores,
                    "memory": memory,
                    "date_started": instance_data["date_started"]
                })

        return instance_list
    

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