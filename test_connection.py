import socket
import sys

s = socket.socket()
result = s.connect_ex(('localhost', 8000))
if result == 0:
    print('Port 8000 is open - Server is running!')
    sys.exit(0)
else:
    print('Port 8000 is closed - Server is NOT running')
    sys.exit(1)
