import board
import digitalio
import time

# Define sensor pins
sensor_pins = [
    board.A5, board.A6,
    board.A7, board.D8,
    board.D9, board.D10
]

white_val = 500
black_val = 2000

normArray = []

# Define emitter control pins
ctrl_even = digitalio.DigitalInOut(board.D12)
ctrl_even.direction = digitalio.Direction.OUTPUT

# State Machine Definitions
STATE_START = 0
STATE_SERPENTINE = 1
STATE_STRAIGHTAWAY = 2
STATE_TURNS = 3
STATE_FORK = 4
STATE_FINISH = 5

end_of_stage = False
state_index = 0
state_list = [
    STATE_START, STATE_SERPENTINE, STATE_STRAIGHTAWAY,
    STATE_TURNS, STATE_FORK, STATE_TURNS,
    STATE_STRAIGHTAWAY, STATE_SERPENTINE, STATE_FINISH
]
debug = False


# Create sensor objects
sensors = [digitalio.DigitalInOut(pin) for pin in sensor_pins]
for sensor in sensors:
    sensor.switch_to_output(value=False)  # Start with output low

def normalizeSensorValues(sensor_values):
    #Set reference values for white and black surfaces
    white_val = 500
    black_val = 2000

    #Normalize each sensor value to a range of 0 to 1
    normalized_values = []
    for val in sensor_values:
        normalized_value = (val - white_val) / (black_val - white_val)
        normalized_value = max(0.0, min(1.0, normalized_value))
        normalized_values.append(normalized_value)
    return normalized_values

def computeError(sensor_values):
    """Compute the error for line following based on sensor readings

    Parameters:
        sensor_values (list of float): Normalized sensor readings from the reflectance array.

    Returns:
        tuple: Contains the calculated error, a boolean indicating if all sensors detect black,
               a boolean indicating if all sensors detect white, and the normalized sensor values.
    """
    # Normalize sensor values to ensure consistency
    sensor_values = normalizeSensorValues(sensor_values)

    # Define weights for each sensor to compute the error
    weights = [-3, -2, -1, 1, 2, 3]
    error = sum(weight * value for weight, value in zip(weights, sensor_values))

    # Determine if all sensors detect black or white
    black_threshold = 0.7  # Threshold for detecting black
    white_threshold = 0.3  # Threshold for detecting white

    all_black = all(value >= black_threshold for value in sensor_values)
    all_white = all(value <= white_threshold for value in sensor_values)

    return error, all_black, all_white, sensor_values


def read_sensors():
    # Step 1: Turn on IR emitters
    ctrl_even.value = True

    # Step 2: Set sensor pins as outputs and drive high
    for sensor in sensors:
        sensor.switch_to_output(value=True)
    time.sleep(0.00001)  # Allow at least 10 Î¼s for the sensors to charge

    # Step 3: Set sensor pins to input (high impedance)
    for sensor in sensors:
        sensor.switch_to_input(pull=None)

    # Step 4: Measure decay time
    start_time = time.monotonic_ns()
    decay_times = [0] * len(sensors)
    while True:
        all_done = True
        for i, sensor in enumerate(sensors):
            if decay_times[i] == 0 and not sensor.value:  # Check if pin has gone low
                decay_times[i] = time.monotonic_ns() - start_time
            if decay_times[i] == 0:
                all_done = False
        if all_done:
            break

    # Turn off IR emitters
    ctrl_even.value = False

    # Convert decay times to microseconds
    decay_times = [time_ns / 1000 for time_ns in decay_times]
    return decay_times



while True:
    # Read and print sensor values
    sensor_values = read_sensors()
    #normArray.append(normalizeSensorValues(sensor_values))
    print("Sensor values (us):", sensor_values)
    #print("Sensor value array (us):", normArray)
    time.sleep(0.5)