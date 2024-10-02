import random



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



bus_stop = random.choices( 
            list(bus_stops.keys()),  # List of all bus stop keys
            weights=[bus_stops[stop]['arrival_rate'] for stop in bus_stops],  # Corresponding weights (arrival rates) for each bus stop
            k=1  # Pick one bus stop
)[0] # Extract the chosen stop

print(bus_stop)