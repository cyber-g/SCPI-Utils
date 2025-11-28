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

def autoscale(sock):
    """Send autoscale command."""
    send(sock, "DISPlay:WINDow:TRACe1:Y:SCALe:AUTO")
    query_singleline(sock, "*OPC?")  # wait until complete