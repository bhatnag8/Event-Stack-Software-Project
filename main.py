import time
import numpy as np
import random
import matplotlib.pyplot as plt
from scipy.stats import norm
from colorama import Fore, Style


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
        print(f"{Fore.GREEN}[+] ADDITION [{job_id}] Queue {self.queue_id}: {self.jobs}{Style.RESET_ALL}")

    def remove_job(self, job_id):
        if job_id in self.jobs:
            self.jobs.remove(job_id)
            print(f"{Fore.RED}[-] SUBTRACT [{job_id}] Queue {self.queue_id}: {self.jobs}{Style.RESET_ALL}")
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


def plot_moving_average_queue_lengths(queue_lengths, initial_window_size=100):
    plt.figure()
    for queue_id, lengths in queue_lengths.items():
        window_size = initial_window_size if len(lengths) >= initial_window_size else max(1, len(lengths) // 2)
        if window_size > 1:
            moving_avg_lengths = [
                np.mean(lengths[i:i + window_size]) for i in range(len(lengths) - window_size + 1)
            ]
            time_points = range(window_size, window_size + len(moving_avg_lengths))
            plt.plot(time_points, moving_avg_lengths, label=f"Queue {queue_id}")
        else:
            plt.plot(range(len(lengths)), lengths, label=f"Queue {queue_id}", linestyle="--", alpha=0.7)

    plt.xlabel("Time (arbitrary units)")
    plt.ylabel("Moving Average Queue Length")
    plt.title("Moving Average Queue Length Over Time")
    plt.legend()
    plt.show()


def plot_average_queue_length_with_confidence(queue_lengths):
    plt.figure()
    avg_lengths = {queue_id: np.mean(lengths) for queue_id, lengths in queue_lengths.items()}
    error_bars = {queue_id: calculate_confidence_interval(lengths)[1] for queue_id, lengths in queue_lengths.items()}
    plt.bar(avg_lengths.keys(), avg_lengths.values(), yerr=error_bars.values(), color='skyblue', edgecolor='black', capsize=5)
    plt.xlabel("Queue ID")
    plt.ylabel("Average Queue Length")
    plt.title("Average Queue Length per Queue with 95% CI")
    plt.show()


def plot_cumulative_throughput(throughput, queue_throughput_times):
    plt.figure()
    for queue_id, times in queue_throughput_times.items():
        cumulative_counts = list(range(1, len(times) + 1))
        plt.plot(times, cumulative_counts, label=f"Queue {queue_id}")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Cumulative Jobs Processed")
    plt.title("Cumulative Throughput Over Time")
    plt.legend()
    plt.show()


def plot_sojourn_times_with_confidence(sojourn_times):
    mean_sojourn, mo_error_sojourn = calculate_confidence_interval(sojourn_times)
    plt.figure()
    plt.hist(sojourn_times, bins=30, color='skyblue', edgecolor='black')
    plt.axvline(mean_sojourn, color='red', linestyle='--', label=f'Mean = {mean_sojourn:.2f} ± {mo_error_sojourn:.2f}')
    plt.axvline(mean_sojourn - mo_error_sojourn, color='red', linestyle=':', label='95% CI')
    plt.axvline(mean_sojourn + mo_error_sojourn, color='red', linestyle=':')
    plt.xlabel("Sojourn Time (s)")
    plt.ylabel("Frequency")
    plt.title("Distribution of Sojourn Times with 95% CI")
    plt.legend()
    plt.show()


def plot_utilization(queue_lengths):
    plt.figure()
    utilizations = {queue_id: sum(1 for length in lengths if length > 0) / len(lengths) for queue_id, lengths in queue_lengths.items()}
    plt.bar(utilizations.keys(), utilizations.values(), color='skyblue', edgecolor='black')
    plt.xlabel("Queue ID")
    plt.ylabel("Utilization")
    plt.title("Queue Utilization Over Time")
    plt.show()


# Simulation functions
def log_event(action, queues):
    print(f"{Fore.BLUE}[Simulation] {action}{Style.RESET_ALL}")
    for queue in queues:
        queue_state = f"Queue {queue.queue_id}: {queue.jobs}"
        print(queue_state)
    print("=*==*" * 14)


def simulate_arrival(event_stack, job_id, arrival_time, queues, arrival_rate):
    action = f"Job {job_id} arrives at Queue 1 at time {arrival_time:.2f}"
    queues[0].add_job(job_id)
    job_times[job_id] = {"arrival": arrival_time}
    service_time = queues[0].generate_service_time()
    event_stack.insert_event(Event("departure", arrival_time + service_time, {"job_id": job_id, "queue_id": 0}))
    next_arrival_time = arrival_time + generate_poisson_arrival(arrival_rate)
    event_stack.insert_event(Event("arrival", next_arrival_time, {"job_id": job_id + 1}))
    log_event(action, queues)


def simulate_departure(event_stack, job_id, queue_id, departure_time, queues):
    action = f"Job {job_id} departs Queue {queue_id + 1} at time {departure_time:.2f}"
    queues[queue_id].remove_job(job_id)
    throughput[queue_id + 1] += 1
    queue_throughput_times[queue_id + 1].append(departure_time)

    if queue_id < len(queues) - 1:
        queues[queue_id + 1].add_job(job_id)
        service_time = queues[queue_id + 1].generate_service_time()
        event_stack.insert_event(Event("departure", departure_time + service_time, {"job_id": job_id, "queue_id": queue_id + 1}))
    else:
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
            simulate_departure(event_stack, next_event.details["job_id"], next_event.details["queue_id"], current_time, queues)
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
    plot_cumulative_throughput(throughput, queue_throughput_times)
    plot_sojourn_times_with_confidence(sojourn_times)
    plot_utilization(queue_lengths)

    mean_sojourn, mo_error_sojourn = calculate_confidence_interval(sojourn_times)
    print(f"\nMean Sojourn Time: {mean_sojourn:.2f} ± {mo_error_sojourn:.2f} (95% CI)")

    for queue_id, lengths in queue_lengths.items():
        mean_queue_length, mo_error_queue_length = calculate_confidence_interval(lengths)
        print(f"Average Queue Length for Queue {queue_id}: {mean_queue_length:.2f} ± {mo_error_queue_length:.2f} (95% CI)")

    theoretical_sojourn_time = sum(1 / queue.service_rate for queue in queues)
    theoretical_queue_length = arrival_rate * theoretical_sojourn_time

    print(f"\nTheoretical Mean Sojourn Time (Jackson's Theorem): {theoretical_sojourn_time:.2f}")
    print(f"Theoretical Average Queue Length (Jackson's Theorem): {theoretical_queue_length:.2f}")
    print(f"\nObserved Mean Sojourn Time: {mean_sojourn:.2f}")


# Run the simulation
if __name__ == "__main__":
    queues = [
        Queue(queue_id=1, service_rate=3.5),
        Queue(queue_id=2, service_rate=2.7),
        Queue(queue_id=3, service_rate=5.6),
        Queue(queue_id=4, service_rate=6.4),
        Queue(queue_id=5, service_rate=7.1),
    ]

    mode = 1
    max_value = 700
    arrival_rate = 3
    start(queues, mode, max_value, arrival_rate)
