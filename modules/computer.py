import os
from os import path as Path
from datetime import datetime


class Computer:
    def __init__(self, path: str) -> None:
        path: str = Path.normpath(fr"{path}")

        if Path.exists(Path.join(path, ".szamitogep_config")):
            config_file = open(Path.join(path, ".szamitogep_config"), "r", encoding="utf8")
            config: list = config_file.readlines()
            config_file.close()

            computer_name: str = path.split(os.sep)[-1]
            cores: int = int(config[0])
            memory: int = int(config[1])

            self.cores: int = cores
            self.memory: int = memory
            self.name: str = computer_name
            self.path: str = path

            if not self.validate_computer(): return
            print(f"Computer ({computer_name}) initialized with {cores} cores and {memory} of memory.\n{self.free_cores} cores and {self.free_memory} memory left free.", end="\n\n")
        else:
            print(f"There's no config file in {path}")


    def validate_computer(self) -> bool:
            usage: dict = self.calculate_resource_usage()

            if usage["memory_usage_percent"] > 100:
                print(f"Computer ({self.name}) is overloaded! Memory limit exceeded ({usage["memory_usage_percent"]}%).")
                return False
            
            if usage["core_usage_percent"] > 100:
                print(f"Computer ({self.name}) is overloaded! Core limit exceeded ({usage["cpu_usage_percent"]}%).")
                return False
            
            return True



    def get_processes(self) -> dict:
        files: list = os.listdir(self.path)
        process_list: dict = {}

        if ".szamitogep_config" in files:
            files.remove(".szamitogep_config")

        for process in files:
            process_list[process] = self.get_process_info(process)
            
        return process_list


    def get_process_info(self, process: str) -> dict:
        if Path.exists(Path.join(self.path, process)):
            process_info: list = process.split("-")

            file = open(Path.join(self.path, process), "r", encoding="utf8")
            process_file_info: list = file.readlines()
            file.close()
            
            for line in process_file_info:
                process_file_info[process_file_info.index(line)] = line.strip()

            return {"name":str(process_info[0]), "id":str(process_info[1]), "date_started": str(process_file_info[0]), "status": str(process_file_info[1]), "cores": int(process_file_info[2]), "memory": int(process_file_info[3])}


    def calculate_resource_usage(self) -> dict:
        processes: dict = self.get_processes()

        memory_usage: int = 0
        cpu_usage: int = 0

        for _, info in processes.items():
            memory_usage += int(info["memory"])
            cpu_usage += int(info["cores"])

        self.free_memory: int = self.memory - memory_usage
        self.free_cores: int = self.cores - cpu_usage

        memory_usage_percentage: float = round(memory_usage / self.memory * 100, 1)
        cpu_usage_percentage: float = round(cpu_usage / self.cores * 100, 1)

        return {"memory_usage_percent": memory_usage_percentage, "core_usage_percent": cpu_usage_percentage}


    def kill_process(self, process: str) -> bool:
        try:
            if Path.exists(Path.join(self.path, process)):
                os.remove(Path.join(self.path, process))
                self.calculate_resource_usage()
                return True
            
            print("Error while killing process: "+process+" does not exists! Perhaps you misspelled the name?")
            return False
        except:
            print("Error while killing process: "+process)
            return False

    
    def start_process(self, process_name: str, status: str, cpu_req: int, ram_req: int) -> bool:
        try:
            if self.free_cores - cpu_req < 0:
                print(f"Error while creating process on computer ({self.name}): "+process_name+" -> Core limit exceeded.")
                return False
            
            if self.free_memory - ram_req < 0:
                print(f"Error while creating process on computer ({self.name}): "+process_name+" -> Memory limit exceeded.")
                return False

            file = open(Path.join(self.path, process_name), "w", encoding="utf8")

            date_started: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data: str = f"{date_started}\n{status.upper()}\n{cpu_req}\n{ram_req}"
            file.write(data)
            file.close()

            self.calculate_resource_usage()
            print(f"Process ({process_name}) started successfully on computer ({self.name}).")
            return True
        except:
            print("Error while creating process: "+process_name)
            return False

    def edit_resources(self, cores: int, memory: int) -> bool:
        min_cores: int = self.cores-self.free_cores
        min_memory: int = self.memory-self.free_memory

        if cores < min_cores:
            print(f"Can't set core count to {cores} on computer ({self.name}). Required minimum cores: {min_cores} ")
            return False
        
        if memory < min_memory:
            print(f"Can't set memory size to {memory} on computer ({self.name}). Required minimum memory size: {min_memory} ")
            return False

        prev_cores: int = self.cores
        prev_memory: int = self.memory

        self.cores = cores
        self.memory = memory
        
        if self.validate_computer():
            self.calculate_resource_usage()
            print(f"Succesfully edited resources on computer ({self.name}). Memory: {prev_memory} -> {memory}, cores: {prev_cores} -> {cores}")
            return True
        else:
            print(f"CRITICAL ERROR DETECTED: can't validate computer ({self.name}). Setting back previus resources.")
            self.cores = prev_cores
            self.memory = memory
            self.calculate_resource_usage()
            return False


