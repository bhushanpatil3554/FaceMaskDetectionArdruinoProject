from pyfirmata import Arduino, SERVO

port ='/dev/cu.usbmodem14201'

pin =10

board = Arduino(port)

board.digital[pin].mode = SERVO

servo_last_state = 0
counter_state_nomask = 0

counter_state_withmask = 0

def rotate_servo(pin, angle):
    board.digital[pin].write(angle)

def open_gate(value):
    global servo_last_state
    global counter_state_nomask,counter_state_withmask
    if value == 0 and servo_last_state == 1:
        if counter_state_nomask == 3:
            counter_state_nomask =0
            servo_last_state = 0
            rotate_servo(pin,180)
        else :
            counter_state_nomask+=1
    elif value ==1 and servo_last_state == 0:
        if counter_state_withmask ==3 :
            counter_state_withmask =0
            rotate_servo(pin,40)
            servo_last_state = 1
        else :
            counter_state_withmask+=1


