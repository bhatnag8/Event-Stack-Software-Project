# simulation.py
import time
from colorama import Fore, Style
from event_stack import Event, EventStack
from queue import Queue, generate_poisson_arrival


def log_event(action, queues):
    """
    Print the action happening and the state of all queues.
    """
    print("===========================================================")
    print(f"{Fore.BLUE}[Simulation] {action}{Style.RESET_ALL}")
    for queue in queues:
        queue_state = f"Queue {queue.queue_id}: {queue.jobs}"
        print(queue_state)
    print("===========================================================")


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
    queues[queue_id].remove_job()

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

    log_event(action, queues)


def main():
    global arrival_rate, job_times
    arrival_rate = 1.0  # Arrival rate for the Poisson process
    initial_job_id = 1
    job_times = {}

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

    # Simulation loop
    current_time = 0
    max_simulation_time = 100000
    while not event_stack.is_empty() and current_time < max_simulation_time:
        next_event = event_stack.pop_next_event()
        current_time = next_event.event_time

        if next_event.event_type == "arrival":
            simulate_arrival(event_stack, next_event.details["job_id"], current_time, queues)
        elif next_event.event_type == "departure":
            simulate_departure(event_stack, next_event.details["job_id"], next_event.details["queue_id"], current_time,
                               queues)

        time.sleep(0)  # Delay for visualization

    # Final output of throughput or other metrics if needed
    print("\n================= Simulation Complete =================")
    for i, queue in enumerate(queues):
        print(f"Throughput of Queue {i + 1}: {len(job_times)} jobs")


if __name__ == "__main__":
    main()
