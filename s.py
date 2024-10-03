import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Constants
MAX_CAPACITY = 20  # Bus capacity
INTERVAL = 1  # Time between passenger arrivals
TRIP_TIME = 10  # Time for a bus trip
PROB_LEAVE_STOP = 0.3  # Probability of a passenger leaving the bus stop
RUN_TIME = 50  # Total simulation run time

# Passenger arrival rates (no change)
arrival_rate_stop = [0.3, 0.6, 0.1, 0.1, 0.3, 0.9, 0.2, 0.5, 0.6, 0.4, 0.6, 0.4, 0.6, 0.4]

# Travel times between stops (no change)
travel_times = [3, 7, 6, 1, 4, 3, 9, 1, 3, 8, 8, 5, 6, 2, 3]


UTILIZATION = {}

#TODO: KAN endre routers -> ROUTES og bus_stops -> BUS_STOPS


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


# Passenger arrival process
def passenger_arrival(env, bus_stops):
    while True:
        bus_stop = random.choices(
            list(bus_stops.keys()),
            weights=[bus_stops[stop]['arrival_rate'] for stop in bus_stops],
            k=1)[0]
        passenger = {'bus_stop': bus_stop}
        bus_stops[bus_stop]['passengers'].append(passenger)
        print(f'Passenger generated at time {env.now} at stop {bus_stop}. Total at stop: {len(bus_stops[bus_stop]["passengers"])}')
        yield env.timeout(INTERVAL)
        if random.random() < PROB_LEAVE_STOP and passenger in bus_stops[bus_stop]['passengers']:
            bus_stops[bus_stop]['passengers'].remove(passenger)
            print(f'Passenger left Bus Stop {bus_stop} at time {env.now}. Total at stop: {len(bus_stops[bus_stop]["passengers"])}')

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
        self.passengers = []

    def run(self):
        utilizations = []
        selected_route = routes[self.route]['roads']
        while True:
            counter = 0
            yield self.env.timeout(travel_times[selected_route[counter]])
            for stop in routes[self.route]['stops']:
                # Drop off passengers
                leaves = random.randint(0, (MAX_CAPACITY-self.available_seats))  # Random passengers leavin
                self.available_seats += leaves
                print(f'{leaves} Passenger dropped off at stop {stop+1} by Bus {self.bus_id} at {self.env.now}')

                # Pick up passengers
                picked_up = 0
                while bus_stops[stop]['passengers'] and picked_up < self.available_seats:
                    bus_stops[stop]['passengers'].pop(0)
                    picked_up += 1
                    self.available_seats -= 1
                    print(f'Passenger picked up at stop {stop} by Bus {self.bus_id} at {self.env.now}')

                # Utilization
                utilizations.append((MAX_CAPACITY-self.available_seats) / self.max_capacity)
                avg_utilization = np.mean(utilizations)
                UTILIZATION[self.bus_id] = {'avg_util': avg_utilization}
                #print(f'Average utilization for Bus {self.bus_id}: {avg_utilization:.2f}')
                yield self.env.timeout(travel_times[selected_route[counter]])



###########delt opp run_simulation() i to funksjoner
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
            print("BUS ID: ", bus.bus_id)
            prev_routes.append(assigned_route)  # Mark the route as assigned
            env.process(bus.run())
        

    # for i in range(number_of_buses):
    #     current_routes = sorted_routes_with_most_passengers(routes, bus_stops)
    #     for route in current_routes:
    #         if route not in prev_routes:
    #             print(route)
    #             print("prev", prev_routes)
    #             bus = Bus(env, f'bus_id{i}', route, MAX_CAPACITY)
    #         prev_routes.append(route)
    #     env.process(bus.run())

def run_simulation(number_of_buses):
    env = simpy.Environment()
    env.process(passenger_arrival(env, bus_stops))
    env.process(simulation_process(env, number_of_buses))  # Create a separate process
    env.run(until=RUN_TIME)

#######



# Function to run simulation
# def run_simulation(number_of_buses):
#     env = simpy.Environment()
#     env.process(passenger_arrival(env, bus_stops))
#     prev_routes = []

#     yield env.timeout(10)
#     for i in range(number_of_buses):
#         current_routes = sorted_routes_with_most_passengers(routes, bus_stops)
#         for route in current_routes:
#             if route not in prev_routes:
#                 print(route)
#                 print("prev", prev_routes)
#                 bus = Bus(env, f'bus_id{i}', route, MAX_CAPACITY)
#             prev_routes.append(route)
#         env.process(bus.run())
#     env.run(until=RUN_TIME)
    

# Run multiple simulations for each bus count
def util_run_simulation():
    repetitions = 15  # Number of repetitions
    bus_numbers = [5, 7, 10, 15]
    utilizations_mean = []
    utilizations_std_err = []

    for nb in bus_numbers:
        avg_util_per_run = []

        for _ in range(repetitions):
            for i in list(bus_stops.keys()):
                bus_stops[i]['passengers'].clear()
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
