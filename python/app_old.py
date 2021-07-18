from serial import Serial
from time import sleep

from pyautogui import hotkey

def next():
    hotkey('n')

def previous():
    hotkey('p')

def nothing():
    pass

def main(port):
    print('Initing...')
    commands = {'Encendido': next, 'Encendido 2': previous}
    sleep(2)
    with Serial(port=port, baudrate=9600, timeout=0.05) as arduino:
        print('Processing...')
        while(True):
            command = arduino.readline()
            command = command.decode().rstrip()
            if command != '':
                print(command)
                action = commands.get(command, nothing)
                action()


if __name__ == "__main__":
    PORT = 'COM4'
    main(PORT)
