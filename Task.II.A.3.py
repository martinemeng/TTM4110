from matplotlib import pyplot as plt
import simpy
import random
import numpy as np

# Constants
MAX_CAPACITY = 20  # Bus capacity
INTERVAL = 5   # Time between passenger arrivals
TRIP_TIME = 10 # Time for a bus trip
PROB_LEAVE_STOP = 0.3 # Probability of a passenger leaving the bus stop


routes = {
    'Route_13': {
        'stops': [0, 3, 5],
        'roads': [0, 4, 7, 12]
    },
    'Route_14': {
        'stops': [1, 4, 6],
        'roads': [2, 6, 10, 14]
    },
    'Route_23': {
        'stops': [1, 4, 5],
        'roads': [2, 6, 8, 12]
    },
    'Route_24': {
        'stops': [2, 3, 6],
        'roads': [3, 5, 9, 14]
    },
    'Route_31': {
        'stops': [5, 3, 0],
        'roads': [12, 7, 4, 0]
    },
    'Route_41': {
        'stops': [6, 4, 1],
        'roads': [14, 10, 6, 2]
    },
    'Route_32': {
        'stops': [5, 4, 1],
        'roads': [12, 8, 6, 2]
    },
    'Route_42': {
        'stops': [6, 3, 2],
        'roads': [14, 9, 7, 3]
    }
}

# Travel times between stops, t1 = travel_times[0] = travel time for R1 etc.
travel_times = [3, 7, 6, 1, 4, 3, 9, 1, 3, 8, 8, 5, 6, 2, 3]

# Passenger arrival rate to each stop
#lambda for stop 1 e and west, stop 2 east and west, etc.
arrival_rate_stop = [0.3, 0.6, 0.1, 0.1, 0.3, 0.9, 0.2, 0.5, 0.6, 0.4, 0.6, 0.4, 0.6, 0.4]

#def choose_route_and_stop():
        # route = random.choice(list(routes.keys()))
        # stop = random.choice(routes[route]['stops'])
        # return route, stop

def passenger_generator(env, passengers):
    #route, stop = choose_route_and_stop()
    
    while True:        
        # Time between each new passenger
        yield env.timeout(random.expovariate(1.0 / INTERVAL))

        # Create a new passenger, a single entity
        passenger = simpy.Resource(env, capacity=1)

        # Add the passenger to the list
        passengers.append(passenger)
        print(f'Passenger generated at {env.now}')


def select_route():
    # Select a random route
    selected_route = random.choice(list(routes.keys()))
    travel_time = 0
    for road in routes[selected_route]['roads']:
        travel_time += travel_times[road]
    return selected_route, travel_time

# Simulate bus picking up passengers and traveling between stops along the route
def bus(env, passengers, nb):
    available_seats = MAX_CAPACITY
    bus_counts = [5, 7, 10, 15]
    counter = 0 
    
    while counter != bus_counts[0]: 
        counter += 1
        selected_route, travel_time = select_route()
        
    #Pick up and drop off passengers
        for stop in routes[selected_route]['stops']:
            print(stop)
            print(f'Bus arriving at {env.now}')

            picked_up = 0
            taken_seats = MAX_CAPACITY - available_seats
            leaves = random.randint(0,taken_seats)
            available_seats += leaves

            # Drop off passengers
            print(f'{leaves} passengers dropped off at {env.now}')

            # While there are passengers and there is still space in the bus
            while passengers and picked_up <= available_seats:
                # Remove the first passenger from the list (is picked up)
                passengers.pop(0)
                picked_up += 1
                available_seats -= 1
                print(f'Passenger picked up at {env.now} by Bus {selected_route}')

            # Drive to the next stop
        yield env.timeout(travel_time)
        print(f'Bus trip completed at {env.now}')

def run_simulation(nb):
    env = simpy.Environment()
    passengers = []
    env.process(passenger_generator(env, passengers))
    env.process(bus(env, passengers, nb))
    env.run(until=800)
    return len(passengers)

# Run the simulation for different nb values and calculate average utilization and standard error
nb_values = [5, 7, 10, 15]
num_runs = 15
averages = []
standard_errors = []

for nb in nb_values:
    utilizations = [run_simulation(nb) for _ in range(num_runs)] # Calculate the utilization for each run, by dividing the number of passengers by the bus capacity
    avg_utilization = np.mean(utilizations) # Calculate the average utilization
    std_error = np.std(utilizations) / np.sqrt(num_runs) # Calculate the standard error
    averages.append(avg_utilization)
    standard_errors.append(std_error)

# Plot the results with error bars
plt.errorbar(nb_values, averages, yerr=standard_errors, fmt='o', capsize=5, label='Average Utilization')
plt.xlabel('nb values')
plt.ylabel('Average Utilization')
plt.title('Average Utilization with Standard Error')
plt.legend()
plt.show()