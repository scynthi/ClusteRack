import shutil
import os
from os import path as Path
from modules.cluster import Cluster
from modules.computer import Computer
from colorama import Fore, Style, Back
import re

class Root:
    def __init__(self, path: str, ui):
        path : str = Path.normpath(fr"{path}")
        
        if Path.exists(path):
            root_name: str = path.split(os.sep)[-1]

            self.print(f"Starting to initialize root with name {root_name}. This may take a few seconds...")

            self.ui = ui

            self.path :str = path
            self.name :str = root_name
            self.clusters : dict = {}

            self._load_clusters()

            self.cleanup()
            self.print(f"{Fore.BLACK}{Back.GREEN}Root ({root_name}) initialized succesfully with {len(self.clusters)} cluster(s).{Back.RESET+Fore.RESET}\n")


#Root
    def _load_clusters(self):
        """Update the cluster references"""
        files : list = os.listdir(self.path)
        self.clusters = {}

        for file in files:
            full_path : str = Path.normpath(Path.join(self.path, file))
            
            if not Path.isdir(full_path):
                continue

            cluster_name = file
            cluster = Cluster(full_path, self)

            if cluster.initialized:
                self.clusters[cluster_name] = cluster


    def relocate_program(self, program_name: str, origin_cluster_name: str, destination_cluster_name: str) -> bool:
        """Moves program from one cluster to another"""
        origin_cluster: Cluster = self.clusters.get(origin_cluster_name)
        destination_cluster: Cluster = self.clusters.get(destination_cluster_name)

        if not origin_cluster or not destination_cluster:
            self.print(f"{Fore.RED}Either the origin or the destination cluster does not exist.")
            return False

        if program_name not in origin_cluster.programs:
            self.print(f"{Fore.RED}Program {program_name} does not exist in cluster {origin_cluster_name}.")
            return False

        program_data = origin_cluster.programs[program_name]  # Reference, no copy needed

        # Check if process already exists in the destination
        if program_name in destination_cluster.programs:
            self.print(f"{Fore.YELLOW}Program {program_name} already exists in {destination_cluster_name}.")
            return False

        # If process does NOT exist in destination, perform a normal move
        self.print(f"{Fore.GREEN}Moving {program_name} from {origin_cluster_name} to {destination_cluster_name}. . .")

        # Good luck figuring  this out.
        destination_cluster.programs[program_name] = origin_cluster.programs[program_name]

        if not destination_cluster._validate_instance_placement(program_name, destination_cluster.programs[program_name]["required_count"]):
            del destination_cluster.programs[program_name]
            
            self.print(f"{Fore.RED}Could not relocate program due to insufficient resources in destination cluster.")
            return False
        
        del destination_cluster.programs[program_name]

        program_details = origin_cluster.programs[program_name]
        if not destination_cluster.add_program(program_name, program_details["required_count"], program_details["cores"], program_details["memory"]):
            self.print(f"Error while adding program to new cluster.")
            return False
        
        if not origin_cluster.kill_program(program_name):
            self.print(f"{Fore.RED}Failed to remove program {program_name} from {origin_cluster_name}.")
            return False
    
        self.print(f"{Fore.GREEN}Successfully moved process {program_name} from {origin_cluster_name} to {destination_cluster_name}.")
        return True

    def move_computer(self, computer_name: str, origin_cluster_name: str, destination_cluster_name: str) -> bool:
        """Moves computer from one cluster to another"""
        origin_cluster : Cluster = self.clusters.get(origin_cluster_name)
        destination_cluster : Cluster = self.clusters.get(destination_cluster_name)
        
        if origin_cluster == None:
            self.print(f"{Back.RED}The origin cluster {origin_cluster_name} could not be found. Perhaps you misstyped the name.")
            return False

        if destination_cluster == None:
            self.print(f"{Back.RED}The destination cluster {destination_cluster_name} could not be found. Perhaps you misstyped the name.")
            return False
        

        computer : Computer = origin_cluster.computers.get(computer_name)
        if computer == None:
            self.print(f"{Back.RED}The computer ({computer_name}) could not be found under the cluster ({origin_cluster_name}). Perhaps you misstyped the name.")
            return False
        
        if computer_name in destination_cluster.computers:
            self.print(f"{Back.RED}There is already a computer named '{computer_name}' on the destination cluster ({destination_cluster_name}). Please rename the computer and try again.")
            return False

        for program_name in origin_cluster.programs:
            if not origin_cluster._validate_instance_placement(program_name, origin_cluster.programs[program_name]["required_count"]):
                self.print(f"{Fore.RED}Couldn`t move computer due to insufficient resources after movement in origin cluster.")
                return False

        origin_cluster.delete_computer(computer_name, "f")
        destination_cluster.create_computer(computer_name, computer.memory, computer.memory)

        origin_cluster.reload_cluster()
        destination_cluster.reload_cluster()
        self.print(f"{Fore.GREEN}Successfully moved computer from : {origin_cluster_name}, to : {destination_cluster_name}")

        return True
    
#Cluster
    def create_cluster(self, cluster_name: str) -> Cluster:
        """Creates a new cluster under the root with no computers."""
        path: str = Path.join(self.path, cluster_name)

        if Path.exists(path):
            self.print(f"{Fore.RED}Cluster ({cluster_name}) already exists and will NOT be created.")
            return self.clusters.get(cluster_name)
        
        try:
            os.mkdir(path)
            with open(Path.join(path, ".klaszter"), "w", encoding="utf8") as file:
                file.write("")

            self.print(f"{Fore.GREEN}Cluster ({cluster_name}) created successfully.")

            self.clusters[cluster_name] = Cluster(Path.join(self.path, cluster_name), self) 

            return self.clusters.get(cluster_name)
        except:
            self.print(f"{Fore.RED}Error while creating cluster '{cluster_name}'.")
            return False

    def delete_cluster(self, cluster_name : str, mode : str = "try") -> bool:
        """Deletes clusters either with soft mode('try') or force mode('f')"""
        
        full_path: str = Path.join(self.path, cluster_name)
        if not Path.exists(full_path):
            self.print(f"{Fore.RED}Cluster ({cluster_name}) does not exist! Check the name and retry.")
            return False
        
        cluster : Cluster = self.clusters.get(cluster_name)
           
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
            if not len(cluster.computers.keys()) == 0:
                self.print(f"{Fore.RED}Unable to delete cluster '{cluster_name}'. It has computers, try using delete_cluster(cluster_name, 'f').")
                return False
            
            try:
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
        """Changes the name of the cluster without reinitializing it."""
        if not target_cluster in self.clusters:
            self.print(f"{Fore.RED}Target cluster ({new_name}) could not be found. Check the name and retry.")
            return False
        
        if new_name in self.clusters:
            self.print(f"{Fore.RED}Renaming failed. There is already a cluster called {new_name}.")
            return False

        try:
            old_path: str = self.clusters[target_cluster].path
            parent_dir: str = Path.dirname(old_path)
            new_path: str = Path.join(parent_dir, new_name)

            # Rename the cluster folder
            os.rename(old_path, new_path)
            self.clusters[new_name] = self.clusters.pop(target_cluster)
            self.clusters[new_name].path = new_path
            self.clusters[new_name].name = new_name
            self.clusters[new_name].config_path = Path.join(new_path, ".klaszter")

            self.print(f"{Fore.GREEN}Cluster ({target_cluster}) successfully renamed to ({new_name}).")

            return True
            
        except Exception as e:
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: Error renaming cluster: {e}")
            return False


#Utils.
    def cleanup(self) -> bool:
        """Removes unnescecary files and directories from the root""" 
        files: list = os.listdir(self.path)

        for cluster in self.clusters:
            files.remove(cluster)

        self.print(f"{Fore.GREEN}Starting cleanup...")

        removed_files : int = 0
        try:
            for file in files:
                target_path = Path.join(self.path, file)

                while True:
                    user_input = self.user_input(
                        f"Ismeretetlen fájl {self.name}: {file}\n"
                        "1: Törlés\n"
                        "2: Megtartás Figyelmeztetés: destabilizálhatja a rendszert)\n"
                        "Választása (1/2): "
                    ).strip()

                    if user_input == "1":
                        try:
                            if Path.isfile(target_path):
                                self.print(f"Removing file ({file}).")
                                os.remove(target_path)
                            else:
                                self.print(f"Removing folder ({file}).")
                                shutil.rmtree(target_path)
                            removed_files += 1

                        except Exception as e:
                            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR: Cannot delete ({file}). {e}")
                        break

                    elif user_input == "2":
                        self.print(f"Skipping file ({file}).")
                        break  # Exit the while loop after action

                    
                    self.print("Invalid input. Please enter 1 or 2.")

                
        except:
            self.print(f"{Fore.BLACK}{Back.RED}CRITICAL ERROR DETECTED: can't delete file or folder ({file}). Root might be unstable.")
            return False
        

        self.print(f"{Fore.GREEN}Cleanup completed. Removed a total of {removed_files} incorrect files plus folders.")
        return True

    def user_input(self, input_question : str) -> str:
        """Splits input so we can use input from the ui."""
        if self.ui == None:
            user_input = input(input_question)
            return user_input
        else:
            question : str = input_question.splitlines()
            from modules.subwindow import SubWindow
            from modules.ui import UI

            popout : SubWindow = SubWindow()
            popout.geometry("600x300")
            popout.close_button.grid_forget()

            popout.content.grid_columnconfigure(0, weight=1)

            question_frame : UI.Frame = UI.Frame(popout.content)
            question_frame.grid(row=0, column=0, sticky="new")
            question_frame.grid_columnconfigure(0, weight=1)

            for i, line in enumerate(question):
                line = re.sub(r"\033\[[0-9;]*m", "", line)
                line = line.replace(">>", "")
        
                UI.Label(question_frame, text=line, justify="left").grid(row=i, column=0)

            answer : UI.Entry =  UI.Entry(popout.content)
            answer.grid(row=1, column=0, pady=10)

            def set_can_continue(event=None):
                nonlocal can_continue
                can_continue = True

            can_continue  : bool = False
            popout.bind("<Return>", set_can_continue)

            while not can_continue:
                popout.update_idletasks()
                popout.update()

            answer = answer.get()
            popout.destroy()
            return answer

    def print(self, text: str):
        """DEBUGGING TOOL: A print for the terminal"""
        print(f"{Fore.BLACK}{Back.CYAN}[{Back.LIGHTBLUE_EX}ROOT{Back.CYAN}]{Back.RESET}{Fore.CYAN}: {Fore.RESET+Back.RESET+Style.RESET_ALL}" + text + Fore.RESET+Back.RESET+Style.RESET_ALL)