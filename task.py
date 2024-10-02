import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Constants and variables
MAX_CAPACITY = 20  # Bus capacity
INTERVAL = 0.5        # Time between passenger arrivals
TRIP_TIME = 10      # Time for a bus trip
PROB_LEAVE_STOP = 0.3  # Probability of a passenger leaving the bus stop
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

# Passenger arrival rates for each stop
#bus stop 0-6 is the eastbound stops for stop 1-7
#bus stop 10-16 is the westbound stops for stop 1-7
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

# Travel times between stops
travel_times = [3, 7, 6, 1, 4, 3, 9, 1, 3, 8, 8, 5, 6, 2, 3]

def passenger_arrival(env, bus_stops):
    while True:
        # Choose bus stop based on arrival rates
        bus_stop = random.choices(
            list(bus_stops.keys()),
            weights=[bus_stops[stop]['arrival_rate'] for stop in bus_stops],
            k=1)[0]

        # Create a passenger object
        passenger = {'bus_stop': bus_stop}
        bus_stops[bus_stop]['passengers'].append(passenger)
        print(f'Passenger generated at time {env.now} at stop {bus_stop}. Total at stop: {len(bus_stops[bus_stop]["passengers"])}')
        
        yield env.timeout(INTERVAL)  # Wait for the next passenger arrival

        # Check if the passenger leaves
        if random.random() < PROB_LEAVE_STOP:
            if passenger in bus_stops[bus_stop]['passengers']:
                bus_stops[bus_stop]['passengers'].remove(passenger)
                print(f'Passenger left Bus Stop {bus_stop} at time {env.now}. Total at stop: {len(bus_stops[bus_stop]["passengers"])}')


def find_route_with_most_passengers(routes, bus_stops):
    max_passengers = -1
    route_with_max_passengers = None

    for route, data in routes.items():
        total_passengers = sum(len(bus_stops[stop]['passengers']) for stop in data['stops'] if stop in bus_stops)
        if total_passengers > max_passengers:
            max_passengers = total_passengers
            route_with_max_passengers = route

    return route_with_max_passengers

def select_route():
    # Select the route with the highest demand
    selected_route = find_route_with_most_passengers(routes, bus_stops)
    travel_time = 0

    # Calculate travel time for the selected route
    for road in routes[selected_route]['roads']:
        travel_time += travel_times[road]

    return selected_route, travel_time

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
            bus_route, time = select_route()
            route = routes[bus_route]['roads']
            print(route)
            counter = 0
            yield self.env.timeout(travel_times[route[counter]])
            for stop in routes[self.route]['stops']:
                print(f'Bus {self.bus_id} arriving at stop {stop+1} at {self.env.now}, travel time: {travel_times[route[counter]]} on road: {route[counter]}')
                counter += 1
                yield self.env.timeout(travel_times[route[counter]])
                # Drop off passengers
                taken_seats = self.max_capacity - self.available_seats
                leaves = random.randint(0, taken_seats)  # Random number of passengers leaving
                # Remove passengers from the bus
                taken_seats -= leaves
                self.available_seats += leaves
                print(f'{leaves} Passenger dropped off at stop {stop+1} by Bus {self.bus_id} at {self.env.now}')
    
                # Pick up passengers
                picked_up = 0
                while bus_stops[stop]['passengers'] and picked_up < self.available_seats:
                    bus_stops[stop]['passengers'].pop(0)  # Remove the first passenger in the list
                    picked_up += 1
                    taken_seats += 1
                    self.available_seats -= 1
                    print(f'Passenger picked up at stop {stop} by Bus {self.bus_id} at {self.env.now}')
                    

                # Calculate utilization
                utilizations.append(taken_seats / self.max_capacity)
                avg_utilization = np.mean(utilizations)
                UTILIZATION[self.bus_id] = {'avg_util': avg_utilization}
                print(f'Average utilization for Bus {self.bus_id}: {avg_utilization:.2f}')

                # Drive to the next stop
                # TODO: fikse at den ser på hvilket stop den skal til for å sjekke kjøretid
                travel_time = random.choice(routes[self.route]['roads'])  # Get a random travel time for the next road
                yield self.env.timeout(travel_time)

# Function to run the simulation
def run_simulation():
    env = simpy.Environment()
    env.process(passenger_arrival(env, bus_stops))

    number_of_buses = [5, 7, 10, 15]

    # Start buses
    for num in number_of_buses:
        for i in range(num):
            route, _= select_route()
            bus = Bus(env, f'bus_id{i}', route, MAX_CAPACITY)
            env.process(bus.run())

    # Run the simulation for a set time
    env.run(until=50)

# Run the simulation
run_simulation()

utilizations_per_bus_count = []
bus_numbers = [5, 7, 10, 15]
total_utilizations_mean = []

for num_buses in bus_numbers:
    run_simulation()
    print(UTILIZATION.values())
    for key in list(UTILIZATION.keys())[:num_buses]:
        utilizations_per_bus_count.append(UTILIZATION[key]['avg_util'])
    util_mean_per_bus_count = np.mean(utilizations_per_bus_count)
    util_std_per_bus_count = np.std(utilizations_per_bus_count) / np.sqrt(len(utilizations_per_bus_count))
    total_utilizations_mean.append(util_mean_per_bus_count)
    utilizations_per_bus_count.clear()
    print(total_utilizations_mean)



#std_errs = [np.std(util) / np.sqrt(int(util)) for util in utilizations_per_bus_count if util]
#print(len(means), len(bus_numbers))

# Plot the results
plt.errorbar(bus_numbers, total_utilizations_mean, yerr=util_std_per_bus_count, fmt='o', capsize=5, capthick=2, marker='s', markersize=5, label='Avg Utilization')
plt.xlabel('Number of Buses')
plt.ylabel('Average Utilization')
plt.title('Average Bus Utilization vs Number of Buses')
plt.grid(True)
plt.legend()
plt.show()
