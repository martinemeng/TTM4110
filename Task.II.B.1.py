import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Constants
MAX_CAPACITY = 20  # Bus capacity
TRIP_TIME = 10  # Time for a bus trip
RUN_TIME = 60*24  # Total simulation run time

UTILIZATION = {}
TRAVEL_TIMES = []

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

# Passenger arrival rates
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
    13: {'passengers': [], 'arrival_rate': arrival_rate_stop[10]},
    14: {'passengers': [], 'arrival_rate': arrival_rate_stop[11]},
    15: {'passengers': [], 'arrival_rate': arrival_rate_stop[12]},
    16: {'passengers': [], 'arrival_rate': arrival_rate_stop[13]}
}

# all the buses
# bus_id1: {'passengers': [passenger1, passenger2,...] }
buses = {
}

# Passenger arrival rates
arrival_rate_stop = []
for i in range (0, 14):
    arrival_rate_stop.append(0.9)
print(arrival_rate_stop)


# Travel times between stops
travel_times = [3, 7, 6, 1, 4, 3, 9, 1, 3, 8, 8, 5, 6, 2, 3]

# Passenger class
class Passenger:
    def __init__(self, env, bus_stop, end_stop, route):
        self.env = env
        self.bus_stop = bus_stop
        self.end_stop = end_stop
        self.arrival_time = env.now
        self.end_time = None
        self.route = route
    
    def leave_bus(self):
        self.end_time = self.env.now
        total_travel_time = self.end_time - self.arrival_time
        TRAVEL_TIMES.append(total_travel_time)
        return total_travel_time
    
def find_route_with_stops(bus_stop, end_stop, routes):
        for route_name, route_info in routes.items():
            if bus_stop in route_info['stops'] and end_stop in route_info['stops']:
                return route_name
        return route_name


def passenger_arrival(env, bus_stops):
    for bus_stop in bus_stops.keys():
        env.process(generate_passengers(env, bus_stop, bus_stops[bus_stop]['arrival_rate']))

# Passenger arrival process
def generate_passengers(env, bus_stop, arrival_rate):
    while True:

        # Inter-arrival time follows an exponential distribution
        inter_arrival_time = random.expovariate(arrival_rate)
        yield env.timeout(inter_arrival_time)
    
        
        # Find a valid end stop on the same route
        valid_end_stops = []
        for route in routes.values():
            if bus_stop in route['stops']:
                index = route['stops'].index(bus_stop)
                for stop in route['stops'][index:]:
                    valid_end_stops.append(stop)
        valid_end_stops = list(set(valid_end_stops))  # Remove duplicates
        valid_end_stops.remove(bus_stop)  # Remove the starting stop from the list

        if valid_end_stops:
            end_stop = random.choice(valid_end_stops)
            route123 = find_route_with_stops(bus_stop, end_stop, routes)
            passenger = Passenger(env, bus_stop, end_stop=end_stop, route=route123)
            print("passenger ROUTE: ", passenger.route)
            print("passenger end stop: ", passenger.end_stop)
            bus_stops[bus_stop]['passengers'].append(passenger)
            #passengers.append(passenger)
            print(f'Passenger generated at {env.now}. At bus Stop {bus_stop} to {end_stop}')
    
# Find route with most passengers
def sorted_routes_with_most_passengers(routes, bus_stops):
    # Initialize the list to store passenger counts for each route
    route_passenger_counts = []

    # Iterate over routes and count passengers
    for route_name, route_info in routes.items():
        total_passengers = 0
        for stop in route_info['stops']:
            total_passengers += len(bus_stops[stop]['passengers'])
        route_passenger_counts.append((route_name, total_passengers))

    # Sort the list of routes by the number of passengers in descending order
    route_passenger_counts.sort(key=lambda x: x[1], reverse=True)

    # Remove the passenger counts, keeping only the route names
    sorted_route_names = [route_name for route_name, _ in route_passenger_counts]

    
    return sorted_route_names

# Bus class to simulate each bus
class Bus:
    def __init__(self, env, bus_id, route, max_capacity):
        self.env = env
        self.bus_id = bus_id
        self.route = route
        self.max_capacity = max_capacity
        self.available_seats = max_capacity

    def run(self):
        utilizations = []
        while True:
            route = routes[self.route]['roads']
            counter = 0
            yield self.env.timeout(travel_times[route[counter]])

            for stop in routes[self.route]['stops']:
                picked_up = 0
                # Picks up passengers
                for passenger in bus_stops[stop]['passengers']:
                    
                    # Goes on the bus
                    if passenger.route == self.route:
                        if bus_stops[stop]['passengers'] and picked_up < self.available_seats:
                            #passengers.remove(passenger) må fjerne fra dict 
                            self.available_seats -= 1
                            picked_up += 1
                            buses[self.bus_id]['passengers'].append(passenger)
                            #TRAVEL_TIMES.append(passenger.leave_bus())
                            passenger_index = bus_stops[stop]['passengers'].index(passenger)
                            bus_stops[stop]['passengers'].pop(passenger_index)
                print(f'Passenger picked up at stop {stop} by Bus {self.bus_id} at {self.env.now}')
                

            # Drop off passengers
            leaves = 0
            for passenger in buses[self.bus_id]['passengers']:
                passenger_index = buses[self.bus_id]['passengers'].index(passenger)
                if stop == buses[self.bus_id]['passengers'][passenger_index].end_stop:
                    buses[self.bus_id]['passengers'].pop(passenger_index)
                    self.available_seats += 1
                    leaves += 1
                    TRAVEL_TIMES.append(passenger.leave_bus())
            print(f'{leaves} passengers dropped off at stop {stop} at {self.env.now}')
            

            # Utilization
            print(f'Available seats: {(MAX_CAPACITY - self.available_seats)}')
            utilizations.append((MAX_CAPACITY - self.available_seats) / self.max_capacity)
            avg_utilization = np.mean(utilizations)
            UTILIZATION[self.bus_id] = {'avg_util': avg_utilization}
            yield self.env.timeout(travel_times[route[counter]])
            print(f'Bus {self.bus_id} trip completed at {self.env.now}')
    
def simulation_process(env, number_of_buses):
    prev_routes = []
    yield env.timeout(10)  # Introducing the timeout here

    for i in range(number_of_buses):
        current_routes = sorted_routes_with_most_passengers(routes, bus_stops)

        if (current_routes == prev_routes):  # If all routes have been assigned
                prev_routes = []  # Reset the assigned routes
        
        # Find the next available route that has not been assigned
        assigned_route = None
        for route in current_routes:
            if route not in prev_routes:  # Check if route hasn't been assigned
                assigned_route = route
                break
        
        if assigned_route:  # If we found an unassigned route
            print(f"Bus {i} assigned to route {assigned_route}")
            bus = Bus(env, f'bus_id{i}', assigned_route, MAX_CAPACITY)
            buses[f'bus_id{i}'] = {'passengers': []}
            print("BUS ID: ", bus.bus_id)
            prev_routes.append(assigned_route)  # Mark the route as assigned
            env.process(bus.run())

def run_simulation(number_of_buses):
    env = simpy.Environment()
    passenger_arrival(env, bus_stops)
    env.process(simulation_process(env, number_of_buses))  # Create a separate process
    env.run(until=RUN_TIME)


def util_run_simulation():
    repetitions = 15  # Number of repetitions
    bus_numbers = [5, 7, 10, 15]
    utilizations_mean = []
    utilizations_std_err = []
    travel_utilizations_mean = []
    travel_utilizations_std_err = []

    for nb in bus_numbers:
        avg_util_per_run = []

        for _ in range(repetitions):
            for i in list(bus_stops.keys()):
                bus_stops[i]['passengers'].clear()
            UTILIZATION.clear()  # Reset utilization
            TRAVEL_TIMES.clear()
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
        print(utilizations_std_err)

        # Standard error and average of the travel times
        util_travel_time = np.mean(TRAVEL_TIMES)
        std_travel_time = np.std(TRAVEL_TIMES) / np.sqrt(len(TRAVEL_TIMES))
        travel_utilizations_mean.append(util_travel_time)
        travel_utilizations_std_err.append(std_travel_time)
        print("Utilization mean: ", utilizations_mean)
        print("Utilization standard error: ",  utilizations_std_err)
        
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
