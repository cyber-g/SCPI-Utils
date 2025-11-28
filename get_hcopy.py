#!/usr/bin/env python3
"""
SCPI Utils - HCopy Screenshot Capture (HCOPy:EXEC)

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
import scpi_helpers as scpih

# Parse command line arguments
parser = argparse.ArgumentParser(description="Capture screenshot from instrument")
parser.add_argument('-i', '--ip', default='c2s-smbv', help='IP address of the instrument')
parser.add_argument('-p', '--port', type=int, default=5025, help='Port number')
parser.add_argument('-l', '--local_filename', default=None, help='Local file name')
args = parser.parse_args()

# Generate timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Set default local filename if not provided
if args.local_filename is None:
    args.local_filename = f"capture_{timestamp}.png"

FF_IP = args.ip
PORT = args.port

# Connect to Instrument
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((FF_IP, PORT))

# Set image format to PNG
scpih.send(sock, 'HCOPy:IMAGe:FORMat PNG')
# Set region to FULL
scpih.send(sock, 'HCOPy:REGion FULL')
# Execute the capture
scpih.send(sock, 'HCOPy:EXECute')

# Read the PNG binary data
data = scpih.query_binblock(sock, 'HCOPy:DATA?')

# Save to Linux filesystem
with open(args.local_filename, "wb") as f:
    f.write(data)
print(f"Saved {args.local_filename} ({len(data)} bytes)")


sock.close()
