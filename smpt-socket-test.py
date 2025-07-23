import socket
sock = socket.socket()
sock.settimeout(10)
sock.connect(("smtp.gmail.com", 465))
print("✅ Connected")
