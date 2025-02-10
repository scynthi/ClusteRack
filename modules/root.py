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

            self.print(f"Starting to initialize root with name {root_name}. This may take a few seconds...")

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
            self.print(f"{Fore.BLACK}{Back.GREEN}Root ({root_name}) initialized succesfully with {len(self.clusters)} computer(s).{Back.RESET+Fore.RESET}\n")


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

    # Only works if there are no computers in the cluster
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

    def relocate_process(self, process_name: str, origin_cluster_name: str, destination_cluster_name: str) -> bool:
        origin_cluster : Cluster = self.clusters.get(origin_cluster_name)
        destination_cluster : Cluster = self.clusters.get(destination_cluster_name)

        if not origin_cluster or not destination_cluster:
            self.print(f"{Fore.RED}Either the origin or the destination cluster does not exist.")
            return False

        if process_name not in origin_cluster.processes:
            self.print(f"{Fore.RED}Process {process_name} does not exist in cluster {origin_cluster_name}.")
            return False

        if process_name in destination_cluster.processes:
            self.print(f"{Fore.RED}Process {process_name} already exists in cluster {destination_cluster_name}.")
            return False

        process_data = origin_cluster.processes[process_name]

        # Kill the process in origin_cluster
        if not origin_cluster.kill_process(process_name):
            self.print(f"{Fore.RED}Failed to remove process {process_name} from {origin_cluster_name}.")
            return False

        # Force refresh `origin_cluster` so it reflects process removal
        origin_cluster.__init__(origin_cluster.path)

        # Start the process in destination_cluster
        success = destination_cluster.start_process(
            process_name,
            process_data["running"],
            process_data["cores"],
            process_data["memory"],
            process_data["instance_count"],
            process_data["date_started"],
        )

        if success:
            # Force refresh `destination_cluster` so it sees the new process
            destination_cluster.__init__(destination_cluster.path)
            self.print(f"{Fore.GREEN}Successfully moved process {process_name} from {origin_cluster_name} to {destination_cluster_name}.")
            return True
        else:
            self.print(f"{Fore.RED}Failed to start process {process_name} in {destination_cluster_name}.")
            return False


    def move_computer(self, origin_cluster_name: str, destination_cluster_name: str, computer_name: str) -> bool:
        origin_cluster : Cluster = self.clusters[origin_cluster_name]
        destination_cluster : Cluster = self.clusters[destination_cluster_name]
        
        if origin_cluster == None:
            self.print(f"{Back.RED}The origin cluster {origin_cluster_name} could not be found. Perhaps you misstyped the name.")
            return False

        if destination_cluster == None:
            self.print(f"{Back.RED}The destination cluster {destination_cluster_name} could not be found. Perhaps you misstyped the name.")
            return False
        

        computer : Computer = origin_cluster.computers[computer_name]
        if computer == None:
            self.print(f"{Back.RED}The computer ({computer_name}) could not be found under the cluster ({origin_cluster_name}). Perhaps you misstyped the name.")
            return False
        
        if computer_name in destination_cluster.computers:
            self.print(f"{Back.RED}There is already a computer named '{computer_name}' on the destination cluster ({destination_cluster_name}). Please rename the computer and try again.")
            return False


        computer_stats_dict : dict = {
            "computer_name" : computer.name,
            "computer_memory" : computer.memory,
            "computer_cores" : computer.cores,
        }

        origin_cluster.force_delete_computer(computer_name)

        destination_cluster.create_computer(computer_stats_dict["computer_name"],computer_stats_dict["computer_cores"],computer_stats_dict["computer_memory"])

        origin_cluster.__init__(origin_cluster.path)
        destination_cluster.__init__(destination_cluster.path)


    def rename_cluster(self, target_cluster : str, new_name : str) -> bool:
        if not target_cluster in self.clusters:
            self.print(f"{Fore.RED}Target cluster ({new_name}) could not be found. Perhapse you misstyped the name?")
            return False
        
        try:
            old_cluster: Cluster = self.clusters[target_cluster]
            old_path: str = old_cluster.path
            parent_dir: str = Path.dirname(old_path)
            new_path: str = Path.join(parent_dir, new_name)

            if Path.exists(new_path):
                self.print(f"{Fore.RED}Renaming failed. There is already a cluster called {new_name}.")
                return False

            # Rename the cluster folder
            os.rename(old_path, new_path)

            # Reinitialize the cluster object with the new path
            new_cluster = Cluster(new_path)

            # Update the clusters dictionary
            del self.clusters[target_cluster]
            self.clusters[new_name] = new_cluster

            self.print(f"{Fore.GREEN}Cluster ({target_cluster}) successfully renamed to ({new_name}).")

            return True
            
        except Exception as e:
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: Error renaming cluster: {e}")
            return False

    # Only for debugging purposes
    def print(self, text: str):
        print(f"{Fore.BLACK}{Back.CYAN}[{Back.LIGHTBLUE_EX}ROOT{Back.CYAN}]{Back.RESET}{Fore.CYAN}: {Fore.RESET+Back.RESET+Style.RESET_ALL}" + text + Fore.RESET+Back.RESET+Style.RESET_ALL)