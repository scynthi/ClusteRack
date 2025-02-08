import os
import random
import string
from os import path as Path
from modules.computer import Computer
from colorama import Fore, Style, Back
from smart_rebalancer import *

class Cluster:
    def __init__(self, path: str):
        path : str = Path.normpath(fr"{path}")
        self.path: str = path
        cluster_name: str = path.split(os.sep)[-1]
        self.name : str = cluster_name

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
            id_list: list = []

            process_info_dict: dict = {}

            for app in config[0::4]:
                app_list.append(app)

            # for i in range(len(app_list)):
            #     new_id : str = ''.join(random.choices(string.ascii_lowercase, k=6))
            #     while new_id in id_list:
            #         new_id : str = ''.join(random.choices(string.ascii_lowercase, k=6))

            #     id_list.append(new_id)

            for instance_count in config[1::4]:
                instance_count_list.append(instance_count)

            for cores in config[2::4]:
                cores_list.append(cores)
            
            for memory in config[3::4]:
                memory_list.append(memory)

            for i, app in enumerate(app_list):
                process_info_dict[app] = {"instance_count": instance_count_list[i], "cores": cores_list[i], "memory": memory_list[i]}

            self.processes: dict = process_info_dict

        else:
            self.print(f"Cluster {cluster_name} doesn`t have a config file")

            new_cluster_file = open(Path.join(self.path + cluster_name), "w", encoding="utf-8", )
            new_cluster_file.write("")
            new_cluster_file.close()

        


        files: list = os.listdir(path)

        if ".klaszter" in files:
            files.remove(".klaszter")

        self.cleanup()

        computer_dict: dict = {}

        for file in files:
            computer_dict[file] = Computer(Path.join(path, file))
        
        self.computers : dict = computer_dict
        self.smart_rebalancer : SmartRebalancer = SmartRebalancer(self.path, self)
        
        self.print(f"{Fore.BLACK}{Back.GREEN}Cluster ({cluster_name}) initialized succesfully with {len(computer_dict)} computer(s).")
        self.initialized : bool = True

    def create_computer(self, computer_name: str, cores: int, memory: int) -> Computer:
        path: str = Path.join(self.path, computer_name)

        if Path.exists(path):
            self.print(f"{Fore.RED}Computer ({computer_name}) already exists and will NOT be created.")
            return self.computers[computer_name]
        
        try:
            os.mkdir(path)
            config_file = open(Path.join(path, ".szamitogep_config"), "w", encoding="utf8")
            config_file.write(f"{cores}\n{memory}")
            config_file.close()

            self.print(f"{Fore.GREEN}Computer ({computer_name}) created successfully.")
            return Computer(path)   
        except:
            self.print(f"{Fore.RED}Error while creating computer '{computer_name}'.")
            return


    def try_delete_computer(self, computer_name: str) -> bool:
        path: str = Path.join(self.path, computer_name)

        if not Path.exists(path):
            self.print(f"{Fore.RED}Computer ({computer_name}) does not exist! Did you misspell the name?")
            return False
        
        try:
            computer: Computer = Computer(path)
            if computer.get_processes():
                self.print(f"{Fore.RED}Unable to delete computer '{computer_name}'. It has processes, try using force_delete_computer().")
                return False
            
            os.remove(Path.join(path, ".szamitogep_config"))
            os.rmdir(path)

            self.print(f"{Fore.GREEN}Computer '{computer_name}' deleted successfully.")
            return True
        except:
            self.print(f"{Fore.RED}Unable to delete computer ({computer_name}).")
            return False


    def force_delete_computer(self, computer_name: str) -> bool:
        path: str = Path.join(self.path, computer_name)

        if not Path.exists(path):
            self.print(f"{Fore.RED}Computer ({computer_name}) does not exist! Did you misspell the name?")
            return False
        
        try:
            for file in os.listdir(path):
                os.remove(Path.join(path, file))

            os.rmdir(path)
            self.print(f"{Fore.GREEN}Successfully force deleted computer ({computer_name}).")
            return True
        except:
            self.print(f"{Back.RED}{Fore.BLACK}CRITICAL ERROR DETECTED: force deletion failed for computer {computer_name}.")
            return False


    def rename_cluster(self, new_name : str) -> bool:
        if not self.initialized:
            self.print(f"{Fore.RED}Cluster failed to initialize so renaming can't be done. New cluster name would be: {new_name}.")
            return False
        
        try:
            parent_dir: str = Path.dirname(self.path)
            new_path: str = Path.join(parent_dir, new_name)

            if Path.exists(new_path):
                self.print(f"{Fore.RED}Renaming failed. There is already a cluster called {new_name}.")
                return False

            os.rename(self.path, new_path)
            self.path = new_path
            self.print(f"{Fore.GREEN}Cluster folder renamed to '{new_name}' successfully.")

            #Reload self and children -- so the path updates everywhere
            self.__init__(self.path)
            self.reload_computers()
            return True
            
        except Exception as e:
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: Error renaming cluster: {e}")
            return False
        
    def start_process():
        pass
        

    def reload_computers(self) -> None:
        for name in self.computers:
            pc = self.computers[name]
            self.computers[name] = pc.__init__(Path.join(self.path, name))


    def cleanup(self) -> bool:
        files: list = os.listdir(self.path)
        
        self.print(f"{Fore.GREEN}Starting cleanup...")

        if Path.exists(Path.join(self.path, ".klaszter")):
            files.remove(".klaszter")

        removed_files : int = 0

        for file in files:
            if Path.exists(Path.join(self.path, file, ".szamitogep_config")):
                continue
            
            try:
                if Path.isdir(Path.join(self.path, file)):
                    os.rmdir(Path.join(self.path, file))
                else:
                    os.remove(Path.join(self.path, file))
                self.print(f"{Fore.YELLOW}Removed {file} from filesystem since it was marked as incorrect. ")
            except:
                pass
        
        self.print(f"{Fore.GREEN}Cleanup completed. Removed a total of {removed_files} incorrect files plus folders.")
        return True
    
    def print(self, text: str):
        print(f"{Fore.BLACK}{Back.CYAN}[{Back.WHITE}{self.name}{Back.CYAN}]{Back.RESET}{Fore.CYAN}: {Fore.RESET+Back.RESET+Style.RESET_ALL}" + text + Fore.RESET+Back.RESET+Style.RESET_ALL)


if __name__ == "__main__":
    cluster: Cluster = Cluster(r".\Test folder\cluster3")

    # cluster.edit_cluster_name("cluster0")

    # pc: Computer = cluster.create_computer("szamitogep4", 1000, 8000)
    # print(pc.path)

    # cluster.force_delete_computer("szamitogep4")