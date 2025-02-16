import shutil
import os
from os import path as Path
from colorama import Fore, Style, Back

class Computer:
    def __init__(self, path: str, parent):
        path: str = Path.normpath(fr"{path}")
        computer_name: str = path.split(os.sep)[-1]
        self.name: str = computer_name
        self.cluster = parent

        if Path.exists(Path.join(path, ".szamitogep_config")):
            config_file = open(Path.join(path, ".szamitogep_config"), "r", encoding="utf8")
            config: list = config_file.readlines()
            config_file.close()

            if len(config) != 2:
                self.print(f"{Fore.RED}Invalid configuration file at path: {path}")
                return
            
            cores: int = int(config[0])
            memory: int = int(config[1])

            self.cores: int = cores
            self.memory: int = memory
            
            self.path: str = path

            if not self.validate_computer(): return
            self.cleanup()
            self.print(f"{Back.GREEN}{Fore.BLACK}Computer ({computer_name}) initialized with {cores} cores and {memory} of memory. {self.free_cores} cores and {self.free_memory} memory left free.{Back.RESET}\n\n")

        else:
            self.print(f"{Fore.RED}There's no config file in {path}")
            return


    def validate_computer(self) -> bool:
        usage: dict = self.calculate_resource_usage()

        if usage["memory_usage_percent"] > 100:
            self.print(f"{Fore.RED}Computer ({self.name}) is overloaded! Memory limit exceeded ({usage["memory_usage_percent"]}%).")
            return False
        
        if usage["core_usage_percent"] > 100:
            self.print(f"{Fore.RED}Computer ({self.name}) is overloaded! Core limit exceeded ({usage["core_usage_percent"]}%).")
            return False
        
        return True

    def calculate_resource_usage(self) -> dict:
        prog_instances: dict = self.get_prog_instances()

        memory_usage: int = 0
        cpu_usage: int = 0

        for _, info in prog_instances.items():
            if info["status"]:
                memory_usage += int(info["memory"])
                cpu_usage += int(info["cores"])

        self.free_memory: int = self.memory - memory_usage
        self.free_cores: int = self.cores - cpu_usage

        memory_usage_percentage: float = round(memory_usage / self.memory * 100, 1)
        cpu_usage_percentage: float = round(cpu_usage / self.cores * 100, 1)

        return {"memory_usage_percent": memory_usage_percentage, "core_usage_percent": cpu_usage_percentage}
    
    def get_prog_instances(self) -> dict:
        """Return only valid instances"""
        files = os.listdir(self.path)
        valid_instances = {}
        
        for f in files:
            full_path = Path.join(self.path, f)
            if self.cluster.is_prog_instance_file(full_path):
                details = self.get_prog_instance_info(f)
                if details:
                    valid_instances[f] = details
        return valid_instances

    def get_prog_instance_info(self, filename: str) -> dict:
        """Returns None instead of erroring on invalid instances"""
        try:
            if not self.cluster.is_prog_instance_file(Path.join(self.path, filename)):
                return None
                
            name_part, instance_id = filename.split("-")
            with open(Path.join(self.path, filename), "r", encoding="utf8") as f:
                lines = [line.strip() for line in f.readlines()]
                
            status = True if lines[1] == "AKTÍV" else False

            return {
                "name": name_part,
                "id": instance_id,
                "status": status,
                "cores": int(lines[2]),
                "memory": int(lines[3]),
                "date_started": lines[0]
            }
        except:
            return None

    def remove_instance(self, instance_id: str) -> bool:
        """Removes an instance file from the computer."""
        instance_path = Path.join(self.path, instance_id)
        
        if not Path.exists(instance_path):
            self.print(f"{Fore.YELLOW}Instance {instance_id} not found on this computer.")
            return False

        try:
            os.remove(instance_path)
            self.calculate_resource_usage()
            return True
        except Exception as e:
            self.print(f"{Fore.RED}Failed to remove instance {instance_id}: {str(e)}")
            return False


#Utils
    def can_fit_instance(self, instance: dict) -> bool:
        """Checks if the computer has enough free resources for an instance."""
        return (
            self.free_cores >= instance["cores"] and
            self.free_memory >= instance["memory"]
        )

    def cleanup(self) -> bool:
        """Removes unnecessary files and directories from the computer"""
        
        files: list = os.listdir(self.path)
        removed_files: int = 0

        self.print(f"{Fore.GREEN}Starting cleanup...")

        if Path.exists(Path.join(self.path, ".szamitogep_config")):
            files.remove(".szamitogep_config")

        for file in files:
            target_path = Path.join(self.path, file)

            if self.cluster.is_prog_instance_file(target_path):
                continue

            while True:
                try:
                    user_input = self.user_input(
                        f"Unidentified file detected in {self.name}: {file}\n"
                        "1: Delete\n"
                        "2: Keep (Warning: Might make the computer unstable)\n"
                        "Enter your choice (1/2): "
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
                        break  # Exit the while loop after action
                    elif user_input == "2":
                        self.print(f"Skipping file ({file}).")
                        break  # Exit the while loop after action
                    else:
                        self.print("Invalid input. Please enter 1 or 2.")

                except KeyboardInterrupt:
                    self.print(f"\n{Fore.RED}Cleanup interrupted by user.{Fore.RESET}")
                    return False

        self.print(f"{Fore.GREEN}Cleanup completed. Removed {removed_files} files/folders.")
        return True
   
    def user_input(self, input_question : str) -> str:
        if self.cluster.root.ui == None:
            user_input = input(input_question)
            return user_input
        else:
            pass

    def print(self, text: str):
        """DEBUGGING TOOL: A print for the terminal"""
        print(f"{Style.BRIGHT}{Fore.CYAN}[{Fore.WHITE}{self.name}{Fore.CYAN}]: {Fore.RESET+Back.RESET+Style.RESET_ALL}" + text + Fore.RESET+Back.RESET+Style.RESET_ALL)