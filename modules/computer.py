import os
from os import path as Path
from datetime import datetime
from colorama import Fore, Style, Back

class Computer:
    def __init__(self, path: str) -> None:
        path: str = Path.normpath(fr"{path}")
        computer_name: str = path.split(os.sep)[-1]
        self.name: str = computer_name

        if Path.exists(Path.join(path, ".szamitogep_config")):
            config_file = open(Path.join(path, ".szamitogep_config"), "r", encoding="utf8")
            config: list = config_file.readlines()
            config_file.close()

            if len(config) != 2:
                self.print(f"{Fore.RED}Invalid configuration file at path: {path}")
                return False
            
            cores: int = int(config[0])
            memory: int = int(config[1])

            self.cores: int = cores
            self.memory: int = memory
            
            self.path: str = path

            if not self.validate_computer(): return
            self.print(f"{Back.GREEN}{Fore.BLACK}Computer ({computer_name}) initialized with {cores} cores and {memory} of memory. {self.free_cores} cores and {self.free_memory} memory left free.{Back.RESET}\n\n")
        else:
            self.print(f"{Fore.RED}There's no config file in {path}")


    def validate_computer(self) -> bool:
            self.cleanup()
            usage: dict = self.calculate_resource_usage()

            if usage["memory_usage_percent"] > 100:
                self.print(f"{Fore.RED}Computer ({self.name}) is overloaded! Memory limit exceeded ({usage["memory_usage_percent"]}%).")
                return False
            
            if usage["core_usage_percent"] > 100:
                self.print(f"{Fore.RED}Computer ({self.name}) is overloaded! Core limit exceeded ({usage["cpu_usage_percent"]}%).")
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


    def start_process_with_dict(self, process_info: dict) -> bool:
        name: str = process_info["name"]
        id: str = process_info["id"]
        status: bool = process_info["status"]
        cpu_req: int = process_info["cores"]
        ram_req: int = process_info["memory"]
        date_started : str = process_info["date_started"]

        return self.start_process(name+"-"+id, status, cpu_req, ram_req, date_started)


    def start_process(self, process_name: str, running: bool, cpu_req: int, ram_req: int, date_started : str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')) -> bool:
        if not "-" in process_name:
            self.print(f"{Fore.RED}{process_name} does not have a ID. Put a ID in the program name and try again.")
            return False
            
        if not process_name.split("-")[1]:
            self.print(f"{Fore.RED}{process_name} does not have a ID. Put a ID in the program name and try again.")
            return False
        
        if not len(process_name.split("-")[1]) == 6:
            self.print(f"{Fore.RED}{process_name}'s ID is not 6 characters long. Put a ID in the program name and try again.")
            return False


        if Path.exists(Path.join(self.path, process_name)):
            self.print(f"{Fore.RED}{process_name} is already running on computer ({self.name})")
            return False
        
        try:
            if self.free_cores - cpu_req < 0:
                self.print(f"{Fore.RED}Error while creating process on computer ({self.name}): "+process_name+" -> Core limit exceeded.")
                return False
            
            if self.free_memory - ram_req < 0:
                self.print(f"{Fore.RED}Error while creating process on computer ({self.name}): "+process_name+" -> Memory limit exceeded.")
                return False


            status : str = "INAKTÍV"
            if running:
                status = "AKTÍV"
            
            data: str = f"{date_started}\n{status}\n{cpu_req}\n{ram_req}"

            file = open(Path.join(self.path, process_name), "w", encoding="utf8")
            file.write(data)
            file.close()

            self.calculate_resource_usage()
            self.print(f"{Fore.GREEN}Process ({process_name}) started successfully on computer ({self.name}).")
            return True
        except:
            self.print(f"{Fore.RED}Error while creating process: {process_name}")
            return False


    def kill_process(self, process: str) -> bool:
        try:
            if Path.exists(Path.join(self.path, process)):
                os.remove(Path.join(self.path, process))
                self.calculate_resource_usage()
                return True
            
            self.print(f"{Fore.RED}Error while killing process: {process} does not exists! Perhaps you misspelled the name?")
            return False
        except:
            self.print(f"{Fore.RED}Error while killing process: {process}")
            return False


    def edit_process_status(self, process_name: str, running : bool) -> bool:
        if not Path.exists(Path.join(self.path, process_name)):
            self.print(f"P{Fore.RED}rocess ({process_name}) was not found on computer ({self.name})")
            return False
        
        try:
            process_info : dict = self.get_process_info(process_name)
            
            process_info["status"] = running
            status : str = "INAKTÍV"
            if running:
                status = "AKTÍV"

            file = open(Path.join(self.path, process_name), "w", encoding="utf8")
            data: str = f"{process_info["date_started"]}\n{status}\n{process_info["cores"]}\n{process_info["memory"]}"
            file.write(data)
            file.close()

            self.print(f"{Fore.GREEN}Process ({process_name})'s status has been set to: {running}")
            return True
        except:
            self.print(f"{Fore.RED}Error while editing process ({process_name})'s status.")
            return False


    def edit_resources(self, cores: int, memory: int) -> bool:
        min_cores: int = self.cores-self.free_cores
        min_memory: int = self.memory-self.free_memory

        if cores < min_cores:
            self.print(f"{Fore.RED}Can't set core count to {cores} on computer ({self.name}). Required minimum cores: {min_cores} ")
            return False
        
        if memory < min_memory:
            self.print(f"{Fore.RED}Can't set memory size to {memory} on computer ({self.name}). Required minimum memory size: {min_memory} ")
            return False

        prev_cores: int = self.cores
        prev_memory: int = self.memory

        self.cores = cores
        self.memory = memory
        
        if self.validate_computer():
            self.calculate_resource_usage()
            self.print(f"{Fore.GREEN}Succesfully edited resources on computer ({self.name}). Memory: {prev_memory} -> {memory}, cores: {prev_cores} -> {cores}")
            return True
        else:
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: can't validate computer ({self.name}). Setting back previus resources.")
            self.cores = prev_cores
            self.memory = memory
            self.calculate_resource_usage()
            return False


    def cleanup(self) -> bool:
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
                    if Path.isfile(Path.join(self.path, file)):
                        self.print(f"Removing file ({file}).")
                        os.remove(Path.join(self.path, file))
                        removed_files += 1
                    else:
                        self.print(f"Removing folder ({file}).")
                        os.rmdir(Path.join(self.path, file))
                        removed_files += 1
                except:
                    self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: can't delete file or folder ({file}). Computer might be unstable.")
                    return False
        
        self.print(f"{Fore.GREEN}Cleanup completed. Removed a total of {removed_files} incorrect files plus folders.")
        return True
    
    def print(self, text: str):
        print(f"{Style.BRIGHT}{Fore.CYAN}[{Fore.WHITE}{self.name}{Fore.CYAN}]: {Fore.RESET+Back.RESET+Style.RESET_ALL}" + text + Fore.RESET+Back.RESET+Style.RESET_ALL)