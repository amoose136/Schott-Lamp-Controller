import argparse
import serial
import time

begin = time.time()

def range_limited_int(arg: int):
    """make sure the int is in 0 to 1000 range without making argparse ugly as sin"""
    min_val=0
    max_val=1000
    try:
        i = int(arg)
    except ValueError:
        raise argparse.ArgumentTypeError("Must be a integar input")
    if i < min_val or i > max_val:
        raise argparse.ArgumentTypeError("Brightness must be < " + str(max_val) + " and > " + str(min_val))
    return i

parser = argparse.ArgumentParser(description='Set the brightness of a connected Schott Lamp.')
parser.add_argument(
    '--brightness',
    dest='brightness', 
    metavar="N where N is [0-1000]",
    type=range_limited_int,
    help='The brightness of the lamp from 0 to 1000'
)
parser.add_argument(
    '--start',
    dest='start',
    metavar='M (seconds)',
    type=int,
    default=0,
    help='Number of seconds from call time to when the brightness command is sent'
)
parser.add_argument(
    '--stop',
    dest='stop',
    metavar='M (seconds)',
    type=int,
    help='Number of seconds from call time to when the off command is sent'
)
args = parser.parse_args()
with serial.Serial() as ser:
    ser.baudrate = 9600 #From Schott Manual, do not change
    ser.port = 'COM3' #this could change and will need an function to select the right com port later
    ser.parity = serial.PARITY_NONE #From Schott Manual, do not change
    ser.stopbits = serial.STOPBITS_ONE #From Schott Manual, do not change
    ser.xonxoff=False
    ser.write_timeout=0 # Not known if we need to set a timeout yet (val in seconds)
    ser.open()
    msg='0BR'+hex(args.brightness)[2:].zfill(4)+";" #[id][BRightness][0 for padding the number][the brightness as a hexadecimal with the '0x' in front chopped off]
    msg=msg.encode()
    print(msg)
    time.sleep(args.start)
    # lock
    msg0 = '0LK0001;'
    msg0 = msg0.encode('utf-8')
    ser.write(msg0)
    time.sleep(.02) #20ms delay
    ser.write(msg)
    if args.stop is not None:
        time.sleep(args.stop-args.start)
    msg = '0BR0000;'
    msg = msg.encode('utf-8')
    ser.write(msg)
    # unlock
    msg0 = '0LK0000;'
    msg0 = msg0.encode('utf-8')
    ser.write(msg0)

end=time.time()
# print(f"Executed in {end-begin}")