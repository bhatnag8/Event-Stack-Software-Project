import random

class Queue:
    def __init__(self, queue_id, service_rate):
        """
        Initializes a queue with a given ID and exponential service rate.
        Parameters:
            queue_id (int): The ID of the queue (e.g., 1 or 2).
            service_rate (float): The rate parameter (lambda) for the exponential service time.
        """
        self.queue_id = queue_id
        self.service_rate = service_rate
        self.jobs = []

    def add_job(self, job_id):
        """
        Adds a job to the queue and logs the addition with color-coded output.
        Parameters:
            job_id (int): The ID of the job being added.
        """
        self.jobs.append(job_id)

    def remove_job(self):
        """
        Removes and returns the next job from the queue and logs the removal with color-coded output.
        Returns:
            int: The ID of the job being removed.
        """
        if self.jobs:
            job_id = self.jobs.pop(0)
            return job_id
        return None

    def generate_service_time(self):
        """
        Generates a service time based on the exponential distribution.
        Returns:
            float: Service time for the next job in the queue.
        """
        return random.expovariate(self.service_rate)

def generate_poisson_arrival(rate):
    """
    Generates the next arrival time based on a Poisson process.
    Parameters:
        rate (float): The rate parameter (lambda) for the Poisson arrival process.
    Returns:
        float: The time until the next arrival.
    """
    return random.expovariate(rate)
