import os
from os import path as Path
from modules.computer import Computer
from colorama import Fore, Style, Back


class Cluster:
    def __init__(self, path: str):
        path : str = Path.normpath(fr"{path}")
        cluster_name: str = path.split(os.sep)[-1]

        if Path.exists(Path.join(path, ".klaszter")):
            config_file = open(Path.join(path, ".klaszter"), "r", encoding="utf8")
            config: list = config_file.readlines()
            config_file.close()

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

            self.task_list: dict = task_info_dict

        else:
            print(f"Cluster {cluster_name} doesn`t have a config file") 
        
        

        files: list = os.listdir(path)

        if ".klaszter" in files:
            files.remove(".klaszter")

        computer_dict: dict = {}

        for file in files:
            computer_dict[file] = Computer(Path.join(path, file))
        
        self.path: str = path
        
        self.computers : dict = computer_dict

        print(f"Cluster ({cluster_name}) initialized succesfully with {len(computer_dict)} computer(s).")
        self.initialized : bool = True


    def create_computer(self, computer_name: str, cores: int, memory: int) -> Computer:
        path: str = Path.join(self.path, computer_name)

        if Path.exists(path):
            print(f"Computer ({computer_name}) already exists and will NOT be created.")
            return self.computers[computer_name]
        
        try:
            os.mkdir(path)
            config_file = open(Path.join(path, ".szamitogep_config"), "w", encoding="utf8")
            config_file.write(f"{cores}\n{memory}")
            config_file.close()

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
        
        try:
            computer: Computer = Computer(path)
            if computer.get_processes():
                print(f"Unable to delete computer '{computer_name}'. It has processes, try using force_delete_computer().")
                return False
            
            os.remove(Path.join(path, ".szamitogep_config"))
            os.rmdir(path)

            print(f"Computer '{computer_name}' deleted successfully.")
            return True
        except:
            print(f"Unable to delete computer ({computer_name}).")
            return False


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
            print(f"CRITICAL ERROR DETECTED: force deletion failed for computer {computer_name}.")
            return False


    def rename_cluster(self, new_name : str) -> bool:
        if not self.initialized:
            print(f"Cluster failed to initialize so renaming can't be done. New cluster name would be: {new_name}.")
            return False
        
        try:
            parent_dir: str = Path.dirname(self.path)
            new_path: str = Path.join(parent_dir, new_name)

            if Path.exists(new_path):
                print(f"Renaming failed. There is already a cluster called {new_name}.")
                return False

            os.rename(self.path, new_path)
            self.path = new_path
            print(f"Cluster folder renamed to '{new_name}' successfully.")

            #Reload self and children -- so the path updates everywhere
            self.__init__(self.path)
            self.reload_computers()
            return True

        except Exception as e:
            print(f"Error renaming cluster: {e}")
            return False
        
    def start_process():
        pass
        

    def reload_computers(self) -> None:
        for name in self.computers:
            pc = self.computers[name]
            self.computers[name] = pc.__init__(Path.join(self.path, name))



if __name__ == "__main__":
    cluster: Cluster = Cluster(r".\Test folder\cluster0")

    # cluster.edit_cluster_name("cluster0")

    pc: Computer = cluster.create_computer("szamitogep4", 1000, 8000)
    print(pc.path)

    # cluster.force_delete_computer("szamitogep4")