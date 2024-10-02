import simpy
import numpy as np
import matplotlib.pyplot as plt

# Define the parameters
MAX_CAPACITY = 20  # Bus capacity
INTERVAL = 5       # Time between passenger arrivals
TRIP_TIME = 10     # Time for a bus trip
PROB_LEAVE_STOP = 0.3  # Probability of a passenger leaving the bus stop

routes = {
    'Route_13': {'stops': [0, 3, 5], 'roads': [0, 4, 7, 12]},
    'Route_14': {'stops': [1, 4, 6], 'roads': [2, 6, 10, 14]},
    'Route_23': {'stops': [1, 4, 5], 'roads': [2, 6, 8, 12]},
    'Route_24': {'stops': [2, 3, 6], 'roads': [3, 5, 9, 14]},
    'Route_31': {'stops': [5, 3, 0], 'roads': [12, 7, 4, 0]},
    'Route_41': {'stops': [6, 4, 1], 'roads': [14, 10, 6, 2]},
    'Route_32': {'stops': [5, 4, 1], 'roads': [12, 8, 6, 2]},
    'Route_42': {'stops': [6, 3, 2], 'roads': [14, 9, 7, 3]}
}

travel_times = [3, 7, 6, 1, 4, 3, 9, 1, 3, 8, 8, 5, 6, 2, 3]
arrival_rate_stop = [0.3, 0.6, 0.1, 0.1, 0.3, 0.9, 0.2, 0.5, 0.6, 0.4, 0.6, 0.4, 0.6, 0.4]

# Passenger arrival process
def passenger_arrival(env, bus_stop, arrival_rate):
    for time in arrival_rate:
        yield env.timeout(time)
        bus_stop.put(1)

# Bus service process
def bus_service(env, bus_stop, nb):
    while True:
        for _ in range(nb):
            yield env.timeout(1)
            if not bus_stop.items:
                break
            bus_stop.get(1)

# Simulation function
def simulate_bus_utilization(env, nb, arrival_rate):
    bus_stop = simpy.Store(env, capacity=MAX_CAPACITY)
    env.process(passenger_arrival(env, bus_stop, arrival_rate))
    env.process(bus_service(env, bus_stop, nb))
    yield env.timeout(60)  # Run the simulation for 60 minutes
    utilization = len(bus_stop.items) / (nb * 60)
    return utilization

# Run the simulation for different numbers of buses
def run_simulation(nb, arrival_rate, runs=15):
    utilizations = []
    for _ in range(runs):
        env = simpy.Environment()
        utilization = env.run(until=simulate_bus_utilization(env, nb, arrival_rate))
        utilizations.append(utilization)
    return np.mean(utilizations), np.std(utilizations) / np.sqrt(runs)

# Number of buses to simulate
bus_numbers = [5, 7, 10, 15]

# Collect results
results = [run_simulation(nb, arrival_rate_stop) for nb in bus_numbers]

# Extract average utilizations and standard errors
avg_utilizations = [result[0] for result in results]
std_errors = [result[1] for result in results]

# Plot the results with error bars
plt.errorbar(bus_numbers, avg_utilizations, yerr=std_errors, fmt='o', capsize=5)
plt.xlabel('Number of Buses')
plt.ylabel('Average Utilization')
plt.title('Bus Utilization vs Number of Buses')
plt.grid(True)
plt.show()
