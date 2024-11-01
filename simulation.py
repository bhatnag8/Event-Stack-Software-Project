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

def print_queue_states(action, job_id, queue1_state, queue2_state):
    """
    Prints the formatted queue states after each event.
    Parameters:
        action (str): Description of the action that occurred.
        job_id (int): ID of the job associated with the action.
        queue1_state (str): State message for Queue 1.
        queue2_state (str): State message for Queue 2.
    """
    print("===========================================================")
    print(f"{Fore.BLUE}[Simulation] {action}")
    print(queue1_state)
    print(queue2_state)


def simulate_arrival(event_stack, job_id, arrival_time):
    action = f"Job {job_id} arrives at Queue 1 at time {arrival_time:.2f}"
    queue1.add_job(job_id)
    service_time = queue1.generate_service_time()
    event_stack.insert_event(Event("departure_queue_1", arrival_time + service_time, {"job_id": job_id}))

    next_arrival_time = arrival_time + generate_poisson_arrival(arrival_rate)
    event_stack.insert_event(Event("arrival_queue_1", next_arrival_time, {"job_id": job_id + 1}))

    # Log the addition in Queue 1 and unvaried Queue 2
    queue1_state = f"{Fore.GREEN}[+] ADDITION [{job_id}] Queue 1: {queue1.jobs}{Style.RESET_ALL}"
    queue2_state = f"[ ] UNVARIED [ ] Queue 2: {queue2.jobs}"
    print_queue_states(action, job_id, queue1_state, queue2_state)


def simulate_departure_queue_1(event_stack, job_id, departure_time):
    action = f"Job {job_id} departs Queue 1 at time {departure_time:.2f}"
    queue1.remove_job()
    queue2.add_job(job_id)

    service_time = queue2.generate_service_time()
    event_stack.insert_event(Event("departure_queue_2", departure_time + service_time, {"job_id": job_id}))

    # Log the subtraction from Queue 1 and addition to Queue 2
    queue1_state = f"{Fore.RED}[-] SUBTRACT [{job_id}] Queue 1: {queue1.jobs}{Style.RESET_ALL}"
    queue2_state = f"{Fore.GREEN}[+] ADDITION [{job_id}] Queue 2: {queue2.jobs}{Style.RESET_ALL}"
    print_queue_states(action, job_id, queue1_state, queue2_state)


def simulate_departure_queue_2(job_id, departure_time):
    action = f"Job {job_id} departs Queue 2 at time {departure_time:.2f}"
    queue2.remove_job()

    # Log the subtraction from Queue 2 and unvaried Queue 1
    queue1_state = f"[ ] UNVARIED [ ] Queue 1: {queue1.jobs}"
    queue2_state = f"{Fore.RED}[-] SUBTRACT [{job_id}] Queue 2: {queue2.jobs}{Style.RESET_ALL}"
    print_queue_states(action, job_id, queue1_state, queue2_state)


# Schedule the first arrival event
initial_arrival_time = generate_poisson_arrival(arrival_rate)
event_stack.insert_event(Event("arrival_queue_1", initial_arrival_time, {"job_id": initial_job_id}))

# Simulation loop
current_time = 0
while not event_stack.is_empty():
    next_event = event_stack.pop_next_event()
    current_time = next_event.event_time

    if next_event.event_type == "arrival_queue_1":
        simulate_arrival(event_stack, next_event.details["job_id"], current_time)
    elif next_event.event_type == "departure_queue_1":
        simulate_departure_queue_1(event_stack, next_event.details["job_id"], current_time)
    elif next_event.event_type == "departure_queue_2":
        simulate_departure_queue_2(next_event.details["job_id"], current_time)

    time.sleep(5)  # Delay to slow down the simulation
