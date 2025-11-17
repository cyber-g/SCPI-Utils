#!/usr/bin/env python3
"""
SCPI Utils - Screenshot Capture Script

Project: https://github.com/cyber-g/SCPI-Utils

Copyright (C) 2025 Germain PHAM <cygerpham@free.fr>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import socket
from datetime import datetime
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description="Capture screenshot from instrument")
parser.add_argument('-i', '--ip', default='192.168.145', help='IP address of the instrument')
parser.add_argument('-p', '--port', type=int, default=5052, help='Port number')
parser.add_argument('-r', '--remote_filename', default=None, help='Remote file name')
parser.add_argument('-l', '--local_filename', default=None, help='Local file name')
args = parser.parse_args()

# Generate timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Set default remote filename if not provided
if args.remote_filename is None:
    args.remote_filename = f"capture_{timestamp}.png"

# Set default local filename if not provided
if args.local_filename is None:
    args.local_filename = args.remote_filename

FF_IP = args.ip
PORT = args.port

# Connect to FieldFox
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((FF_IP, PORT))

# Capture screen on FieldFox
s.sendall(b'MMEM:STOR:IMAG "' + args.remote_filename.encode() + b'"\n')

# Request the file via BINBLOCK
s.sendall(b'MMEM:DATA? "' + args.remote_filename.encode() + b'"\n')

# Read BINBLOCK header '#<digits><length>'
header = s.recv(2)         # first two characters: # and digit count
assert header[0:1] == b'#'
num_digits = int(header[1:2].decode())

length = int(s.recv(num_digits).decode())

# Read the PNG binary data
data = b""
while len(data) < length:
    data += s.recv(length - len(data))

# Save to Linux filesystem
with open(args.local_filename, "wb") as f:
    f.write(data)

print(f"Saved {args.local_filename} ({len(data)} bytes)")

s.close()
