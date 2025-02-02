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
            print(f"Cluster ({cluster_name}) created successfully.")

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

            print(f"Successfully force deleted cluster ({cluster_name}).")
            return True
        
        except:
            print(f"CRITICAL ERROR DETECTED: force deletion failed for computer {cluster_name}.")
            return False


    def relocate_process(self, process, origin, destination):
        pass


    def move_computer(self, computer, origin, destination):
        pass

if __name__ == "__main__":
    root : Root = Root(r".\Test folder")

    root.force_delete_cluster("cluster2")

    # cluster : Cluster = root.create_cluster("cluster2")

    # pc1 : Computer = cluster.create_computer("szamitogep1", 1000, 7000)
    # pc2 : Computer = cluster.create_computer("szamitogep2", 2000, 4000)
    # pc3 : Computer = cluster.create_computer("szamitogep3", 3000, 3000)

    