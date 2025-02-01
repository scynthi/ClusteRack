import os
from os import path as Path
from modules.computer import Computer


class Cluster:
    def __init__(self, path: str):
        path : str = Path.normpath(fr"{path}")

        if Path.exists(Path.join(path, ".klaszter")):
            config_file = open(Path.join(path, ".klaszter"), "r", encoding="utf8")
            config: list = config_file.readlines()
            config_file.close()

            cluster_name: str = path.split(os.sep)[-1]

            for line in config:
                config[config.index(line)] = line.strip()
            
            app_list: list = []
            instance_count_list: list = []
            cores_list: list = []
            memory_list: list = []

            task_info_dict: dict = {}

            for app in config[0::4]:
                app_list.append(app)
            
            for instance_count in config[1::4]:
                instance_count_list.append(instance_count)

            for cores in config[2::4]:
                cores_list.append(cores)
            
            for memory in config[3::4]:
                memory_list.append(memory)

            for i, app in enumerate(app_list):
                task_info_dict[app] = {"instance_count": instance_count_list[i], "cores": cores_list[i], "memory": memory_list[i]}


            files: list = os.listdir(path)
            files.remove(".klaszter")

            computer_list: dict = {}

            for file in files:
                computer_list[file] = Computer(Path.join(path, file))
            
            self.path: str = path
            self.task_list: dict = task_info_dict
            self.computers : list = computer_list

            print(f"Cluster ({cluster_name}) initialized succesfully with {len(computer_list)} computer(s).")
            

    def create_computer(self, computer_name: str, cores: int, memory: int) -> Computer:
        path: str = Path.join(self.path, computer_name)

        if Path.exists(path):
            print(f"Computer ({computer_name}) already exists and will NOT be created.")
            return self.computers[computer_name]
        
        try:
            os.mkdir(path)
            config_file = open(Path.join(path, ".szamitogep_config"), "w", encoding="utf8")
            config_file.write(f"{cores}\n{memory}")

            print(f"Computer ({computer_name}) created successfully.")
            return Computer(path)
        
        except:
            print(f"Error while creating computer '{computer_name}'.")
            return


    def try_delete_computer(self, computer_name: str) -> bool:
        path: str = Path.join(self.path, computer_name)

        if not Path.exists(path):
            print(f"Computer ({computer_name}) does not exist! Did you misspell the name?")
            return False
        
        computer: Computer = Computer(path)
        if computer.get_processes():
            print(f"Unable to delete computer '{computer_name}'. It has processes, try using force_delete_computer().")
            return False
        
        os.remove(Path.join(path, ".szamitogep_config"))
        os.rmdir(path)

        print(f"Computer '{computer_name}' deleted successfully.")
        return True


    def force_delete_computer(self, computer_name: str) -> bool:
        path: str = Path.join(self.path, computer_name)

        if not Path.exists(path):
            print(f"Computer ({computer_name}) does not exist! Did you misspell the name?")
            return False
        
        try:
            for file in os.listdir(path):
                os.remove(Path.join(path, file))

            os.rmdir(path)
            print(f"Successfully force deleted computer ({computer_name}).")
            return True
        
        except:
            print(f"FORCED DELETE FAILED FOR COMPUTER ({computer_name}).")
            return False


if __name__ == "__main__":
    cluster: Cluster = Cluster(r".\Test folder\cluster0")
    pc: Computer = cluster.create_computer("szamitogep4", 1000, 8000)

    pc.start_process("test-yxssss", "aktív", 10, 10)
    cluster.try_delete_computer("szamitogep4")
    cluster.force_delete_computer("szamitogep4")