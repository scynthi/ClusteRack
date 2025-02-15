import shutil
import os
from os import path as Path
from datetime import datetime
from colorama import Fore, Style, Back

class Computer:
    def __init__(self, path: str):
        path: str = Path.normpath(fr"{path}")
        computer_name: str = path.split(os.sep)[-1]
        self.name: str = computer_name

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
            self.cleanup()
            usage: dict = self.calculate_resource_usage()

            if usage["memory_usage_percent"] > 100:
                self.print(f"{Fore.RED}Computer ({self.name}) is overloaded! Memory limit exceeded ({usage["memory_usage_percent"]}%).")
                return False
            
            if usage["core_usage_percent"] > 100:
                self.print(f"{Fore.RED}Computer ({self.name}) is overloaded! Core limit exceeded ({usage["core_usage_percent"]}%).")
                return False
            
            return True


    def calculate_resource_usage(self) -> dict:
        processes: dict = self.get_processes()

        memory_usage: int = 0
        cpu_usage: int = 0

        for _, info in processes.items():
            if info["status"]:
                memory_usage += int(info["memory"])
                cpu_usage += int(info["cores"])

        self.free_memory: int = self.memory - memory_usage
        self.free_cores: int = self.cores - cpu_usage

        memory_usage_percentage: float = round(memory_usage / self.memory * 100, 1)
        cpu_usage_percentage: float = round(cpu_usage / self.cores * 100, 1)

        return {"memory_usage_percent": memory_usage_percentage, "core_usage_percent": cpu_usage_percentage}


    def get_processes(self) -> dict:
        """Gives back all the running processes on the computer"""
        files: list = os.listdir(self.path)
        process_list: dict = {}

        if ".szamitogep_config" in files:
            files.remove(".szamitogep_config")

        for process in files:
            try:
                process_list[process] = self.get_process_info(process)
            except:
                self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: process ({process}) is incorrect.")

        return process_list


    def get_process_info(self, process: str) -> dict:
        """Gives back the info of one specific running process on the computer"""
        if Path.exists(Path.join(self.path, process)):
            process_info: list = process.split("-")

            file = open(Path.join(self.path, process), "r", encoding="utf8")
            process_file_info: list = file.readlines()
            file.close()
            
            for line in process_file_info:
                process_file_info[process_file_info.index(line)] = line.strip()

            
            status: bool = False
            if str(process_file_info[1]).upper() == "AKTÍV":
                status = True
            elif str(process_file_info[1]).upper() == "":
                self.edit_process_status(process, False)

            return {"name":str(process_info[0]), "id":str(process_info[1]), "status": status, "cores": int(process_file_info[2]), "memory": int(process_file_info[3]), "date_started": str(process_file_info[0])}


#MISC.
    def cleanup(self) -> bool:
        """Removes unnescecary files and directories from the computer""" 
        files: list = os.listdir(self.path)
        
        self.print(f"{Fore.GREEN}Starting cleanup...")

        if Path.exists(Path.join(self.path, ".szamitogep_config")):
            files.remove(".szamitogep_config")

        removed_files : int = 0

        for file in files:
            try:
                self.get_process_info(file)
            except:
                try:
                    target_path = Path.join(self.path, file)

                    if Path.isfile(target_path):
                        self.print(f"Removing file ({file}).")
                        os.remove(Path.join(self.path, file))
                        removed_files += 1
                    else:
                        self.print(f"Removing folder ({file}).")
                        shutil.rmtree(target_path)
                        removed_files += 1
                except:
                    self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: can't delete file or folder ({file}). Computer might be unstable.")
                    return False
        
        self.print(f"{Fore.GREEN}Cleanup completed. Removed a total of {removed_files} incorrect files plus folders.")
        return True
    
    
    def print(self, text: str):
        """DEBUGGING TOOL: A print for the terminal"""
        print(f"{Style.BRIGHT}{Fore.CYAN}[{Fore.WHITE}{self.name}{Fore.CYAN}]: {Fore.RESET+Back.RESET+Style.RESET_ALL}" + text + Fore.RESET+Back.RESET+Style.RESET_ALL)