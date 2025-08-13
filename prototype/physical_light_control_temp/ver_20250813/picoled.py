#!/usr/bin/env python3
import serial
import serial.tools.list_ports
import sys
import time


def find_pico():
    """Find any serial port that might be the Pico"""
    ports = serial.tools.list_ports.comports()
    
    # Try Pico vendor ID first
    for port in ports:
        if port.vid == 0x2E8A:
            return port.device
    
    # Try common ports
    import glob
    for pattern in ['/dev/ttyACM*', '/dev/tty.usbmodem*', '/dev/cu.usbmodem*']:
        ports = glob.glob(pattern)
        if ports:
            return ports[0]
    
    return None

def send_color_luminosity(color, luminosity):
    port = find_pico()
    if not port:
        print("No Pico found!")
        return
    
    print(f"Sending color={color}, luminosity={luminosity} to {port}")
    
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(1)
        
        # Send color and luminosity separated by comma + newline
        data = f"{color},{luminosity}\n"
        ser.write(data.encode())
        ser.flush()
        
        print(f"Sent: color={color}, luminosity={luminosity}")
        ser.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 picoled.py <color> <luminosity>")
        print("  color: integer (0-n for different PWM pins)")
        print("  luminosity: integer (0-65535 for PWM duty cycle)")
        sys.exit(1)
    
    try:
        color = int(sys.argv[1])
        luminosity = int(sys.argv[2])
        
        # Validate luminosity range
        if luminosity < 0 or luminosity > 65535:
            print("Luminosity must be between 0 and 65535")
            sys.exit(1)

        # Validate colour range
        if color < 0 or color > 3:
            print("Colour must be between 0 and 3")
            sys.exit(1)
            
        send_color_luminosity(color, luminosity)
        
    except ValueError:
        print("Please provide valid integers for color and luminosity")
