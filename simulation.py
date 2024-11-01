import time
from colorama import Fore, Style
from event_stack import Event, EventStack
from queue import Queue, generate_poisson_arrival

# Initialize the event stack and queues
event_stack = EventStack()
queue1 = Queue(queue_id=1, service_rate=0.5)
queue2 = Queue(queue_id=2, service_rate=0.7)

arrival_rate = 1.0
initial_job_id = 1

# Performance metrics data
job_times = {}  # Stores arrival and departure times for each job
queue_lengths = {"queue1": [], "queue2": []}  # Queue lengths over time for each queue
throughput = {"queue1": 0, "queue2": 0}  # Count of jobs processed by each queue


def print_queue_states(action, job_id, queue1_state, queue2_state):
    """
    Prints the formatted queue states after each event.
    Parameters:
        action (str): Description of the action that occurred.
        job_id (int): ID of the job associated with the action.
        queue1_state (str): State message for Queue 1.
        queue2_state (str): State message for Queue 2.
    """
    # print("===========================================================")
    # print(f"{Fore.BLUE}[Simulation] {action}")
    # print(queue1_state)
    # print(queue2_state)
    # print("===========================================================")


def simulate_arrival(event_stack, job_id, arrival_time):
    action = f"Job {job_id} arrives at Queue 1 at time {arrival_time:.2f}"
    queue1.add_job(job_id)

    # Track arrival time for sojourn time calculation
    job_times[job_id] = {"arrival": arrival_time}

    # Schedule the departure event from Queue 1
    service_time = queue1.generate_service_time()
    event_stack.insert_event(Event("departure_queue_1", arrival_time + service_time, {"job_id": job_id}))

    # Schedule the next arrival event
    next_arrival_time = arrival_time + generate_poisson_arrival(arrival_rate)
    event_stack.insert_event(Event("arrival_queue_1", next_arrival_time, {"job_id": job_id + 1}))

    # Log the addition in Queue 1 and unvaried Queue 2
    queue1_state = f"{Fore.GREEN}[+] ADDITION [{job_id}] Queue 1: {queue1.jobs}{Style.RESET_ALL}"
    queue2_state = f"[ ] UNVARIED [ ] Queue 2: {queue2.jobs}"
    print_queue_states(action, job_id, queue1_state, queue2_state)

    # Track queue lengths for metrics
    queue_lengths["queue1"].append(len(queue1.jobs))
    queue_lengths["queue2"].append(len(queue2.jobs))


def simulate_departure_queue_1(event_stack, job_id, departure_time):
    action = f"Job {job_id} departs Queue 1 at time {departure_time:.2f}"
    queue1.remove_job()
    queue2.add_job(job_id)
    throughput["queue1"] += 1  # Track throughput for Queue 1

    # Schedule the departure event from Queue 2
    service_time = queue2.generate_service_time()
    event_stack.insert_event(Event("departure_queue_2", departure_time + service_time, {"job_id": job_id}))

    # Log the subtraction from Queue 1 and addition to Queue 2
    queue1_state = f"{Fore.RED}[-] SUBTRACT [{job_id}] Queue 1: {queue1.jobs}{Style.RESET_ALL}"
    queue2_state = f"{Fore.GREEN}[+] ADDITION [{job_id}] Queue 2: {queue2.jobs}{Style.RESET_ALL}"
    print_queue_states(action, job_id, queue1_state, queue2_state)

    # Track queue lengths for metrics
    queue_lengths["queue1"].append(len(queue1.jobs))
    queue_lengths["queue2"].append(len(queue2.jobs))


def simulate_departure_queue_2(job_id, departure_time):
    action = f"Job {job_id} departs Queue 2 at time {departure_time:.2f}"
    queue2.remove_job()
    throughput["queue2"] += 1  # Track throughput for Queue 2

    # Track departure time for sojourn time calculation
    job_times[job_id]["departure"] = departure_time

    # Log the subtraction from Queue 2 and unvaried Queue 1
    queue1_state = f"[ ] UNVARIED [ ] Queue 1: {queue1.jobs}"
    queue2_state = f"{Fore.RED}[-] SUBTRACT [{job_id}] Queue 2: {queue2.jobs}{Style.RESET_ALL}"
    print_queue_states(action, job_id, queue1_state, queue2_state)

    # Track queue lengths for metrics
    queue_lengths["queue1"].append(len(queue1.jobs))
    queue_lengths["queue2"].append(len(queue2.jobs))


# Schedule the first arrival event
initial_arrival_time = generate_poisson_arrival(arrival_rate)
event_stack.insert_event(Event("arrival_queue_1", initial_arrival_time, {"job_id": initial_job_id}))

# Set maximum simulation time in seconds
max_simulation_time = 1000000  # Adjust this as needed
current_time = 0

# Simulation loop with stopping condition
while not event_stack.is_empty() and current_time < max_simulation_time:
    next_event = event_stack.pop_next_event()
    current_time = next_event.event_time

    if current_time > max_simulation_time:
        print("\n================= Simulation Stopped =================")
        print(f"Reached maximum simulation time of {max_simulation_time} seconds.")
        break

    if next_event.event_type == "arrival_queue_1":
        simulate_arrival(event_stack, next_event.details["job_id"], current_time)
    elif next_event.event_type == "departure_queue_1":
        simulate_departure_queue_1(event_stack, next_event.details["job_id"], current_time)
    elif next_event.event_type == "departure_queue_2":
        simulate_departure_queue_2(next_event.details["job_id"], current_time)

    time.sleep(0)  # Delay to slow down the simulation


# Calculate and log performance metrics after the simulation
print("\n================= Simulation Complete =================")

# Mean Sojourn Time (only include jobs that have both arrival and departure times)
completed_jobs = [job for job in job_times if "arrival" in job_times[job] and "departure" in job_times[job]]
if completed_jobs:
    total_sojourn_time = sum(job_times[job]["departure"] - job_times[job]["arrival"] for job in completed_jobs)
    mean_sojourn_time = total_sojourn_time / len(completed_jobs)
    print(f"Mean Sojourn Time: {mean_sojourn_time:.2f} seconds")
else:
    print("No jobs completed their journey through the system.")

# Average Queue Lengths
avg_queue1_length = sum(queue_lengths["queue1"]) / len(queue_lengths["queue1"]) if queue_lengths["queue1"] else 0
avg_queue2_length = sum(queue_lengths["queue2"]) / len(queue_lengths["queue2"]) if queue_lengths["queue2"] else 0
print(f"Average Queue 1 Length: {avg_queue1_length:.2f}")
print(f"Average Queue 2 Length: {avg_queue2_length:.2f}")

# Throughput (total jobs processed per queue)
print(f"Throughput of Queue 1: {throughput['queue1']} jobs")
print(f"Throughput of Queue 2: {throughput['queue2']} jobs")
