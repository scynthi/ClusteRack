import shutil
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

            self.ui = None

            self.path :str = path
            self.name :str = root_name
            self.clusters : dict = {}

            self._load_clusters()

            # self.cleanup()
            self.print(f"{Fore.BLACK}{Back.GREEN}Root ({root_name}) initialized succesfully with {len(self.clusters)} cluster(s).{Back.RESET+Fore.RESET}\n")


#Root
    def _load_clusters(self):
        """Update the cluster references"""
        files : list = os.listdir(self.path)
        
        for file in files:
            full_path : str = Path.normpath(Path.join(self.path, file))
            
            if not Path.isdir(full_path):
                continue

            cluster_name = file
            cluster = Cluster(full_path, self)

            if cluster.initialized:
                self.clusters[cluster_name] = cluster


    def relocate_process(self, process_name: str, origin_cluster_name: str, destination_cluster_name: str) -> bool:
        """Moves process from one cluster to another"""
        origin_cluster: Cluster = self.clusters.get(origin_cluster_name)
        destination_cluster: Cluster = self.clusters.get(destination_cluster_name)

        if not origin_cluster or not destination_cluster:
            self.print(f"{Fore.RED}Either the origin or the destination cluster does not exist.")
            return False

        if process_name not in origin_cluster.processes:
            self.print(f"{Fore.RED}Process {process_name} does not exist in cluster {origin_cluster_name}.")
            return False

        process_data = origin_cluster.processes[process_name]  # Reference, no copy needed

        # Check if process already exists in the destination
        if process_name in destination_cluster.processes:
            self.print(f"{Fore.YELLOW}Process {process_name} already exists in {destination_cluster_name}.")

            while True:
                print(
                    f"\n{Fore.CYAN}Choose an option:\n"
                    f"1: Stop (Cancel move)\n"
                    f"2: Overwrite (Replace existing process)\n"
                    f"3: Merge instance counts\n"
                    f"Enter your choice (1/2/3): {Fore.RESET}",
                    end=""
                )
                user_choice = input().strip()

                if user_choice in ["1", "2", "3"]:
                    break
                else:
                    print(f"{Fore.RED}Invalid choice! Please enter 1, 2, or 3.{Fore.RESET}")

            if user_choice == "1":
                self.print(f"{Fore.RED}Move cancelled. {process_name} was not relocated.")
                return False

            elif user_choice == "2":
                self.print(f"{Fore.YELLOW}Overwriting process {process_name} in {destination_cluster_name}.")
                
                overwrite_success = destination_cluster.edit_process_resources(
                    process_name, "instance_count", process_data["instance_count"]
                ) and destination_cluster.edit_process_resources(
                    process_name, "cores", process_data["cores"]
                ) and destination_cluster.edit_process_resources(
                    process_name, "memory", process_data["memory"]
                ) and destination_cluster.edit_process_resources(
                    process_name, "running", process_data["running"]
                )

                if not overwrite_success:
                    self.print(f"{Fore.RED}Failed to overwrite process {process_name} in {destination_cluster_name}.")
                    return False

                self.print(f"{Fore.GREEN}Successfully overwrote process {process_name} in {destination_cluster_name}.")

            elif user_choice == "3":
                self.print(f"{Fore.GREEN}Merging process {process_name} into {destination_cluster_name}.")

                new_instance_count = int(destination_cluster.processes[process_name]["instance_count"]) + int(
                    process_data["instance_count"]
                )

                merge_success = destination_cluster.edit_process_resources(
                    process_name, "instance_count", new_instance_count
                )

                if not merge_success:
                    self.print(f"{Fore.RED}Failed to merge process {process_name} in {destination_cluster_name}.")
                    return False

                self.print(f"{Fore.GREEN}Successfully merged {process_name} into {destination_cluster_name}.")

            # Regardless of case, remove the process from the origin cluster
            if not origin_cluster.kill_process(process_name):
                self.print(f"{Fore.RED}Failed to remove process {process_name} from {origin_cluster_name}.")
                return False

            return True

        # If process does NOT exist in destination, perform a normal move
        self.print(f"{Fore.GREEN}Moving {process_name} from {origin_cluster_name} to {destination_cluster_name}.")

        if not origin_cluster.kill_process(process_name):
            self.print(f"{Fore.RED}Failed to remove process {process_name} from {origin_cluster_name}.")
            return False

        success = destination_cluster.start_process(
            process_name,
            process_data["running"],
            process_data["cores"],
            process_data["memory"],
            process_data["instance_count"],
            process_data["date_started"],
        )

        if success:
            self.print(f"{Fore.GREEN}Successfully moved process {process_name} from {origin_cluster_name} to {destination_cluster_name}.")
            return True
        else:
            self.print(f"{Fore.RED}Failed to start process {process_name} in {destination_cluster_name}.")
            return False


    def move_computer(self, computer_name: str, origin_cluster_name: str, destination_cluster_name: str) -> bool:
        """Moves computer from one cluster to another"""
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


#Cluster
    def create_cluster(self, cluster_name: str) -> Cluster:
        path: str = Path.join(self.path, cluster_name)

        if Path.exists(path):
            self.print(f"{Fore.RED}Cluster ({cluster_name}) already exists and will NOT be created.")
            return self.clusters[cluster_name]
        
        try:
            os.mkdir(path)
            with open(Path.join(path, ".klaszter"), "w", encoding="utf8") as file:
                file.write("")

            self.print(f"{Fore.GREEN}Cluster ({cluster_name}) created successfully.")

            self.clusters[cluster_name] = Cluster(path, self)

            return Cluster(path, self)
        except:
            self.print(f"{Fore.RED}Error while creating cluster '{cluster_name}'.")
            return


    def delete_cluster(self, cluster_name : str, mode : str = "try") -> bool:
        """Deletes clusters either with soft mode('try') or force mode('f')"""

        full_path: str = Path.join(self.path, cluster_name)
        if not Path.exists(full_path):
            self.print(f"{Fore.RED}Cluster ({cluster_name}) does not exist! Check the name and retry.")
            return False
        
        
           
        if mode == "f":
            try:
                shutil.rmtree(full_path)

                self.print(f"{Fore.GREEN}Successfully force deleted cluster ({cluster_name}).")
                
                self._load_clusters()
                return True
            
            except Exception as e:
                self.print(f"{Back.RED}{Fore.BLACK}CRITICAL ERROR DETECTED: force deletion failed for computer {cluster_name} : {e}.")
                return False

        elif mode == "try":
            try:
                cluster : Cluster = self.clusters[cluster_name]

                if cluster.computers:
                    self.print(f"{Fore.RED}Unable to delete cluster '{cluster_name}'. It has computers, try using delete_cluster(cluster_name, 'f').")
                    return False
                
                if Path.exists(Path.join(cluster.path, ".klaszter")):
                    os.remove(Path.join(cluster.path, ".klaszter"))
  

                shutil.rmtree(full_path, ignore_errors=True)

                self.print(f"{Fore.GREEN}Cluster '{cluster_name}' deleted successfully.")
                self._load_clusters()
                return True

            except:
                self.print(f"{Fore.RED}Unable to delete cluster ({cluster_name}).")
                return False
        else:
            self.print(f"{Fore.RED}Can not delete cluster ({cluster_name}) please specify a valid mode")
            return False


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
            new_cluster = Cluster(new_path, self)

            # Update the clusters dictionary
            del self.clusters[target_cluster]
            self.clusters[new_name] = new_cluster

            self.print(f"{Fore.GREEN}Cluster ({target_cluster}) successfully renamed to ({new_name}).")

            return True
            
        except Exception as e:
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: Error renaming cluster: {e}")
            return False


#MISC.
    def cleanup(self) -> bool:
        """Removes unnescecary files and directories from the root""" 
        files: list = os.listdir(self.path)
        
        self.print(f"{Fore.GREEN}Starting cleanup...")

        removed_files : int = 0

        try:
            for file in files:
                target_path = Path.join(self.path, file)

                if Path.isdir(target_path):
                    if ".klaszter" in os.listdir(target_path):
                        continue

                    shutil.rmtree(target_path)
                    removed_files += 1
            
                else:
                    os.remove(target_path)
                    removed_files += 1

                self.print(f"{Fore.YELLOW}Removed {file} from filesystem since it was marked as incorrect.")
                
        except:
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: can't delete file or folder ({file}). Root might be unstable.")
            return False
        

        self.print(f"{Fore.GREEN}Cleanup completed. Removed a total of {removed_files} incorrect files plus folders.")
        return True


    def print(self, text: str):
        """DEBUGGING TOOL: A print for the terminal"""
        print(f"{Fore.BLACK}{Back.CYAN}[{Back.LIGHTBLUE_EX}ROOT{Back.CYAN}]{Back.RESET}{Fore.CYAN}: {Fore.RESET+Back.RESET+Style.RESET_ALL}" + text + Fore.RESET+Back.RESET+Style.RESET_ALL)