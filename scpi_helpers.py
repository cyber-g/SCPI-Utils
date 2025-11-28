# ------------------
# Low-level helpers
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