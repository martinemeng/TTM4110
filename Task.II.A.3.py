from matplotlib import pyplot as plt
import simpy
import random
import numpy as np

# Constants and variables
MAX_CAPACITY = 20  # Bus capacity
INTERVAL = 5   # Time between passenger arrivals
TRIP_TIME = 10 # Time for a bus trip
PROB_LEAVE_STOP = 0.3 # Probability of a passenger leaving the bus stop
UTILIZATION = {
    'bus_id1': {'avg_util':[]}
}
print('Hei')

#bus stop 0-6 is the eastbound stops for stop 1-7
#bus stop 10-16 is the westbound stops for stop 1-7
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


# Passenger arrival rate to each stop
#lambda for stop 1 e and west, stop 2 east and west, etc.
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

# Travel times between stops, t1 = travel_times[0] = travel time for R1 etc.
travel_times = [3, 7, 6, 1, 4, 3, 9, 1, 3, 8, 8, 5, 6, 2, 3]


#def choose_route_and_stop():
        # route = random.choice(list(routes.keys()))
        # stop = random.choice(routes[route]['stops'])
        # return route, stop


def passenger_arrival(env, bus_stops):
    
    while True:
        #chooses the bus stop semi-random based on the arrival rates
        bus_stop = random.choices(list(bus_stops.keys()), weights=bus_stops[bus_stop]['arrival_rate'], k=1)[0]

        # Create a new passenger, a single entity
        passenger = simpy.Resource(env, capacity=1, bus_stop=bus_stop)

        # Add the passenger to the list to the designated bus stop
        bus_stops[bus_stop]['passengers'].append(passenger)
        print(f'Passenger generated at {env.now}')

        # Implement the 30% probability for the passenger to leave the bus stop
        if random.random() < PROB_LEAVE_STOP:
            bus_stops[bus_stop]['passengers'].remove(passenger)
            print(f'Passenger left Bus Stop {bus_stop} at {env.now}')

def find_route_with_most_passengers(routes, bus_stops):
    max_passengers = -1
    route_with_max_passengers = None

    for route, data in routes.items():
        total_passengers = sum(len(bus_stops[stop]['passengers']) for stop in data['stops'])
        if total_passengers > max_passengers:
            max_passengers = total_passengers
            route_with_max_passengers = route

    return route_with_max_passengers
#skrive i rapporten at den samme ruten kan bli valgt flere ganger etter hverandre (basert på flest antall ventende passasjerer)


def select_route():
    # Select the route with the highest demand
    selected_route = find_route_with_most_passengers(routes, bus_stops)

    travel_time = 0
    total_travel_time = []
    for road in routes[selected_route]['roads']:
        total_travel_time.append(travel_times[road])
        average_travel_time = np.mean(total_travel_time)
        travel_time += travel_times[road]
    return selected_route, travel_time, average_travel_time

# Simulate bus picking up passengers and traveling between stops along the route
# Bus class
class Bus:
    def __init__(self, env, bus_id, route, max_capacity):
        self.env = env
        self.bus_id = bus_id
        self.route = route
        self.max_capacity = max_capacity
        self.available_seats = max_capacity

    def run(self):
        while True:
            utilizations = []
            for stop in routes[self.route]['stops']:
                print(f'Bus {self.bus_id} arriving at stop {stop} at {self.env.now}')

                picked_up = 0
                taken_seats = self.max_capacity - self.available_seats
                leaves = random.randint(0, taken_seats)
                self.available_seats += leaves

                # Drop off passengers
                print(f'{leaves} passengers dropped off at stop {stop} at {self.env.now}')

                # Pick up passengers
                while bus_stops[stop]['passengers'] and picked_up < self.available_seats:
                    bus_stops[stop]['passengers'].pop(0)
                    picked_up += 1
                    self.available_seats -= 1
                    print(f'Passenger picked up at stop {stop} by Bus {self.bus_id} at {self.env.now}')

                # Drive to the next stop
                travel_time = random.choice(routes[self.route]['roads'])
                yield self.env.timeout(travel_time)
                print(f'Bus {self.bus_id} trip completed at {self.env.now}')
                utilizations.append(taken_seats / self.max_capacity)
                avg_utilization = np.mean(utilizations)
                UTILIZATION['bus_id1']['avg_util'].append(avg_utilization)
                


# Create and start buses
env = simpy.Environment()
buses = []
bus_counts = [5, 7, 10, 15]

for i in range(bus_counts[0]):
    route, _, time = select_route()
    bus = Bus(env, i, route, MAX_CAPACITY)
    buses.append(bus)
    env.process(bus.run()) 


def run_simulation(nb):
    passengers = []
    env.process(passenger_arrival(env, bus_stops))
    env.run(until=800)
    return len(passengers)

# Run the simulation for different nb values and calculate average utilization and standard error
nb_values = [5, 7, 10, 15]
num_runs = 15
averages = []
standard_errors = []

# for nb in nb_values:
#     util = 0
#     for bus_id in UTILIZATION:
#         util += UTILIZATION[bus_id]['avg_util'][0]
#     avg_utilization = np.mean(util) # Calculate the average utilization
#     std_error = np.std(UTILIZATION) / np.sqrt(num_runs) # Calculate the standard error
#     averages.append(avg_utilization)
#     standard_errors.append(std_error)

# Plot the results with error bars
# plt.errorbar(nb_values, averages, yerr=standard_errors, fmt='o', capsize=5, label='Average Utilization')
# plt.xlabel('nb values')
# plt.ylabel('Average Utilization')
# plt.title('Average Utilization with Standard Error')
# plt.legend()
# plt.show()