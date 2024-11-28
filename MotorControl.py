import board
import digitalio
import pwmio
import time

# Define encoder pins
encoderA_left = digitalio.DigitalInOut(board.A1)
encoderA_left.direction = digitalio.Direction.INPUT
encoderA_left.pull = digitalio.Pull.UP

encoderB_left = digitalio.DigitalInOut(board.A2)
encoderB_left.direction = digitalio.Direction.INPUT
encoderB_left.pull = digitalio.Pull.UP

encoderA_right = digitalio.DigitalInOut(board.D5)
encoderA_right.direction = digitalio.Direction.INPUT
encoderA_right.pull = digitalio.Pull.UP

encoderB_right = digitalio.DigitalInOut(board.D6)
encoderB_right.direction = digitalio.Direction.INPUT
encoderB_right.pull = digitalio.Pull.UP

# Motor PWM Pins (for speed control)
motor1_pwm = pwmio.PWMOut(board.A4, duty_cycle=0)  # M1 PWM Pin
motor2_pwm = pwmio.PWMOut(board.D4, duty_cycle=0)  # M2 PWM Pin

# Motor DIR Pins (for direction control)
motor1_dir = digitalio.DigitalInOut(board.A3)  # M1 DIR Pin
motor1_dir.direction = digitalio.Direction.OUTPUT

motor2_dir = digitalio.DigitalInOut(board.D3)  # M2 DIR Pin
motor2_dir.direction = digitalio.Direction.OUTPUT


# Variables to track encoder counts
count_left = 0
count_right = 0

# Motor speed (max value)
motor_speed = 65535  # Full speed (adjust as needed)

# Previous states for encoder readings
last_state_left = encoderA_left.value
last_state_right = encoderA_right.value

def update_encoder_counts():
    global count_left, count_right, last_state_left, last_state_right

    # Left encoder
    current_state_left = encoderA_left.value
    if current_state_left != last_state_left:  # Detect edge
        if encoderB_left.value != current_state_left:
            count_left += 1  # Forward
        else:
            count_left -= 1  # Backward
    last_state_left = current_state_left

    # Right encoder
    current_state_right = encoderA_right.value
    if current_state_right != last_state_right:  # Detect edge
        if encoderB_right.value != current_state_right:
            count_right += 1  # Forward
        else:
            count_right -= 1  # Backward
    last_state_right = current_state_right

def control_motors(motorNum, speed, dir):
    # Adjust motor speed based on encoder counts or any logic
    if motorNum is 'A':
        if dir is True:  # Example condition to adjust left motor speed
            motor1_pwm.duty_cycle = speed
            motor1_dir.value = True  # Forward direction (True for forward)
        elif dir is False:
            motor1_pwm.duty_cycle = speed  # Stop motor
            motor1_dir.value = False  # Reverse direction (False for reverse)
        else:
            motor1_pwm.duty_cycle = 0
    if motorNum is 'B':
        if dir is True:  # Example condition to adjust right motor speed
            motor2_pwm.duty_cycle = speed
            motor2_dir.value = True  # Forward direction (True for forward)
        elif dir is False:
            motor2_pwm.duty_cycle = speed  # Stop motor
            motor2_dir.value = False  # Reverse direction (False for reverse)
        else:
            motor2_pwm.duty_cycle = 0

while True:
    update_encoder_counts()
    control_motors('A', motor_speed, True)  # Adjust motors based on encoder counts
    control_motors('B', motor_speed, False)
    print(f"Left Count: {count_left}, Right Count: {count_right}")
    time.sleep(0.01)