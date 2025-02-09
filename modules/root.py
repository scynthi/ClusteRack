import os
from os import path as Path
from modules.cluster import Cluster
from modules.computer import Computer
from colorama import Fore, Style, Back


class Root:
    def __init__(self, path: str):
        path : str = Path.normpath(fr"{path}")
        
        if Path.exists(path):
            root_name: str = path.split(os.sep)[-1]

            self.print(f"Starting to initialize root with name {root_name}. This may take a few minutes...")

            files : list = os.listdir(path)
            cluster_dict: dict = {}
            
            for file in files:
                full_path : str = Path.normpath(Path.join(path, file))
                
                if not Path.isdir(full_path):
                    continue

                cluster_name = file
                cluster_dict[cluster_name] = Cluster(full_path)

            self.path :str = path
            self.name :str = root_name
            self.clusters : dict = cluster_dict
            self.print("Root initialized")


    def create_cluster(self, cluster_name: str) -> Cluster:
        path: str = Path.join(self.path, cluster_name)

        if Path.exists(path):
            self.print(f"Cluster ({cluster_name}) already exists and will NOT be created.")
            return self.clusters[cluster_name]
        
        try:
            os.mkdir(path)
            file = open(Path.join(path, ".klaszter"), "w", encoding="utf8")
            file.close()
            self.print(f"Cluster ({cluster_name}) created successfully.")

            self.__init__(self.path)

            return Cluster(path)
        except:
            self.print(f"Error while creating cluster '{cluster_name}'.")
            return


    def try_delete_cluster(self, cluster_name: str) -> bool:
        path: str = Path.join(self.path, cluster_name)

        if not Path.exists(path):
            self.print(f'Cluster ({cluster_name}) does not exist! Did you misspell the name?')
            return False
        
        try:
            cluster: Cluster = Cluster(path)
            if cluster.computers:
                self.print(f"Unable to delete cluster '{cluster_name}'. It has computers, try using force_delete_cluster()")
                return False
            
            if Path.exists(Path.join(path, ".klaszter")):
                os.remove(Path.join(path, ".klaszter"))
            
            os.rmdir(path)
            self.__init__(self.path)

            self.print(f"Cluster '{cluster_name}' deleted successfully.")
            return True

        except:
            self.print(f"Unable to delete cluster ({cluster_name}).")
            return False


    def force_delete_cluster(self, cluster_name: str) -> bool:
        path: str = Path.join(self.path, cluster_name)
        
        if not Path.exists(path):
            self.print(f'Cluster ({cluster_name}) does not exist! Did you misspell the name?')
            return False
        
        try:
            if Path.exists(Path.join(path, ".klaszter")):
                os.remove(Path.join(path, ".klaszter"))

            cluster : Cluster = self.clusters[cluster_name]

            for computer in cluster.computers:
                cluster.force_delete_computer(computer)
                        
            os.rmdir(path)
            self.__init__(self.path)

            self.print(f"Successfully force deleted cluster ({cluster_name}).")
            return True
        
        except:
            self.print(f"CRITICAL ERROR DETECTED: force deletion failed for computer {cluster_name}.")
            return False


    def relocate_process(self, process_name: str, origin_cluster_name: str, origin_computer_name: str, destination_cluster_name: str, destination_computer_name: str) -> bool:
        origin_cluster : Cluster = self.clusters.get(origin_cluster_name)
        destination_cluster : Cluster = self.clusters.get(destination_cluster_name)

        if origin_cluster == None or destination_cluster == None:
            self.print("Either the origin or the destination cluster does not exist.")
            return False
        

        origin_computer : Computer = None
        destination_computer : Computer = None
        
        for computer in origin_cluster.computers.values():
            pc : Computer = computer

            if pc.name == origin_computer_name:
                origin_computer = pc

        for computer in destination_cluster.computers.values():
            pc : Computer = computer
            
            if pc.name == destination_computer_name:
                destination_computer = pc
        
        if origin_computer == None or destination_computer == None:
            self.print("Either the origin or the destination computer does not exist.")
            return False
        
        if process_name in destination_computer.get_processes().keys():
            self.print(f"A process with the same name and id is already running on computer {destination_computer_name}.")
            return False

        if not process_name in origin_computer.get_processes().keys():
            self.print(f"Process {process_name} does not exists on computer {origin_cluster_name}/{origin_computer_name}.")
            return False
        

        process_info : dict = origin_computer.get_process_info(process_name)

        if not origin_computer.kill_process(process_name):
            self.print(f"Can't kill process ({process_name}) on computer {origin_cluster_name}/{origin_computer_name}.")

        if not destination_computer.start_process_with_dict(process_info):
            self.print(f"Can't start process ({process_name}) on computer {destination_cluster_name}/{destination_computer_name}.")

        

        self.print(f"Succesfully moved process {process_name} from {origin_cluster_name}/{origin_computer_name} to cluster {destination_cluster_name}/{destination_computer_name}.")
        return False


    def move_computer(self, computer_name: str, origin_cluster_name: str, destination_cluster_name: str) -> bool:
        if not self.clusters.get(origin_cluster_name):
            self.print(f"The origin cluster {origin_cluster_name} could not be found. Perhaps you misstyped the name.")
            return False

        if not self.clusters.get(destination_cluster_name):
            self.print(f"The destination cluster {destination_cluster_name} could not be found. Perhaps you misstyped the name.")
            return False

        origin_cluster : Cluster = self.clusters[origin_cluster_name]
        destination_cluster : Cluster = self.clusters[destination_cluster_name]


        if not origin_cluster.computers.get(computer_name):
            self.print(f"The computer ({computer_name}) could not be found under the cluster ({origin_cluster_name}). Perhaps you misstyped the name.")
            return False
        
        computer : Computer = origin_cluster.computers[computer_name]

        computer_stats_dict : dict = {
            "computer_name" : computer.name,
            "computer_memory" : computer.memory,
            "computer_cores" : computer.cores,
            "computer_process_dict" : computer.get_processes()
        }

        origin_cluster.force_delete_computer(computer_name)

        destination_cluster.create_computer(computer_stats_dict["computer_name"],computer_stats_dict["computer_cores"],computer_stats_dict["computer_memory"])

    def print(self, text: str):
        print(f"{Fore.BLACK}{Back.CYAN}[{Back.LIGHTBLUE_EX}ROOT{Back.CYAN}]{Back.RESET}{Fore.CYAN}: {Fore.RESET+Back.RESET+Style.RESET_ALL}" + text + Fore.RESET+Back.RESET+Style.RESET_ALL)