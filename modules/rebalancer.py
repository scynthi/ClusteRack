import os
import time
import random
import string
from datetime import datetime
from os import path as Path
from colorama import Fore, Style, Back
from modules.computer import Computer

rebalancing_algos = ["load_balance", "best_fit", "fast"]

class Rebalancer:
    def __init__(self, parent_cluster):
        self.cluster = parent_cluster
        self.default_rebalance_algo = rebalancing_algos[0]  # Default algorithm

        self.sorted_computer_list = []
        self.sorted_instances_list = []


    def run_default_rebalance_algo(self):
        """Runs the currently selected algorithm."""
        if self.default_rebalance_algo == "load_balance":
            self.rebalance_load_balance()
        elif self.default_rebalance_algo == "best_fit":
            self.rebalance_best_fit()
        elif self.default_rebalance_algo == "fast":
            self.rebalance_fast()
        else:
            print(f"{Fore.RED}Unknown rebalancing algorithm selected!")


    def sort_computers(self) -> None:
        """Sort computers based on core and memory"""
        if not hasattr(self.cluster, "computers"):
            return

        self.sorted_computer_list = sorted(
            self.cluster.computers.items(),
            key=lambda x: (-x[1].cores, x[1].memory)
        )


    def sort_programs(self) -> None:
        """Sort processes based on req. core and req. memory"""
        if not self.cluster.distributable_instances:
            return

        self.sorted_instances_list = sorted(
                self.cluster.distributable_instances,
                key=lambda instance: (-instance['cores'], -instance['memory'])
            )


    def clear_computers(self):
        """Clears all program instances from computers before rebalancing."""
        for computer in self.cluster.computers.values():
            for instance in computer.get_prog_instances():
                computer.remove_instance(instance)

    def rebalance_load_balance(self):
        """Evenly distributes instances across all computers."""
        print(f"{Fore.YELLOW}Running Load Balance Algorithm...")
        if not self.cluster.computers: return

        self.clear_computers()
        available_computers = list(self.cluster.computers.values())

        for idx, instance in enumerate(self.cluster.distributable_instances):
            target_computer = available_computers[idx % len(available_computers)]
            target_computer.add_instance(instance)

        print(f"{Fore.GREEN}Load balancing complete!{Fore.RESET}")

    def rebalance_best_fit(self):
        """Packs instances efficiently into computers with the most available space."""
        print(f"{Fore.YELLOW}Running Best Fit Algorithm...")
        if not self.cluster.computers: return

        self.clear_computers()
        self.sort_computers()

        for instance in self.cluster.distributable_instances:
            for computer in self.sorted_computer_list:
                if computer[1].can_fit_instance(instance):
                    computer[1].add_instance(instance)
                    break

        print(f"{Fore.GREEN}Best Fit packing complete!{Fore.RESET}")

    def rebalance_fast(self):
        """Quickly assigns instances using a first-fit strategy."""
        print(f"{Fore.YELLOW}Running Fast Algorithm...")
        if not self.cluster.computers: return

        self.clear_computers()

        for instance in self.cluster.distributable_instances:
            for computer in self.cluster.computers.values():
                if computer.can_fit_instance(instance):
                    computer.add_instance(instance)
                    break


        print(f"{Fore.GREEN}Fast rebalancing complete!{Fore.RESET}")

    def print_computer_scores(self):
        """DEBUGGING TOOL: A print for the terminal"""
        print(Fore.CYAN + "Current Computer Scores:" + Style.RESET_ALL)
        for name, computer in self.sorted_computer_list:
            score = self.calculate_computer_score(computer)
            print(f"{Style.BRIGHT + Fore.CYAN}[{Fore.WHITE}{name}{Fore.CYAN}] -> {Fore.WHITE}Score: {Style.BRIGHT+Fore.GREEN}{score:.2f} {Style.NORMAL+Fore.WHITE}(Cores: {computer.free_cores}/{computer.cores}, Memory: {computer.free_memory}/{computer.memory})")

    def print_assignments(self, assignments):
        """DEBUGGING TOOL: A print for the terminal"""
        if not assignments:
            print(Fore.MAGENTA + Style.BRIGHT  + "\nNo assignments happened ---------" + Style.RESET_ALL + Back.RESET)
            return

        print(Fore.CYAN + Style.BRIGHT + "\nProcess Assignments:" + Style.RESET_ALL)
        for process_name, computers in assignments.items():
            assigned_to = [comp.name for comp in computers]
            print(f"{Style.BRIGHT + Fore.CYAN}[{Fore.YELLOW}{process_name}{Fore.CYAN}] -> {Fore.WHITE}{', '.join(assigned_to)}{Style.RESET_ALL}")
