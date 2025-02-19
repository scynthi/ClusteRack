import os
import re
import shutil
import random
import string
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

        self.active_inst_num : int = 0
        self.inactive_inst_num : int = 0
        
        # Ignore if `.klaszter` file is missing
        self.config_path = Path.join(path, ".klaszter")
        if not Path.exists(self.config_path):
            while True:
                user_input = self.user_input(
                    f"Nincs konfigurációs file a {self.path} -ban\n"
                    f"{Fore.WHITE + Style.BRIGHT}Szeretne generálni egyet?\n"
                    f"1 - Igen\n"
                    f"2 - Nem >> ").strip()

                if user_input == "1":
                    try:
                        open(Path.join(self.path, ".klaszter"), "w", encoding="utf8")
                        self.print(f"{Fore.GREEN}Cluster config file created succesfully. Reloading cluster now. . .")
                        self.__init__(self.path, self.root)
                        return
                    except:
                        self.print(f"{Fore.RED}Error during cluster file creation. Skipping cluster. . .")
                        return

                elif user_input == "2":
                    self.print(f"{Fore.WHITE}Skipping folder")

                self.print(f"{Fore.RED}Choose a valid option.")



        if not hasattr(self, "initialized"):
            self.initialized = False
            self.programs = {}  # Stores program details (name, instance count, cores, memory)
            self.instances = {}  # Stores instance details (id, running, date_started)
            self.distributable_instances = []

            

        self.computers = {}
        self._load_computers()

        self._load_programs()

        self.rebalancer = Rebalancer(self)
        self.set_rebalance_algo(0)
        self.run_rebalance()
        self.cleanup()

        self.print(f"{Fore.BLACK}{Back.GREEN}Cluster ({self.name}) initialized succesfully with {len(self.computers)} computer(s) and {len(self.programs)} program(s).{Back.RESET+Fore.RESET}\n")
        self.initialized = True


    def _load_computers(self):
        """Update the computer references"""
        self.computers = {}
        files: list = os.listdir(self.path)

        if ".klaszter" in files:
            files.remove(".klaszter")

        for file in files:
            computer : Computer = Computer(Path.join(self.path, file), self)
            if computer.instialized: self.computers[file] = computer

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
        
        self.active_inst_num = 0
        self.inactive_inst_num = 0

        temp_resource_usage = {
            comp.name: {
                "free_cores": comp.cores,  
                "free_memory": comp.memory
            }
            for comp in self.computers.values()
        }

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
                if not self._validate_instance_placement(program_name, required_count, temp_resource_usage):
                    while True:
                        user_input = self.user_input(
                            f"{Fore.RED}Nincsen elég erőforrás {required_count} darabnyi '{program_name}' program példány futtatásához! {Fore.RESET}\n"
                            f"{Style.BRIGHT}Adjon meg egy kisebb mennyiség számot\n"
                            f"Vagy írja be a 0-át, hogy nullázza a darabszámot és átugorja a programot. >> {Style.RESET_ALL}").strip()
                        
                        if user_input.isdigit():
                            new_count = int(user_input)
                            if new_count == 0:
                                self.print(f"{Fore.WHITE}Did not distribute ({program_name}) Set instance count to 0.")
                                self.edit_program_resources(program_name, "required_count", 0, reload=False)
                                skip_program = True
                                break

                            if self._validate_instance_placement(program_name, new_count, temp_resource_usage):
                                required_count = new_count
                                break

                        self.print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a valid number.")

                if skip_program: continue

                # Find a computer that can fit the instances
                for c_name, resources in temp_resource_usage.items():
                    if resources["free_cores"] >= required_count * cores and resources["free_memory"] >= required_count * memory:
                        # Deduct resources
                        resources["free_cores"] -= required_count * cores
                        resources["free_memory"] -= required_count * memory
                        break  # Stop after updating one computer

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
                                            f"Nem fut elég '{program_name}' példány, minimum {required_count} darabnak kell! \n"
                                            f"{Fore.GREEN}Léteznek inaktív példányok({len(inactive_valid_instances)}).{Fore.WHITE + Style.BRIGHT} Szeretné őket elindítani?{Style.RESET_ALL}\n"
                                            f"1 - Igen\n"
                                            f"2 - Mégse >> ").strip()
                        if user_input == '1':
                            while (len(active_valid_instances) < required_count) and inactive_valid_instances: 
                                instance_to_activate = inactive_valid_instances.pop(0) # Get oldest inactive instance
                                active_valid_instances.append(instance_to_activate) # Activate and move to active list
                                
                                self.instances[program_name][instance_to_activate['id']]["status"] = True # Update tracking data
                            break

                        if user_input == '2':
                            break

                        self.print(f"{Fore.RED + Style.BRIGHT}Please input a valid choice!")

                # Generate new instances as needed
                new_needed = required_count - len(active_valid_instances)
                if new_needed > 0:
                    while True:
                        user_input = self.user_input(
                                            f"{Fore.YELLOW + Style.BRIGHT}Nem fut elég {Fore.RESET + Style.RESET_ALL} '{program_name}' példány, minimum {required_count} kell! \n"
                                            f"{Fore.WHITE + Style.BRIGHT} Szeretene {Fore.GREEN}újakat indítani?{Fore.RESET + Style.RESET_ALL}\n"
                                            f"1 - Igen\n"
                                            f"2 - Mégse >> ").strip()
                        if user_input == '1':
                            for _ in range(new_needed):
                                instance_id = self._generate_instance_id()
                                
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

                        self.print(f"{Fore.RED + Style.BRIGHT}Please input a valid choice!")


                # Handle excess instances
                extra_instances_count = len(active_valid_instances) - required_count
                if len(all_instances) > required_count:
                    self.print(f"{Back.BLUE + Fore.BLACK}More instances (Active({len(active_valid_instances)}), Incative({len(inactive_valid_instances)})) found on cluster than required ({required_count}).")

                if extra_instances_count > 0:
                    self.print(f"{Fore.YELLOW}Warning: extra active '{program_name}' instances found!")

                    extra_instances = []
                    for i in range(extra_instances_count):
                        extra_instances.append(active_valid_instances[-(i+1)])

                    while True:
                        user_input = self.user_input(
                            f"{Style.BRIGHT}Szeretné\n"
                            f"(1) Leállítani a példányokat\n"
                            f"(2) Vagy törölni a példányokat? (1/2) >> {Style.RESET_ALL}"
                        ).strip()
                        
                        if user_input == '1':
                            for instance in extra_instances:
                                # Only deactivate if currently active
                                if instance["status"]:
                                    active_valid_instances.remove(instance)
                                    inactive_valid_instances.append(instance)
                                    self.edit_instance_status(instance['id'], False, reload=False)
                            break

                        if user_input == '2':
                            for instance in extra_instances:
                                try:
                                    if instance["status"]:
                                        active_valid_instances.remove(instance)
                                        self.kill_instance(instance['id'], reload=False)
                                except Exception as e:
                                    self.print(f"{Fore.RED}Failed to delete {f"{program_name}-{instance_id}"}: {str(e)}")
                            break

                        self.print(f"{Fore.RED + Style.BRIGHT}Please input a valid choice!")
                
                self.active_inst_num += len(active_valid_instances)
                self.inactive_inst_num += len(inactive_valid_instances)

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
                self.update_instance_cores_memory(
                    computer,
                    f"{program_name}-{instance['id']}",
                    "cores",
                    req_cores
                )
                needs_update = True
                
            if instance["memory"] != req_mem:
                self.update_instance_cores_memory(
                    computer,
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

    def update_instance_cores_memory(self, computer,instance_id: str, property_name: str, new_value: str) -> bool:
        """Makes sure that all instances have the same requirements as described in the cluster config file."""

        instance_path = Path.join(computer.path, instance_id)
        
        if not self.is_prog_instance_file(instance_path):
            return False

        # Validate property
        valid_props = ["cores", "memory"]
        if property_name not in valid_props:
            self.print(f"{Fore.RED}Invalid property: {property_name}")
            return False
        
        new_value = int(new_value)

        # Perform edit
        try:
            with open(instance_path, "r+", encoding="utf8") as f:
                lines = [line.strip() for line in f.readlines()]
                
                # Map properties to line numbers
                property_map = {
                    "cores": 2,
                    "memory": 3
                }
                
                # Update the value
                line_idx = property_map[property_name]
                lines[line_idx] = str(new_value)
                
                # Write back changes
                f.seek(0)
                f.truncate()
                f.write("\n".join(lines))
        
        except Exception as e:
            self.print(f"Failed to update instance {instance_id}: {str(e)}")
            return False

        return True


    def _validate_instance_placement(self, program_name, required_count, temp_resource_usage=None):
        """
        Check if we can fit all instances, using either a simulated state (`temp_resource_usage`) 
        or real-time resource availability.
        """

        # Get program requirements
        req_cores = int(self.programs[program_name]["cores"])
        req_memory = int(self.programs[program_name]["memory"])

        # Use `temp_resource_usage` if provided, else use real-time values
        if temp_resource_usage:
            total_free_cores  = 0# = sum(comp["free_cores"] for comp in temp_resource_usage.values())
            for comp in temp_resource_usage.values():
                total_free_cores += comp["free_cores"]

            total_free_memory = sum(comp["free_memory"] for comp in temp_resource_usage.values())

            # Sort by available resources
            sorted_computers = sorted(temp_resource_usage.values(), key=lambda c: (-c["free_cores"], -c["free_memory"]))
        else:
            total_free_cores = sum(comp.free_cores for comp in self.computers.values())
            total_free_memory = sum(comp.free_memory for comp in self.computers.values())

            # Sort computers normally
            sorted_computers = sorted(self.computers.values(), key=lambda c: (-c.free_cores, -c.free_memory))

        # Quick Check: If total cluster resources aren't enough, fail immediately
        if required_count * req_cores > total_free_cores or required_count * req_memory > total_free_memory:
            return False

        # Try placing instances using Best-Fit Decreasing
        remaining_instances = required_count
        for computer in sorted_computers:
            if temp_resource_usage:
                free_cores = computer["free_cores"]
                free_memory = computer["free_memory"]
            else:
                computer.calculate_resource_usage()
                free_cores = computer.free_cores
                free_memory = computer.free_memory

            # Max instances this computer can fit
            max_fit = min(free_cores // req_cores, free_memory // req_memory)

            # Assign as many as possible without exceeding required_count
            to_place = min(max_fit, remaining_instances)
            remaining_instances -= to_place

            # If we placed all instances, we're done!
            if remaining_instances == 0:
                return True

        return required_count == 0  # If required_count is 0, it's always valid




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
                            f"{Style.BRIGHT} Szeretné {program_name}-{instance_id} program példánnyal csinálni:\n"
                            f"1) Manuálisan átnevezni (\n"
                            f"2) Automatikusan új azonosítóval ellátni\n"
                            f"Válasz (1/2) >> "
                        ).strip()

                        if user_choice == "1":
                            new_id = self.user_input("Adjon meg 6 karaktert: ").strip()
                            if len(new_id) == 6 and new_id.isalnum() and new_id not in seen_ids:
                                new_instance_id = new_id  # Just store the new ID, program name is already mapped
                                self.change_instance_id(instance_id, new_instance_id, program_name, False)

                                seen_ids[new_id] = program_name  # Update tracking
                                break
                            else:
                                self.print(f"{Fore.RED + Style.BRIGHT}Invalid ID. Ensure it is 6 alphanumeric characters and unique.")
                        
                        elif user_choice == "2":                            
                            _, instance = self.get_instance_by_id(instance_id)
                            self.change_instance_id(instance_id, "",program_name, False)

                            seen_ids[instance["id"]] = program_name  # Update tracking
                            break

                        self.print(f"{Fore.RED + Style.BRIGHT}Please input a valid choice! Please enter 1 or 2")


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
                    f"{Style.BRIGHT}Szeretné:\n"
                    f"1) Manuálisan átnevezni ({duplicate})\n"
                    f"2) Ignorálni\n"
                    f"Válasz (1/2): "
                ).strip()

                if user_input == "1":
                    new_name = self.user_input("Adjon meg egy új egyéni nevet: ").strip()
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
        self.run_rebalance()

        self.print(f"{Back.BLUE + Fore.WHITE}Successfully reloaded cluster")


# Rebalancer
    def set_rebalance_algo(self, new_algo_id: int = 0):
        self.rebalancer.default_rebalance_algo = rebalancing_algos[new_algo_id]

    def run_rebalance(self):
        self.rebalancer.run_default_rebalance_algo()


# Computers
    def create_computer(self, computer_name: str, cores: int, memory: int) -> Computer:
        full_path: str = Path.join(self.path, computer_name)

        if Path.exists(full_path):
            self.print(f"{Fore.RED}Computer ({computer_name}) already exists and will NOT be created.")
            return self.computers[computer_name]
        
        if cores < 0 or memory < 0:
            self.print(f"{Fore.RED}Can not start computer with negative resoruces")
            return False
        
        try:
            os.mkdir(full_path)
            with open(Path.join(full_path, ".szamitogep_config"), "w", encoding="utf8") as config_file:
                config_file.write(f"{cores}\n{memory}")

            self.print(f"{Fore.GREEN}Computer ({computer_name}) created successfully.")
            
            self._load_computers()
            return self.computers.get(computer_name)
        except:
            self.print(f"{Fore.RED}Error while creating computer '{computer_name}'.")
            return False

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
    def add_program(self, program_name: str, instance_count : int, cores: int, memory: int, reload : bool = True):
        """Adds programs to the cluster config file and reloads the cluster."""

        if program_name in self.programs:
            self.print(f"{Fore.RED}There is alrady a program named {program_name}")
            return False
        if int(instance_count) < 0 or int(cores) < 0 or int(memory) < 0:
            self.print(f"{Fore.RED}Can not add program with negative resoruces!")
            return False
        
        data = f"{program_name}\n{instance_count}\n{cores}\n{memory}\n"

        self.programs[program_name] = {"instance_count" : instance_count, "cores": cores, "memory" : memory}
        if not self._validate_instance_placement(program_name, int(instance_count)):
            self.print(f"{Fore.RED}Could not create program due to innsufficient resources.")
            del self.programs[program_name]
            return False

        cluster_config_path = Path.join(self.path, ".klaszter")
        with open(cluster_config_path, "a", encoding="utf8") as config_file:
            config_file.write(data)

        if reload:
            self._load_programs()
            self.run_rebalance()
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

        self.print(f"{Fore.GREEN}Program {program_name} killed successfully!")

        self._load_programs()
        return True

    def stop_program(self, program_name : str, reload : bool = True):
        """Deactivates all instances of a program and sets instance count to 0"""
        if program_name not in self.programs:
            self.print(f"{Fore.RED}There is no program named {program_name} in the cluster. Check name and try again!")
            return False
        
        instances_to_stop = []
        if self.instances.get(program_name):
            for instance_id in self.instances.get(program_name):
                instances_to_stop.append(instance_id)

        for instance_id in instances_to_stop:
            self.edit_instance_status(instance_id, False, reload=False)
        
        self.programs[program_name]["required_count"] = 0
        
        data = ""
        with open(self.config_path, "w+", encoding="utf8") as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]

            for prog_name, details in self.programs.items():
                data += f"{prog_name}\n{details["required_count"]}\n{details["cores"]}\n{details["memory"]}\n"
            
            print(data)

            file.write("")
            file.write(data)

        if reload:
            self._load_programs()
            self.run_rebalance()

        self.print(f"{Fore.GREEN}Program {program_name} stopped successfully!")

        return True

    def edit_program_resources(self, program_name: str, property_to_edit: str, new_value, reload : bool = True):
        """Can edit the instance count, the cores and the memory required"""

        if program_name not in self.programs:
            self.print(f"{Fore.RED}Program {program_name} does not exist! Check the name and try again.")
            return False
        
        allowed_properties = ["required_count", "cores", "memory"]
            
        if property_to_edit not in allowed_properties:
            self.print(f"{Fore.RED}Invalid property. Allowed: {allowed_properties}")
            return False
        
        # Convert new_value to correct type
        new_value = int(new_value)

        if new_value < 0:
            self.print(f"{Fore.RED}Can not change the program's resources to negative values!")
            return False
        
        # Check if we can fit it on the cluster
        old_value = self.programs[program_name][property_to_edit]
        
        if new_value == old_value:
            return True
        
        self.programs[program_name][property_to_edit] = new_value

        if not self._validate_instance_placement(program_name, self.programs[program_name]["required_count"]) and not (property_to_edit == "required_count" and new_value == 0):
            self.programs[program_name][property_to_edit] = old_value
            self.print(f"{Fore.RED}The edited program would not fit on the cluster. Abendonding editing process.")
            return False
        
        data = f""
        with open(self.config_path, "w+", encoding="utf8") as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]

            for prog_name, details in self.programs.items():
                data += f"{prog_name}\n{details["required_count"]}\n{details["cores"]}\n{details["memory"]}\n"
            
            file.write("")
            file.write(data)
        
        if reload:
            self._load_programs()
            self.run_rebalance()
        return True
        
    def rename_program(self, program_name : str, new_program_name: str, reload : bool = True):
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

        if reload:
            self._load_programs()
            self.run_rebalance()
        return True


#Instances
    def add_instance(self, program_name : str, instance_id : str = ""):
        """Adds new instance either by user created id or self generated id"""
        if program_name not in self.programs:
            return False
        
        if not instance_id:
            instance_id = self._generate_instance_id()
        
        if self.is_instance_on_cluster_by_id(instance_id):
            return False
        
        parent_program = self.programs[program_name]
        new_instance = {'status': True, 'cores': parent_program['cores'], 'memory': parent_program['memory'], 'computer': None, 'date_started': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'id': instance_id}
        
        while True:
            user_input = self.user_input(
                f"{Style.BRIGHT}Fusson ez a porgram példány?\n"
                "1 - Igen\n"
                "2 - Nem\n"
                "3 - Kilépés >> ").strip()
            
            if user_input == "1":
                if self._validate_instance_placement(program_name, parent_program["required_count"] + 1):
                    self.edit_program_resources(program_name, "required_count", parent_program["required_count"] + 1, reload=False)
                    break
                self.print(f"{Fore.RED + Style.BRIGHT}Can`t add new instance. There isn`t enough space on the cluster. Try adding it as inactive")

            elif user_input =="2":
                new_instance["status"] == False
                break

            elif user_input =="3":
                return False
            
            self.print(f"{Fore.RED + Style.BRIGHT}Please enter a valid choice!")

        self.instances[program_name][instance_id] = new_instance

        self._load_programs()
        self.run_rebalance()
        return True

    def edit_instance_status(self, instance_id: str, new_status: bool, reload : bool = True) -> bool:
        """Edit instance status to true or false"""
        
        if not self.is_instance_on_cluster_by_id(instance_id): 
            self.print(f"{Fore.RED}Instance {instance_id} not found in cluster!")
            return False

        target_program, instance_to_stop = self.get_instance_by_id(instance_id)

        if not instance_to_stop:
            self.print(f"{Fore.RED}Could not find instance to stop.")
            return False
        
        self.instances[target_program][instance_id]["status"] = new_status
        
        full_name = f"{target_program}-{instance_id}"
        self.print(f"{Fore.GREEN}Instance {full_name} stopped successfully.")

        if reload:
            self._load_programs()
            self.run_rebalance()
        return True

    def kill_instance(self, instance_id : str, reload : bool = True):
        """Kills an instance and removes references, can be used for batch removal is reload is turned off."""

        if not self.is_instance_on_cluster_by_id(instance_id): 
            self.print(f"{Fore.RED}Instance ({instance_id}) not found on cluster")
            return False

        target_program, instance_to_kill = self.get_instance_by_id(instance_id)

        if not instance_to_kill:
            self.print(f"{Fore.RED}Could not find instance to kill.")
            return False
        
        target_computer = ""
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
            self.run_rebalance()
        return True

    def change_instance_id(self, instance_id : str, new_instance_id : str = "", program_name : str = "", reload : bool = True) -> bool:
        """Changes the instance id of a given instance. To change the instance in the filesystem reload needs to be called in the cycle. You may enter program name for a specific instance."""
        if not self.is_instance_on_cluster_by_id(instance_id): return False

        target_program, instnace_to_change = self.get_instance_by_id(instance_id)
        
        if not instnace_to_change:
            self.print(f"{Fore.RED}Could not find instance to change.")
            return False
        
        if program_name:
            target_program = program_name

        existing_ids = []

        for program_instances in self.instances.values():
            for key in program_instances.keys():
                existing_ids.append(key)

        if new_instance_id == "":
            new_instance_id = self._generate_instance_id()
            self.instances[target_program][new_instance_id] = self.instances[target_program].pop(instance_id)

        elif len(new_instance_id) == 6 and new_instance_id.isalnum() and new_instance_id not in existing_ids:        
            self.instances[target_program][new_instance_id] = self.instances[target_program].pop(instance_id)

        else:
            self.print(f"{Style.BRIGHT + Fore.RED}Invalid ID. Ensure it is 6 alphanumeric characters and unique.")
            return False
        
        if reload:
            self._update_distributable_instances()
            self.run_rebalance()
        return True
        

#UTILS
    def cleanup(self):
        """Removes unnescecary files and directories from the cluster""" 
        files: list = os.listdir(self.path)

        for computer in self.computers:
            files.remove(computer)

        files.remove(".klaszter")

        self.print(f"{Fore.GREEN}Starting cleanup...")

        removed_files : int = 0
        try:
            for file in files:
                target_path = Path.join(self.path, file)

                while True:
                    user_input = self.user_input(
                        f"Azonosítatlan fájl {self.name}: {file}\n"
                        "1: Törlés\n"
                        "2: Megtartás (Figyelmeztetés: destabilizálhatja a klasztert)\n"
                        "Válasz (1/2) >> "
                    ).strip()

                    if user_input == "1":
                        try:
                            if Path.isfile(target_path):
                                self.print(f"Removing file ({file}).")
                                os.remove(target_path)
                            else:
                                self.print(f"Removing folder ({file}).")
                                shutil.rmtree(target_path)
                            removed_files += 1

                        except Exception as e:
                            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR: Cannot delete ({file}). {e}")
                        break

                    elif user_input == "2":
                        self.print(f"Skipping file ({file}).")
                        break  # Exit the while loop after action

                    else:
                        self.print("Invalid input. Please enter 1 or 2.")

                self.print(f"{Fore.YELLOW}Removed {file} from filesystem.")
                
        except:
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: can't delete file or folder ({file}). Cluster might be unstable.")
            return False
        

        self.print(f"{Fore.GREEN}Cleanup completed. Removed a total of {removed_files} incorrect files plus folders.")
        return True

    def get_active_inactive_instances(self) -> tuple:
        """Gives back a tuple with the current active and inactive instances in dictionaries."""
        active_dict = {}
        inactive_dict = {}
        
        for prog_name, instances in self.instances.items():
            for instance_id, instance in instances.items():
                if instance["status"] == True:
                    active_dict[instance_id] = instance
                elif instance["satutus"] == True:
                    inactive_dict[instance_id] = instance
        
        return (active_dict, inactive_dict)

    def is_prog_instance_file(self, path: str) -> bool:
        """Runs a check to see wether the file under the given path is an instance or not using a pattern."""
        filename = Path.basename(path)
        
        # Check filename format: programname-id (id must be 6 chars)
        if not re.match(Path.join(r"^[a-zA-Z0-9]+-[a-zA-Z0-9]{6}$"), filename):
            return False
        
        # Check file contents structure
        try:
            with open(path, "r", encoding="utf8") as file:
                lines = [line.strip() for line in file.readlines()]
            
            return (len(lines) == 4 and
                    re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", lines[0]) and
                    lines[1] in {"AKTÍV", "INAKTÍV"} and
                    lines[2].isdigit() and 
                    lines[3].isdigit())
        except:
            return False

    def get_instance_by_id(self, id : str) -> tuple:
        """Returns a tuple with the program of the instance being the first value and the instance the second"""
        for program in self.instances:
            target_program = program
            program : dict = self.instances[program]

            for instance in program:
                if instance == id:
                    return (target_program, program[id])

    def is_instance_on_cluster_by_id(self, id : str) -> bool:
        instance_exists = False
        for _, programs in self.instances.items():
            for instance_id in programs:
                if instance_id == id: instance_exists = True
        if not instance_exists : return False
        return True

    def user_input(self, input_question : str) -> str:
        """Splits input so we can use input from the ui."""
        
        if self.root.ui == None:
            user_input = input(input_question)
            return user_input
        else:
            question : str = input_question.splitlines()
            from modules.subwindow import SubWindow
            from modules.ui import UI

            popout : SubWindow = SubWindow()
            popout.geometry("600x300")
            popout.close_button.grid_forget()

            popout.content.grid_columnconfigure(0, weight=1)

            question_frame : UI.Frame = UI.Frame(popout.content)
            question_frame.grid(row=0, column=0, sticky="new")
            question_frame.grid_columnconfigure(0, weight=1)

            for i, line in enumerate(question):
                line = re.sub(r"\033\[[0-9;]*m", "", line)
                line = line.replace(">>", "")
        
                UI.Label(question_frame, text=line, justify="left").grid(row=i, column=0)

            answer : UI.Entry =  UI.Entry(popout.content)
            answer.grid(row=1, column=0, pady=10)

            def set_can_continue(event=None):
                nonlocal can_continue
                can_continue = True

            can_continue  : bool = False
            popout.bind("<Return>", set_can_continue)

            while not can_continue:
                popout.update_idletasks()
                popout.update()

            answer = answer.get()
            popout.destroy()
            return answer

    def print(self, text: str):
        """Debugging print method."""
        print(f"{Fore.BLACK}{Back.CYAN}[{Back.WHITE}{self.name}{Back.CYAN}]{Back.RESET}{Fore.CYAN}: {text}{Style.RESET_ALL}")

    def signiture(self):
        print(f"{Fore.BLUE}undefined")