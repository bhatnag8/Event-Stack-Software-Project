# simulation.py
import time
from colorama import Fore, Style
import matplotlib.pyplot as plt
from numpy.ma.core import count

from event_stack import Event, EventStack
from queue import Queue, generate_poisson_arrival
from plot_metrics import plot_moving_average_queue_lengths, plot_average_queue_length_per_queue, plot_cumulative_throughput, plot_sojourn_times, plot_utilization, plot_average_queue_length_with_confidence, plot_sojourn_times_with_confidence

import numpy as np
from scipy.stats import norm

def calculate_confidence_interval(data, confidence_level=0.95):
    """
    Calculate the confidence interval for a given dataset.
    """
    mean = np.mean(data)
    std_dev = np.std(data, ddof=1)
    z_score = norm.ppf(1 - (1 - confidence_level) / 2)
    margin_of_error = z_score * (std_dev / np.sqrt(len(data)))
    return mean, margin_of_error

def log_event(action, queues):
    """
    Print the action happening and the state of all queues.
    """
    print(f"{Fore.BLUE}[Simulation] {action}{Style.RESET_ALL}")
    for queue in queues:
        queue_state = f"Queue {queue.queue_id}: {queue.jobs}"
        print(queue_state)
    print("=*==*" * 14)

def simulate_arrival(event_stack, job_id, arrival_time, queues):
    """
    Handle the arrival of a job to the first queue.
    """
    action = f"Job {job_id} arrives at Queue 1 at time {arrival_time:.2f}"
    queues[0].add_job(job_id)

    # Track arrival time
    job_times[job_id] = {"arrival": arrival_time}

    # Schedule departure from the first queue
    service_time = queues[0].generate_service_time()
    event_stack.insert_event(Event("departure", arrival_time + service_time, {"job_id": job_id, "queue_id": 0}))

    # Schedule the next arrival
    next_arrival_time = arrival_time + generate_poisson_arrival(arrival_rate)
    event_stack.insert_event(Event("arrival", next_arrival_time, {"job_id": job_id + 1}))

    log_event(action, queues)

def simulate_departure(event_stack, job_id, queue_id, departure_time, queues):
    """
    Handle the departure of a job from a queue and move it to the next queue if available.
    """
    action = f"Job {job_id} departs Queue {queue_id + 1} at time {departure_time:.2f}"
    queues[queue_id].remove_job(job_id)

    # Update throughput for the current queue
    throughput[queue_id + 1] += 1  # Increment throughput for the current queue
    queue_throughput_times[queue_id + 1].append(departure_time)  # Track the departure time for cumulative plotting

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

# simulation.py
# ... (rest of the code remains the same)

def main():
    global arrival_rate, job_times, sojourn_times, queue_lengths, throughput, queue_throughput_times
    arrival_rate = 1.0  # Arrival rate for the Poisson process
    initial_job_id = 1
    job_times = {}
    sojourn_times = []  # Track total time in the system for each job
    queue_lengths = {i: [] for i in range(1, 7)}  # Periodic length tracking for each queue
    throughput = {i: 0 for i in range(1, 7)}  # Count of jobs processed per queue
    queue_throughput_times = {i: [] for i in range(1, 7)}  # Timestamps for throughput over time

    # Define the queues with service rates
    queues = [
        Queue(queue_id=1, service_rate=0.5),
        Queue(queue_id=2, service_rate=0.7),
        Queue(queue_id=3, service_rate=0.6),
        Queue(queue_id=4, service_rate=0.4),
        Queue(queue_id=5, service_rate=0.1),
        Queue(queue_id=6, service_rate=0.9),
    ]

    # Initialize the event stack
    event_stack = EventStack()

    # Schedule the first arrival
    initial_arrival_time = generate_poisson_arrival(arrival_rate)
    event_stack.insert_event(Event("arrival", initial_arrival_time, {"job_id": initial_job_id}))

    # Simulation loop with a maximum time limit
    max_simulation_time = 10000  # Set maximum simulation time
    current_time = 0
    completed_jobs = 0

    while not event_stack.is_empty() and current_time < max_simulation_time:
        next_event = event_stack.pop_next_event()
        current_time = next_event.event_time

        if next_event.event_type == "arrival":
            simulate_arrival(event_stack, next_event.details["job_id"], current_time, queues)
        elif next_event.event_type == "departure":
            simulate_departure(event_stack, next_event.details["job_id"], next_event.details["queue_id"], current_time, queues)
            if next_event.details["queue_id"] == len(queues) - 1:
                completed_jobs += 1

        # Track queue lengths at regular intervals
        if completed_jobs % 100 == 0:
            for i, queue in enumerate(queues, 1):
                queue_lengths[i].append(len(queue.jobs))

    # Final output and plot the metrics
    print("\n================= Simulation Complete =================")
    print(f"Simulation ran for {max_simulation_time} seconds.")
    print(f"Total jobs completed: {completed_jobs}")
    for i, queue in enumerate(queues, 1):
        print(f"Throughput of Queue {i}: {throughput[i]} jobs")

    # Plot metrics after simulation completes
    plot_moving_average_queue_lengths(queue_lengths)
    plot_average_queue_length_with_confidence(queue_lengths)
    plot_cumulative_throughput(throughput, queue_throughput_times)
    plot_sojourn_times_with_confidence(sojourn_times)
    plot_utilization(queue_lengths)

    # Step 1: Calculate Confidence Intervals
    mean_sojourn, mo_error_sojourn = calculate_confidence_interval(sojourn_times)
    print(f"\nMean Sojourn Time: {mean_sojourn:.2f} ± {mo_error_sojourn:.2f} (95% CI)")

    for queue_id, lengths in queue_lengths.items():
        mean_queue_length, mo_error_queue_length = calculate_confidence_interval(lengths)
        print(
            f"Average Queue Length for Queue {queue_id}: {mean_queue_length:.2f} ± {mo_error_queue_length:.2f} (95% CI)")

    # Step 2: Validation with Jackson's Theorem
    theoretical_sojourn_time = sum(1 / queue.service_rate for queue in queues)
    theoretical_queue_length = arrival_rate * theoretical_sojourn_time

    print(f"\nTheoretical Mean Sojourn Time (Jackson's Theorem): {theoretical_sojourn_time:.2f}")
    print(f"Theoretical Average Queue Length (Jackson's Theorem): {theoretical_queue_length:.2f}")

    # Compare theoretical and observed values
    print(f"\nObserved Mean Sojourn Time: {mean_sojourn:.2f}")
    for queue_id, lengths in queue_lengths.items():
        mean_queue_length = np.mean(lengths)
        print(f"Observed Average Queue Length for Queue {queue_id}: {mean_queue_length:.2f}")

if __name__ == "__main__":
    main()
