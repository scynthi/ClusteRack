import os
from os import path as Path

path : str = os.path.normpath(r"C:\GitHub\ClusteRack\Test folder\cluster0\szamitogep2")



class Computer:
    def __init__(self, path : str) -> None:
        if Path.exists(Path.join(path, ".szamitogep_config")):

            computer_name : str = path.split(os.sep)[-1]

            config : list = open(Path.join(path, ".szamitogep_config"), "r", encoding="utf8").readlines()

            for line in config:
                if "\n" in line:
                    line = line.strip("\n")

            cores : int = int(config[0])
            memory : int = int(config[1])

            self.cores = cores
            self.memory = memory
            self.name = computer_name
            self.path = path

            print(f"Computer ({computer_name}) initialized with {cores} cores and {memory} of memory.", end="\n\n")


    def get_processes(self) -> dict:
        files : list = os.listdir(self.path)
        process_list : dict = {}

        if ".szamitogep_config" in files:
            files.remove(".szamitogep_config")

        for process in files:
            process_list[process] = self.get_process_info(process)
            
        return process_list


    def get_process_info(self, process : str) -> dict:
        process_file_info : list = open(Path.join(self.path, process), "r", encoding="utf8").readlines()

        process_info: list = process.split("-")
        

        for line in process_file_info:
            if "\n" in line:
                process_file_info[process_file_info.index(line)] = line.strip("\n")
        

        return {"name":process_info[0], "id":process_info[1], "date_started": process_file_info[0], "status": process_file_info[1], "cpu_req": process_file_info[2], "memory_req": process_file_info[3]}

    def calculate_resource_usage(self) -> dict:
        processes : dict = self.get_processes()

        memory_usage : int = 0
        cpu_usage : int = 0

        for _, info in processes.items():
            memory_usage += int(info["memory_req"])
            cpu_usage += int(info["cpu_req"])

        memory_usage_percentage : float = round(memory_usage / self.memory * 100, 1)
        cpu_usage_percentage : float = round(cpu_usage / self.cores * 100, 1)

        return {"memory_usage_percent": memory_usage_percentage, "cpu_usage_percent": cpu_usage_percentage}

        


if __name__ == "__main__":
    pc : Computer = Computer(path)

    print(pc.get_processes())
    print(pc.calculate_resource_usage())

