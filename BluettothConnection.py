import serial
import time
print("start...")
s = serial.Serial("/dev/tty.HC-05-SerialPort",9600,timeout=4)
s.write(bytes("O",'utf-8'))  #79
time.sleep(5)
s.write(bytes("C",'utf-8'))  #67
time.sleep(5)
s.write(bytes("O",'utf-8'))  #79

time.sleep(5)
s.write(bytes("C",'utf-8'))  #67


