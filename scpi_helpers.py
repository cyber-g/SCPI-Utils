"""
scpi_helpers.py — SCPI socket helper utilities

SCPI-Utils: a collection of small, focused utilities for interacting with
SCPI-compliant instruments over TCP/IP. This module provides minimal, helper
functions for sending SCPI commands and receiving ASCII or IEEE 488.2
binary-block responses.

Project: https://github.com/cyber-g/SCPI-Utils
Author: Germain PHAM <cygerpham@free.fr>
Copyright (C) 2025 Germain PHAM
License: GNU General Public License v3.0

Notes:
- These helpers are intentionally small and synchronous. For production
  or high-reliability use, add explicit timeouts, retries and robust
  error handling as needed.
- Binary block parsing follows the IEEE 488.2 '#<N><length>' convention.
(https://fr.mathworks.com/matlabcentral/answers/1598789-what-is-the-data-format-used-by-readbinblock-and-writebinblock-functions-in-instrument-control-toolb)

"""

# ------------------
# SCPI helpers
# ------------------

def send(sock, cmd):
    """Send SCPI command (no response)."""
    if not cmd.endswith("\n"):
        cmd += "\n"
    sock.sendall(cmd.encode("ascii"))

def query_singleline(sock, cmd):
    """Send SCPI query and return the ASCII response (single line)."""
    if not cmd.endswith("\n"):
        cmd += "\n"
    sock.sendall(cmd.encode("ascii"))

    data = b""
    while b"\n" not in data:
        chunk = sock.recv(4096)
        if not chunk:
            raise IOError("Socket closed while waiting for response")
        data += chunk

    line, _, _ = data.partition(b"\n")
    return line.decode("ascii").strip()

def query_binblock(sock, cmd):
    """Send SCPI query and return the binary response (BINBLOCK)."""
    if not cmd.endswith("\n"):
        cmd += "\n"
    sock.sendall(cmd.encode("ascii"))

    # Read BINBLOCK header '#<digits><length>'
    header = sock.recv(2)   # first two characters: # and digit count
    assert header[0:1] == b'#'
    num_digits = int(header[1:2].decode())
    length = int(sock.recv(num_digits).decode())

    # Read the binary data
    data = b""
    while len(data) < length:
        data += sock.recv(length - len(data))

    return data

def autoscale(sock):
    """Send autoscale command."""
    send(sock, "DISPlay:WINDow:TRACe1:Y:SCALe:AUTO")
    query_singleline(sock, "*OPC?")  # wait until complete