import signal

def sleep_terminal(signum, frame):
    print('teste')

while True:
    signal.signal(signal.SIGINT, sleep_terminal)