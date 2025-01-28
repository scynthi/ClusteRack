import os
from os import path as Path
from modules.computer import Computer


class Cluster:
    def __init__(self, path : str):
        path = Path.normpath(fr"{path}")

        if Path.exists(Path.join(path, ".klaszter")):
            config_file = open(Path.join(path, ".klaszter"), "r", encoding="utf8")
            config : list = config_file.readlines()
            config_file.close()

            cluster_name : str = path.split(os.sep)[-1]

            for line in config:
                config[config.index(line)] = line.strip()
            
            app_list : list = []
            instance_count_list : list = []
            cores_list : list = []
            memory_list : list = []

            task_info_dict : dict = {}

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


            files : list = os.listdir(path)
            files.remove(".klaszter")

            computer_list : list = []

            for file in files:
                computer_list.append(Computer(Path.join(path, file)))
            
            print(f"Cluster ({cluster_name}) has been initialized with {len(computer_list)} computer(s).")
                    
                    
                    
        
            


if __name__ == "__main__":
    cluster : Cluster = Cluster(r".\Test folder\cluster0")