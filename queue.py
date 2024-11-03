# queue.py
from colorama import Fore, Style
import random

class Queue:
    def __init__(self, queue_id, service_rate):
        """
        Initialize the queue with a specific service rate.
        """
        self.queue_id = queue_id
        self.service_rate = service_rate  # Mean service time is controlled by this rate
        self.jobs = []

    def add_job(self, job_id):
        """
        Adds a job to the queue.
        """
        self.jobs.append(job_id)
        # print(f"{Fore.GREEN}[+] ADDITION [{job_id}] Queue {self.queue_id}: {self.jobs}{Style.RESET_ALL}")

    def remove_job(self):
        """
        Removes a job from the queue.
        """
        if self.jobs:
            job_id = self.jobs.pop(0)
            # print(f"{Fore.RED}[-] SUBTRACT [{job_id}] Queue {self.queue_id}: {self.jobs}{Style.RESET_ALL}")
            return job_id
        return None

    def generate_service_time(self):
        """
        Generate service times using an exponential distribution.
        This meets the assumption of identically distributed and independent service times.
        """
        return random.expovariate(self.service_rate)

def generate_poisson_arrival(rate):
    """
    Generates arrival times for jobs using an exponential distribution.
    This meets the Poisson arrival assumption for Queue 1.
    """
    return random.expovariate(rate)
