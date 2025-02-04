import os
from os import path as Path
from modules.cluster import Cluster
from modules.computer import Computer


class Root:
    def __init__(self, path: str):
        path : str = Path.normpath(fr"{path}")
        
        if Path.exists(path):
            root_name: str = path.split(os.sep)[-1]


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


    def create_cluster(self, cluster_name: str) -> Cluster:
        path: str = Path.join(self.path, cluster_name)

        if Path.exists(path):
            print(f"Cluster ({cluster_name}) already exists and will NOT be created.")
            return self.clusters[cluster_name]
        
        try:
            os.mkdir(path)
            file = open(Path.join(path, ".klaszter"), "w", encoding="utf8")
            file.close()
            print(f"Cluster ({cluster_name}) created successfully.")

            self.__init__(self.path)

            return Cluster(path)
        except:
            print(f"Error while creating cluster '{cluster_name}'.")
            return


    def try_delete_cluster(self, cluster_name: str) -> bool:
        path: str = Path.join(self.path, cluster_name)

        if not Path.exists(path):
            print(f'Cluster ({cluster_name}) does not exist! Did you misspell the name?')
            return False
        
        try:
            cluster: Cluster = Cluster(path)
            if cluster.computers:
                print(f"Unable to delete cluster '{cluster_name}'. It has computers, try using force_delete_cluster()")
                return False
            
            if Path.exists(Path.join(path, ".klaszter")):
                os.remove(Path.join(path, ".klaszter"))
            
            os.rmdir(path)
            self.__init__(self.path)

            print(f"Cluster '{cluster_name}' deleted successfully.")
            return True

        except:
            print(f"Unable to delete cluster ({cluster_name}).")
            return False


    def force_delete_cluster(self, cluster_name: str) -> bool:
        path: str = Path.join(self.path, cluster_name)
        
        if not Path.exists(path):
            print(f'Cluster ({cluster_name}) does not exist! Did you misspell the name?')
            return False
        
        try:
            if Path.exists(Path.join(path, ".klaszter")):
                os.remove(Path.join(path, ".klaszter"))

            cluster : Cluster = self.clusters[cluster_name]

            for computer in cluster.computers:
                cluster.force_delete_computer(computer)
                        
            os.rmdir(path)
            self.__init__(self.path)

            print(f"Successfully force deleted cluster ({cluster_name}).")
            return True
        
        except:
            print(f"CRITICAL ERROR DETECTED: force deletion failed for computer {cluster_name}.")
            return False


    def relocate_process(self, process, origin, destination):
        pass


    def move_computer(self, computer_name: str, origin_cluster_name: str, destination_cluster_name: str) -> bool:
        if not self.clusters[origin_cluster_name]:
            print(f"The origin cluster {origin_cluster_name} could not be found. Perhapse you misstyped the name")
            return False

        if not self. clusters[destination_cluster_name]:
            print(f"The destination cluster {destination_cluster_name} could not be found. Perhapse you misstyped the name")
            return False

        origin_cluster : Cluster = self.clusters[origin_cluster_name]
        destination_cluster : Cluster = self.clusters[destination_cluster_name]


        if not origin_cluster.computers[computer_name]:
            print(f"The computer ({computer_name}) could not be found under the cluster({origin_cluster_name}). Perhapse you misstyped the name")
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

        pass
    

if __name__ == "__main__":
    root : Root = Root(r".\Test folder")

    cluster1 : Cluster = root.create_cluster("cluster3")

    pc1 : Computer = cluster1.create_computer("computer1", 1000, 7000)
    pc2 : Computer = cluster1.create_computer("computer2", 1000, 7000)
    pc3 : Computer = cluster1.create_computer("computer3", 1000, 7000)

    # cluster1.rename_cluster("klaszter1")

    # pc1.start_process("ultrakill-abcdef", True, 500, 2000)
    



    # cluster : Cluster = root.create_cluster("cluster2")

    # pc1 : Computer = cluster.create_computer("szamitogep1", 1000, 7000)
    # pc2 : Computer = cluster.create_computer("szamitogep2", 2000, 4000)
    # pc3 : Computer = cluster.create_computer("szamitogep3", 3000, 3000)

    