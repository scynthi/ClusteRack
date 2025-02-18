import shutil
import os
from os import path as Path
from colorama import Fore, Style, Back
import re

class Computer:
    def __init__(self, path: str, parent):
        if not hasattr(self, "initialized"):
            self.instialized = False
        
        path: str = Path.normpath(fr"{path}")
        self.path = path
        
        computer_name: str = path.split(os.sep)[-1]
        self.name: str = computer_name
        
        self.cluster = parent
        
        self.cores: int = 0
        self.memory: int = 0
        
        if self._load_config():
            
            self.cleanup()
            self.print(f"{Back.GREEN}{Fore.BLACK}Computer ({computer_name}) initialized with {self.cores} cores and {self.memory} of memory. {self.free_cores} cores and {self.free_memory} memory left free.{Back.RESET}\n\n")
            self.instialized = True
        else:
            return


    def _load_config(self) -> bool:
        """Loads computer attributes if there is a config file. Creates config file by user input if there is no config file."""
        if Path.exists(Path.join(self.path, ".szamitogep_config")):
            config_file = open(Path.join(self.path, ".szamitogep_config"), "r", encoding="utf8")
            config: list = config_file.readlines()
            config_file.close()

            if len(config) != 2:
                self.print(f"{Fore.RED}Invalid configuration file at path: {self.path}")
                return False
            
            cores: int = int(config[0])
            memory: int = int(config[1])

            self.cores: int = cores
            self.memory: int = memory
            if not self.validate_computer(): return False
            return True
            
        else:
            self.print(f"{Fore.RED}There's no config file in {self.path}")
            try:
                while True:
                    user_input = self.user_input(
                        f"Nincs konfigurációs file a {self.path}\n"
                        f"{Fore.WHITE + Style.BRIGHT}Szeretne generálni egyet?\n"
                        f"1 - Igen\n"
                        f"2 - Nem >> ").strip()
                    
                    if user_input == "1":
                        new_cores = 0
                        new_memory = 0
                        while True:
                            new_cores = self.user_input("Adja meg a magok számát(Millimag) >> ")
                            if new_cores.isdigit() and int(new_cores) > 0: break
                            self.print(f"{Fore.RED}Please enter a valid positive number.")
                        while True:
                            new_memory = self.user_input("Adja meg a memóriát(Megabyte) >> ")
                            if new_memory.isdigit() and int(new_memory) > 0: break
                            
                            self.print(f"{Fore.RED}Please enter a valid positive number.")

                        with open(Path.join(self.path, ".szamitogep_config"), "w", encoding="utf8") as config_file:
                            config_file.write(f"{new_cores}\n{new_memory}")
                        
                        self.cluster.computers[self.name] = self
                        self._load_config()
                        return True

                    elif user_input == "2":
                        return False
                    
                    self.print(f"{Fore.RED}Choose a valid option.")

            except Exception as e:
                self.print(f"{Fore.RED}Computer config creation abendoned because of: {e}")
            return False
            

    def validate_computer(self) -> bool:
        """Checks wether the usage is overstepping the computer's resources."""
        
        usage: dict = self.calculate_resource_usage()

        if usage["memory_usage_percent"] > 100:
            self.print(f"{Fore.RED}Computer ({self.name}) is overloaded! Memory limit exceeded ({usage["memory_usage_percent"]}%).")
            return False
        
        if usage["core_usage_percent"] > 100:
            self.print(f"{Fore.RED}Computer ({self.name}) is overloaded! Core limit exceeded ({usage["core_usage_percent"]}%).")
            return False
        
        return True

    def calculate_resource_usage(self) -> dict:
        """Calculates resource usage based on child instances of the computer."""
        
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
                        f"Ismeretlen fájl a {self.name}: {file} - ban\n"
                        "1: Törlés\n"
                        "2: Megtartás (Figyelmeztetés: Lehetséges hogy destabilizálja a számítógépet)\n"
                        "Irja be választását(1/2): "
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

            while True:
                popout.update()
                if len(answer.get()) == 1:
                    answer : str = answer.get()
                    popout.destroy()
                    return answer

    def print(self, text: str):
        """DEBUGGING TOOL: A print for the terminal"""
        print(f"{Style.BRIGHT}{Fore.CYAN}[{Fore.WHITE}{self.name}{Fore.CYAN}]: {Fore.RESET+Back.RESET+Style.RESET_ALL}" + text + Fore.RESET+Back.RESET+Style.RESET_ALL)