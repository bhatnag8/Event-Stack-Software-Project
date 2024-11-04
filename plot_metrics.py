# plot_metrics.py
import numpy as np

import matplotlib.pyplot as plt
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


def plot_moving_average_queue_lengths(queue_lengths, initial_window_size=100):
    """
    Plot the moving average of queue length over time for each queue.
    If the number of data points is less than the window size, adjust the window size accordingly.
    """
    plt.figure()
    for queue_id, lengths in queue_lengths.items():
        if len(lengths) < initial_window_size:
            # Adjust window size if not enough data points
            window_size = max(1, len(lengths) // 2)
        else:
            window_size = initial_window_size

        if window_size > 1:
            # Calculate moving average with the adjusted window size
            moving_avg_lengths = [
                np.mean(lengths[i:i + window_size]) for i in range(len(lengths) - window_size + 1)
            ]
            time_points = range(window_size, window_size + len(moving_avg_lengths))
            plt.plot(time_points, moving_avg_lengths, label=f"Queue {queue_id}")
        else:
            # Fallback to raw data if window size is 1
            plt.plot(range(len(lengths)), lengths, label=f"Queue {queue_id}", linestyle="--", alpha=0.7)

    plt.xlabel("Time (arbitrary units)")
    plt.ylabel("Moving Average Queue Length")
    plt.title("Moving Average Queue Length Over Time")
    plt.legend()
    plt.show()

def plot_average_queue_length_per_queue(queue_lengths):
    """
    Plot the average queue length for each queue over the entire simulation.
    """
    plt.figure()
    avg_lengths = {queue_id: sum(lengths) / len(lengths) for queue_id, lengths in queue_lengths.items()}
    plt.bar(avg_lengths.keys(), avg_lengths.values(), color='skyblue', edgecolor='black')
    plt.xlabel("Queue ID")
    plt.ylabel("Average Queue Length")
    plt.title("Average Queue Length per Queue")
    plt.show()

def plot_cumulative_throughput(throughput, queue_throughput_times):
    """
    Plot cumulative throughput over time for each queue, starting from zero.
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

def plot_sojourn_times(sojourn_times):
    """
    Plot a histogram of sojourn times.
    """
    plt.figure()
    plt.hist(sojourn_times, bins=30, color='skyblue', edgecolor='black')
    plt.xlabel("Sojourn Time (s)")
    plt.ylabel("Frequency")
    plt.title("Distribution of Sojourn Times")
    plt.show()

def plot_utilization(queue_lengths):
    """
    Plot utilization for each queue as the proportion of time it is non-empty.
    """
    plt.figure()
    utilizations = {queue_id: sum(1 for length in lengths if length > 0) / len(lengths)
                    for queue_id, lengths in queue_lengths.items()}
    plt.bar(utilizations.keys(), utilizations.values(), color='skyblue', edgecolor='black')
    plt.xlabel("Queue ID")
    plt.ylabel("Utilization")
    plt.title("Queue Utilization Over Time")
    plt.show()

def plot_sojourn_times_with_confidence(sojourn_times):
    """
    Plot a histogram of sojourn times with the mean and confidence interval.
    """
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

def plot_average_queue_length_with_confidence(queue_lengths):
    """
    Plot the average queue length for each queue with confidence intervals.
    """
    plt.figure()
    avg_lengths = {queue_id: np.mean(lengths) for queue_id, lengths in queue_lengths.items()}
    error_bars = {queue_id: calculate_confidence_interval(lengths)[1] for queue_id, lengths in queue_lengths.items()}
    plt.bar(avg_lengths.keys(), avg_lengths.values(), yerr=error_bars.values(), color='skyblue', edgecolor='black', capsize=5)
    plt.xlabel("Queue ID")
    plt.ylabel("Average Queue Length")
    plt.title("Average Queue Length per Queue with 95% CI")
    plt.show()
