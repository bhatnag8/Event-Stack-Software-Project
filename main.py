import time
import numpy as np
import random
import matplotlib.pyplot as plt
from scipy.stats import norm
from colorama import Fore, Style

seed = 1
random.seed(seed)
np.random.seed(seed)

# Event, Node, EventStack classes
class Event:
    def __init__(self, event_type, event_time, details=None):
        self.event_type = event_type
        self.event_time = event_time
        self.details = details


class Node:
    def __init__(self, event):
        self.event = event
        self.next = None
        self.prev = None


class EventStack:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_event(self, event):
        new_node = Node(event)
        if not self.head:
            self.head = self.tail = new_node
        else:
            current = self.head
            while current and current.event.event_time <= event.event_time:
                current = current.next
            if current == self.head:
                new_node.next = self.head
                self.head.prev = new_node
                self.head = new_node
            elif not current:
                self.tail.next = new_node
                new_node.prev = self.tail
                self.tail = new_node
            else:
                prev_node = current.prev
                prev_node.next = new_node
                new_node.prev = prev_node
                new_node.next = current
                current.prev = new_node

    def pop_next_event(self):
        if not self.head:
            return None
        next_event = self.head.event
        self.head = self.head.next
        if self.head:
            self.head.prev = None
        else:
            self.tail = None
        return next_event

    def is_empty(self):
        return self.head is None


# Queue class and helper functions
class Queue:
    def __init__(self, queue_id, service_rate):
        self.queue_id = queue_id
        self.service_rate = service_rate
        self.jobs = []

    def add_job(self, job_id):
        self.jobs.append(job_id)
        #print(f"{Fore.GREEN}[+] ADDITION [{job_id}] Queue {self.queue_id}: {self.jobs}{Style.RESET_ALL}")

    def remove_job(self, job_id):
        if job_id in self.jobs:
            self.jobs.remove(job_id)
            #print(f"{Fore.RED}[-] SUBTRACT [{job_id}] Queue {self.queue_id}: {self.jobs}{Style.RESET_ALL}")
            return job_id
        return None

    def generate_service_time(self):
        return random.expovariate(self.service_rate)


def generate_poisson_arrival(rate):
    return random.expovariate(rate)


# Plotting functions
def calculate_confidence_interval(data, confidence_level=0.95):
    mean = np.mean(data)
    std_dev = np.std(data, ddof=1)
    z_score = norm.ppf(1 - (1 - confidence_level) / 2)
    margin_of_error = z_score * (std_dev / np.sqrt(len(data)))
    return mean, margin_of_error


import numpy as np
import matplotlib.pyplot as plt


def plot_moving_average_queue_lengths(queue_lengths, initial_window_size=100):
    """
    Plot the moving average of queue length over time for each queue.
    The moving average smooths out short-term fluctuations and highlights longer-term trends.

    Parameters:
    - queue_lengths (dict): A dictionary where keys are queue IDs, and values are lists of job counts over time.
    - initial_window_size (int): The window size for calculating the moving average.
    """
    plt.figure()
    for queue_id, lengths in queue_lengths.items():
        # Adjust window size if there are fewer data points than the initial window
        window_size = initial_window_size if len(lengths) >= initial_window_size else max(1, len(lengths) // 2)

        if window_size > 1:
            # Calculate the moving average for each time window
            moving_avg_lengths = [
                np.mean(lengths[i:i + window_size]) for i in range(len(lengths) - window_size + 1)
            ]
            time_points = range(window_size, window_size + len(moving_avg_lengths))
            plt.plot(time_points, moving_avg_lengths, label=f"Queue {queue_id}")
        else:
            # Fallback to raw data if window size is too small
            plt.plot(range(len(lengths)), lengths, label=f"Queue {queue_id}", linestyle="--", alpha=0.7)

    plt.xlabel("Time (arbitrary units)")
    plt.ylabel("Moving Average Queue Length")
    plt.title("Moving Average Queue Length Over Time")
    plt.legend()
    plt.show()


def plot_average_queue_length_with_confidence(queue_lengths):
    """
    Plot the average queue length for each queue with confidence intervals.
    """
    plt.figure()
    avg_lengths = {queue_id: np.mean(lengths) for queue_id, lengths in queue_lengths.items()}
    error_bars = {queue_id: calculate_confidence_interval(lengths)[1] for queue_id, lengths in queue_lengths.items()}

    plt.bar(avg_lengths.keys(), avg_lengths.values(), yerr=error_bars.values(), color='skyblue', edgecolor='black',
            capsize=5)
    plt.xlabel("Queue ID")
    plt.ylabel("Average Queue Length")
    plt.title("Average Queue Length per Queue with 95% CI")
    plt.show()


def plot_cumulative_throughput(throughput, queue_throughput_times):
    """
    Plot cumulative throughput over time for each queue, starting from zero.

    Args:
        throughput (dict): Dictionary with queue IDs as keys and total jobs processed as values.
        queue_throughput_times (dict): Dictionary with queue IDs as keys and lists of times
                                       at which each job was processed.
    """
    plt.figure()
    for queue_id, times in queue_throughput_times.items():
        cumulative_counts = list(range(1, len(times) + 1))  # Cumulative counts of jobs processed
        plt.plot(times, cumulative_counts, label=f"Queue {queue_id}")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Cumulative Jobs Processed")
    plt.title("Cumulative Throughput Over Time")
    plt.legend()
    plt.show()


def plot_average_sojourn_time_with_confidence(queue_sojourn_times):
    """
    Plot the average sojourn time for each queue with confidence intervals.
    """
    plt.figure()
    avg_sojourn_times = {queue_id: np.mean(times) for queue_id, times in queue_sojourn_times.items()}
    error_bars = {queue_id: calculate_confidence_interval(times)[1] for queue_id, times in queue_sojourn_times.items()}
    plt.bar(avg_sojourn_times.keys(), avg_sojourn_times.values(), yerr=error_bars.values(), color='skyblue', edgecolor='black', capsize=5)
    plt.xlabel("Queue ID")
    plt.ylabel("Average Sojourn Time")
    plt.title("Average Sojourn Time per Queue with 95% CI")
    plt.show()


def plot_utilization(queue_lengths):
    """
    Plot utilization for each queue as the proportion of time it is non-empty.
    Utilization provides insight into each queue's load and highlights potential bottlenecks.
    """
    plt.figure()
    utilizations = {queue_id: sum(1 for length in lengths if length > 0) / len(lengths)
                    for queue_id, lengths in queue_lengths.items()}
    plt.bar(utilizations.keys(), utilizations.values(), color='skyblue', edgecolor='black')
    plt.xlabel("Queue ID")
    plt.ylabel("Utilization")
    plt.ylim(0, 1)  # Set y-axis limit from 0 to 1 for consistency across plots
    plt.title("Queue Utilization Over Time")
    plt.show()

def plot_sojourn_times_with_confidence(sojourn_times):

    # Calculate the mean and empirical 95% range (2.5th and 97.5th percentiles)
    mean_sojourn = np.mean(sojourn_times)
    lower_percentile = np.percentile(sojourn_times, 2.5)
    upper_percentile = np.percentile(sojourn_times, 97.5)

    # Plot the histogram of sojourn times
    plt.figure()
    plt.hist(sojourn_times, bins=30, color='skyblue', edgecolor='black')

    # Mark the mean and empirical 95% range
    plt.axvline(mean_sojourn, color='red', linestyle='--', label=f'Mean = {mean_sojourn:.2f}')
    plt.axvline(lower_percentile, color='green', linestyle=':', label='95% Empirical Range Lower')
    plt.axvline(upper_percentile, color='green', linestyle=':', label='95% Empirical Range Upper')

    plt.xlabel("Sojourn Time (s)")
    plt.ylabel("Frequency")
    plt.title("Distribution of Sojourn Times with 95% Empirical Range")
    plt.legend()
    plt.show()


def plot_littles_law_validation(average_queue_length, arrival_rate, average_sojourn_time, config_name):
    """
    Validate Little's Law by comparing the observed average queue length (L)
    with the product of arrival rate (lambda) and average sojourn time (W).

    Args:
    - average_queue_length (float): Observed average queue length from simulation.
    - arrival_rate (float): Arrival rate (throughput).
    - average_sojourn_time (float): Observed average sojourn time from simulation.
    - config_name (str): The name of the current configuration for labeling the plot.
    """
    # Calculate the theoretical queue length using Little's Law
    littles_law_value = arrival_rate * average_sojourn_time

    # Log the components for Little's Law validation
    print(f"\nLittle's Law Validation for {config_name}")
    print(f"Arrival Rate (λ): {arrival_rate:.2f}")
    print(f"Average Sojourn Time (W): {average_sojourn_time:.2f}")
    print(f"λ * W (Expected L): {littles_law_value:.2f}")
    print(f"Observed Average Queue Length (L): {average_queue_length:.2f}\n")

    # Plot the observed and theoretical values for comparison
    plt.figure()
    plt.bar(['Observed L', 'λ * W (Little\'s Law)'], [average_queue_length, littles_law_value],
            color=['skyblue', 'lightcoral'])
    plt.ylabel("Average Queue Length (L)")
    plt.title(f"Validation of Little's Law - {config_name}")
    plt.ylim(0,
             max(average_queue_length, littles_law_value) * 1.1)  # Set y-limit slightly above max for better visibility
    plt.show()





# Simulation functions
def log_event(action, queues):
    #print(f"{Fore.BLUE}[Simulation] {action}{Style.RESET_ALL}")
    for queue in queues:
        queue_state = f"Queue {queue.queue_id}: {queue.jobs}"
        #print(queue_state)
    #print("=*==*" * 14)


def simulate_arrival(event_stack, job_id, arrival_time, queues, arrival_rate):
    action = f"Job {job_id} arrives at Queue 1 at time {arrival_time:.2f}"
    queues[0].add_job(job_id)
    job_times[job_id] = {"arrival": arrival_time}
    service_time = queues[0].generate_service_time()
    event_stack.insert_event(Event("departure", arrival_time + service_time, {"job_id": job_id, "queue_id": 0}))
    next_arrival_time = arrival_time + generate_poisson_arrival(arrival_rate)
    event_stack.insert_event(Event("arrival", next_arrival_time, {"job_id": job_id + 1}))
    log_event(action, queues)


def simulate_departure(event_stack, job_id, queue_id, departure_time, queues, queue_sojourn_times):
    """
    Handle the departure of a job from a queue and move it to the next queue if available.
    """
    action = f"Job {job_id} departs Queue {queue_id + 1} at time {departure_time:.2f}"
    queues[queue_id].remove_job(job_id)

    # Record sojourn time for the specific queue
    arrival_time = job_times[job_id]["arrival"]
    queue_sojourn_times[queue_id + 1].append(departure_time - arrival_time)

    # Update throughput for the current queue
    throughput[queue_id + 1] += 1
    queue_throughput_times[queue_id + 1].append(departure_time)

    # Move to the next queue if it exists
    if queue_id < len(queues) - 1:
        queues[queue_id + 1].add_job(job_id)

        # Schedule the next departure for the next queue
        service_time = queues[queue_id + 1].generate_service_time()
        event_stack.insert_event(
            Event("departure", departure_time + service_time, {"job_id": job_id, "queue_id": queue_id + 1}))
    else:
        # If it's the last queue, record departure time
        job_times[job_id]["departure"] = departure_time
        sojourn_times.append(departure_time - job_times[job_id]["arrival"])

    log_event(action, queues)


def start(queues, mode, max_value, arrival_rate):
    global job_times, sojourn_times, queue_lengths, throughput, queue_throughput_times
    job_times = {}
    sojourn_times = []
    queue_lengths = {i: [] for i in range(1, len(queues) + 1)}
    throughput = {i: 0 for i in range(1, len(queues) + 1)}
    queue_throughput_times = {i: [] for i in range(1, len(queues) + 1)}

    queue_sojourn_times = {i: [] for i in range(1, len(queues) + 1)}  # Initialize per-queue sojourn times

    event_stack = EventStack()
    initial_job_id = 1
    initial_arrival_time = generate_poisson_arrival(arrival_rate)
    event_stack.insert_event(Event("arrival", initial_arrival_time, {"job_id": initial_job_id}))

    current_time = 0
    completed_jobs = 0

    while not event_stack.is_empty():
        next_event = event_stack.pop_next_event()
        current_time = next_event.event_time

        if mode == 1 and current_time >= max_value:
            break
        elif mode == 2 and completed_jobs >= max_value:
            break

        if next_event.event_type == "arrival":
            simulate_arrival(event_stack, next_event.details["job_id"], current_time, queues, arrival_rate)
        elif next_event.event_type == "departure":
            simulate_departure(event_stack, next_event.details["job_id"], next_event.details["queue_id"], current_time, queues, queue_sojourn_times)
            if next_event.details["queue_id"] == len(queues) - 1:
                completed_jobs += 1

        if completed_jobs % 10 == 0:
            for i, queue in enumerate(queues, 1):
                queue_lengths[i].append(len(queue.jobs))

    print("\n================= Simulation Complete =================")
    print(f"Total jobs completed: {completed_jobs}")
    for i, queue in enumerate(queues, 1):
        print(f"Throughput of Queue {i}: {throughput[i]} jobs")

    plot_moving_average_queue_lengths(queue_lengths)
    plot_average_queue_length_with_confidence(queue_lengths)
    #plot_cumulative_throughput(throughput, queue_throughput_times) # not present in v2 of assignment
    plot_utilization(queue_lengths)

    plot_average_sojourn_time_with_confidence(queue_sojourn_times)
    plot_sojourn_times_with_confidence(sojourn_times)


    mean_sojourn, mo_error_sojourn = calculate_confidence_interval(sojourn_times)
    print(f"\nMean Sojourn Time: {mean_sojourn:.2f} ± {mo_error_sojourn:.2f} (95% CI)")

    for queue_id, lengths in queue_lengths.items():
        mean_queue_length, mo_error_queue_length = calculate_confidence_interval(lengths)
        print(f"Average Queue Length for Queue {queue_id}: {mean_queue_length:.2f} ± {mo_error_queue_length:.2f} (95% CI)")

    theoretical_sojourn_time = sum(1 / queue.service_rate for queue in queues)
    theoretical_queue_length = arrival_rate * theoretical_sojourn_time

    # print(f"\nTheoretical Mean Sojourn Time (Jackson's Theorem): {theoretical_sojourn_time:.2f}")
    # print(f"Theoretical Average Queue Length (Jackson's Theorem): {theoretical_queue_length:.2f}")
    # print(f"\nObserved Mean Sojourn Time: {mean_sojourn:.2f}")
    return theoretical_sojourn_time, theoretical_queue_length, mean_sojourn, queue_lengths

# Run the simulation
if __name__ == "__main__":
    # Define the three configurations for the simulation with different queue settings, arrival rates, and load conditions.
    configurations = [
        {
            "name": "Moderate Load, Balanced capacity",
            "queues": [
                Queue(queue_id=1, service_rate=3.5),
                Queue(queue_id=2, service_rate=2.7),
                Queue(queue_id=3, service_rate=5.6),
                Queue(queue_id=4, service_rate=6.4),
                Queue(queue_id=5, service_rate=7.1),
            ],
            "arrival_rate": 3,
            "max_value": 700,
        },
        {
            "name": "High Load, Low Capacity",
            "queues": [
                Queue(queue_id=1, service_rate=3.0),
                Queue(queue_id=2, service_rate=2.5),
                Queue(queue_id=3, service_rate=3.3),
                Queue(queue_id=4, service_rate=3.0),
                Queue(queue_id=5, service_rate=1.5),
            ],
            "arrival_rate": 7.5,
            "max_value": 700,
        },
        {
            "name": "Low Load, High Capacity",
            "queues": [
                Queue(queue_id=1, service_rate=8.0),
                Queue(queue_id=2, service_rate=6.8),
                Queue(queue_id=3, service_rate=7.4),
                Queue(queue_id=4, service_rate=7.9),
                Queue(queue_id=5, service_rate=8.0),
            ],
            "arrival_rate": 1.2,
            "max_value": 700,
        },
    ]

    # Mode selection: Mode 1 indicates that the simulation runs for a time-based limit (i.e., `max_value` represents time).
    mode = 1

    # Loop through each defined configuration, running the simulation and generating plots and metrics for each setup.
    for config in configurations:
        print(f"\nRunning configuration: {config['name']}")  # Output configuration name for clarity
        # Start the simulation with the defined parameters for each configuration.
        theoretical_sojourn, theoretical_queue_length, observed_mean_sojourn, queue_lengths = start(
            queues=config["queues"],
            mode=mode,
            max_value=config["max_value"],
            arrival_rate=config["arrival_rate"]
        )
        print(f"\n{config['name']} Theoretical Mean Sojourn Time (Jackson's Theorem): {theoretical_sojourn:.2f}")
        print(f"{config['name']} Theoretical Average Queue Length (Jackson's Theorem): {theoretical_queue_length:.2f}")
        print(f"{config['name']} Observed Mean Sojourn Time: {observed_mean_sojourn:.2f}\n")
        # Inside the main loop after each configuration's simulation run
        observed_avg_queue_length = sum(np.mean(lengths) for lengths in queue_lengths.values())
        plot_littles_law_validation(
            average_queue_length=observed_avg_queue_length,
            arrival_rate=config["arrival_rate"],
            average_sojourn_time=observed_mean_sojourn,
            config_name=config["name"]
        )


