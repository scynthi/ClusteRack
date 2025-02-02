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

            computer_dict: dict = {}

            for file in files:
                computer_dict[file] = Computer(Path.join(path, file))
            
            self.path: str = path
            self.task_list: dict = task_info_dict
            self.computers : dict = computer_dict

            print(f"Cluster ({cluster_name}) initialized succesfully with {len(computer_dict)} computer(s).")
            self.initialized : bool = True
        else:
            print(f"Cluster can't be initialized with path given: {path}.")
            self.initialized : bool = False  

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
            print(f"CRITICAL ERROR DETECTED: forced deletion failed for computer {computer_name}.")
            return False


    def edit_cluster_name(self, new_name : str = "Default Cluster") -> bool:

        if not self.initialized:
            print(f"Cluster failed to initialize so renaming can'T be done. New cluster name would be: {new_name}.")
            return False
        
        try:
            parent_dir: str = Path.dirname(self.path)
            new_path: str = Path.join(parent_dir, new_name)

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
        

    def reload_computers(self) -> None:
        for name in self.computers:
            pc = self.computers[name]
            pc.__init__(Path.join(self.path, name))



if __name__ == "__main__":
    cluster: Cluster = Cluster(r".\Test folder\cluster0")

    cluster.edit_cluster_name("anyad")

    pc: Computer = cluster.create_computer("szamitogep4", 1000, 8000)
    print(pc.path)

    cluster.force_delete_computer("szamitogep4")
