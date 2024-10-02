import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

#FORBEDRET KODE AV CHAT 

# Constants
MAX_CAPACITY = 20  # Bus capacity
INTERVAL = 0.5  # Time between passenger arrivals
TRIP_TIME = 10  # Time for a bus trip
PROB_LEAVE_STOP = 0.3  # Probability of a passenger leaving the bus stop
RUN_TIME = 500  # Total simulation run time

UTILIZATION = {
    #'bus_id1': {'avg_util': []}
}

# Define bus routes
routes = {
    'Route_13': {'stops': [0, 3, 5], 'roads': [0, 4, 7, 12]},
    'Route_14': {'stops': [1, 4, 6], 'roads': [2, 6, 10, 14]},
    'Route_23': {'stops': [1, 4, 5], 'roads': [2, 6, 8, 12]},
    'Route_24': {'stops': [2, 3, 6], 'roads': [3, 5, 9, 14]},
    'Route_31': {'stops': [15, 13, 10], 'roads': [12, 7, 4, 0]},
    'Route_41': {'stops': [16, 14, 11], 'roads': [14, 10, 6, 2]},
    'Route_32': {'stops': [15, 14, 11], 'roads': [12, 8, 6, 2]},
    'Route_42': {'stops': [16, 13, 12], 'roads': [14, 9, 7, 3]}
}



# Passenger arrival rates (no change)
arrival_rate_stop = [0.3, 0.6, 0.1, 0.1, 0.3, 0.9, 0.2, 0.5, 0.6, 0.4, 0.6, 0.4, 0.6, 0.4]
bus_stops = {
    0: {'passengers': [], 'arrival_rate': arrival_rate_stop[0]},
    1: {'passengers': [], 'arrival_rate': arrival_rate_stop[1]},
    2: {'passengers': [], 'arrival_rate': arrival_rate_stop[2]},
    3: {'passengers': [], 'arrival_rate': arrival_rate_stop[3]},
    4: {'passengers': [], 'arrival_rate': arrival_rate_stop[4]},
    5: {'passengers': [], 'arrival_rate': arrival_rate_stop[5]},
    6: {'passengers': [], 'arrival_rate': arrival_rate_stop[6]},
    
    10: {'passengers': [], 'arrival_rate': arrival_rate_stop[7]},
    11: {'passengers': [], 'arrival_rate': arrival_rate_stop[8]},
    12: {'passengers': [], 'arrival_rate': arrival_rate_stop[9]},
    13 : {'passengers': [], 'arrival_rate': arrival_rate_stop[10]},
    14 : {'passengers': [], 'arrival_rate': arrival_rate_stop[11]},
    15 : {'passengers': [], 'arrival_rate': arrival_rate_stop[12]},
    16 : {'passengers': [], 'arrival_rate': arrival_rate_stop[13]}
}
# Travel times between stops (no change)
travel_times = [3, 7, 6, 1, 4, 3, 9, 1, 3, 8, 8, 5, 6, 2, 3]

# Passenger arrival process (no change)
def passenger_arrival(env, bus_stops):
    while True:
        bus_stop = random.choices(
            list(bus_stops.keys()),
            weights=[bus_stops[stop]['arrival_rate'] for stop in bus_stops],
            k=1)[0]
        passenger = {'bus_stop': bus_stop}
        bus_stops[bus_stop]['passengers'].append(passenger)
        yield env.timeout(INTERVAL)
        if random.random() < PROB_LEAVE_STOP and passenger in bus_stops[bus_stop]['passengers']:
            bus_stops[bus_stop]['passengers'].remove(passenger)

# Find route with most passengers (no change)
def find_route_with_most_passengers(routes, bus_stops):
    max_passengers = -1
    route_with_max_passengers = None
    for route, data in routes.items():
        total_passengers = sum(len(bus_stops[stop]['passengers']) for stop in data['stops'] if stop in bus_stops)
        if total_passengers > max_passengers:
            max_passengers = total_passengers
            route_with_max_passengers = route
    return route_with_max_passengers

# Select route (no change)
def select_route():
    selected_route = find_route_with_most_passengers(routes, bus_stops)
    return selected_route

# Bus class to simulate each bus
class Bus:
    def __init__(self, env, bus_id, route, max_capacity):
        self.env = env
        self.bus_id = bus_id
        self.route = route
        self.max_capacity = max_capacity
        self.available_seats = max_capacity
        self.passengers = []

    def run(self):
        utilizations = []
        while True:
            route = routes[self.route]['roads']
            counter = 0
            yield self.env.timeout(travel_times[route[counter]])
            for stop in routes[self.route]['stops']:
                # Drop off passengers
                taken_seats = self.max_capacity - self.available_seats
                leaves = random.randint(0, taken_seats)  # Random passengers leaving
                taken_seats -= leaves
                self.available_seats += leaves

                # Pick up passengers
                picked_up = 0
                while bus_stops[stop]['passengers'] and picked_up < self.available_seats:
                    bus_stops[stop]['passengers'].pop(0)
                    picked_up += 1
                    self.available_seats -= 1
                    taken_seats += 1

                # Utilization
                utilizations.append(taken_seats / self.max_capacity)
                avg_utilization = np.mean(utilizations)
                UTILIZATION[self.bus_id] = {'avg_util': avg_utilization}
                yield self.env.timeout(travel_times[route[counter]])

# Function to run simulation
def run_simulation(number_of_buses):
    env = simpy.Environment()
    env.process(passenger_arrival(env, bus_stops))
    for i in range(number_of_buses):
        route = select_route()
        bus = Bus(env, f'bus_id{i}', route, MAX_CAPACITY)
        env.process(bus.run())
    env.run(until=RUN_TIME)

# Run multiple simulations for each bus count
def util_run_simulation():
    repetitions = 15  # Number of repetitions
    bus_numbers = [5, 7, 10, 15]
    utilizations_mean = []
    utilizations_std_err = []

    for nb in bus_numbers:
        avg_util_per_run = []

        for _ in range(repetitions):
            UTILIZATION.clear()  # Reset utilization
            run_simulation(nb)

            # Collect utilization for all buses
            avg_utilizations = [UTILIZATION[key]['avg_util'] for key in UTILIZATION.keys()]
            avg_util_per_run.append(np.mean(avg_utilizations))

        # Calculate average and standard error
        avg_util = np.mean(avg_util_per_run)
        std_err = np.std(avg_util_per_run) / np.sqrt(repetitions)
        utilizations_mean.append(avg_util)
        utilizations_std_err.append(std_err)
    print(utilizations_mean)

    # Plotting
    plt.errorbar(bus_numbers, utilizations_mean, yerr=utilizations_std_err, fmt='o', capsize=5, label='Avg Utilization')
    plt.xlabel('Number of Buses')
    plt.ylabel('Average Utilization')
    plt.title('Bus Utilization vs Number of Buses')
    plt.grid(True)
    plt.legend()
    plt.show()

    return utilizations_mean, utilizations_std_err

util_run_simulation()
