# simulation.py
import time
from colorama import Fore, Style
import numpy as np
from event_stack import Event, EventStack
from queue import Queue, generate_poisson_arrival
from plot_metrics import plot_moving_average_queue_lengths, plot_average_queue_length_with_confidence, plot_cumulative_throughput, plot_sojourn_times_with_confidence, plot_utilization
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

def simulate_arrival(event_stack, job_id, arrival_time, queues, arrival_rate):
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

    # Initialize the event stack
    event_stack = EventStack()
    initial_job_id = 1

    # Schedule the first arrival
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

        # Track queue lengths periodically
        if completed_jobs % 10 == 0:  # Adjust tracking frequency as needed
            for i, queue in enumerate(queues, 1):
                queue_lengths[i].append(len(queue.jobs))

    # Output results and plot metrics
    print("\n================= Simulation Complete =================")
    print(f"Total jobs completed: {completed_jobs}")
    for i, queue in enumerate(queues, 1):
        print(f"Throughput of Queue {i}: {throughput[i]} jobs")

    # Plot metrics after simulation completes
    plot_moving_average_queue_lengths(queue_lengths)
    plot_average_queue_length_with_confidence(queue_lengths)
    plot_cumulative_throughput(throughput, queue_throughput_times)
    plot_sojourn_times_with_confidence(sojourn_times)
    plot_utilization(queue_lengths)

    # Calculate and print confidence intervals
    mean_sojourn, mo_error_sojourn = calculate_confidence_interval(sojourn_times)
    print(f"\nMean Sojourn Time: {mean_sojourn:.2f} ± {mo_error_sojourn:.2f} (95% CI)")

    for queue_id, lengths in queue_lengths.items():
        mean_queue_length, mo_error_queue_length = calculate_confidence_interval(lengths)
        print(f"Average Queue Length for Queue {queue_id}: {mean_queue_length:.2f} ± {mo_error_queue_length:.2f} (95% CI)")

    # Validation with Jackson's Theorem
    theoretical_sojourn_time = sum(1 / queue.service_rate for queue in queues)
    theoretical_queue_length = arrival_rate * theoretical_sojourn_time

    print(f"\nTheoretical Mean Sojourn Time (Jackson's Theorem): {theoretical_sojourn_time:.2f}")
    print(f"Theoretical Average Queue Length (Jackson's Theorem): {theoretical_queue_length:.2f}")
    print(f"\nObserved Mean Sojourn Time: {mean_sojourn:.2f}")

if __name__ == "__main__":
    # Initialize a list of Queue objects, each with a unique queue_id and specified service rate.
    # The service_rate determines the average time each job spends in the queue (exponential distribution).
    queues = [
        Queue(queue_id=1, service_rate=3.5),
        Queue(queue_id=2, service_rate=2.7),
        Queue(queue_id=3, service_rate=5.6),
        Queue(queue_id=4, service_rate=6.4),
        Queue(queue_id=5, service_rate=7.1),
    ]

    # Set the simulation mode:
    # Mode 1: The simulation will run based on a maximum time limit.
    # Mode 2: The simulation will run until a maximum number of jobs are completed.
    mode = 1  # Use Mode 1 for time-based simulation; change to 2 for job-based simulation.

    # Define the limit for the simulation based on the selected mode:
    # - If mode is 1 (time-based), `max_value` represents the maximum simulation time in seconds.
    # - If mode is 2 (job-based), `max_value` represents the maximum number of jobs to complete.
    max_value = 700  # Adjust this based on the mode; e.g., 70 seconds for mode 1.

    # Set the arrival rate of jobs into the system:
    # This rate defines the average number of arrivals per unit of time and affects the job inflow frequency.
    # For Poisson arrivals, the arrival time intervals follow an exponential distribution with this rate.
    arrival_rate = 3  # Example rate; adjust based on desired job arrival frequency.

    # Start the simulation by calling `main` with the defined parameters:
    # - `queues`: The list of initialized Queue objects.
    # - `mode`: Determines whether the simulation is time-based (1) or job-based (2).
    # - `max_value`: Represents the time limit (if mode 1) or job limit (if mode 2).
    # - `arrival_rate`: Controls the frequency of job arrivals into the first queue.
    start(queues, mode, max_value, arrival_rate)

