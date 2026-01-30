#!/usr/bin/env python3
import socket
import scpi_helpers as scpih
import time
import argparse

# Defaults (can be overridden via CLI)
INSTRUMENT_IP   = "192.168.1.45"
INSTRUMENT_PORT = 5025

CENTER_FREQ_HZ = 2.39995e9
MAIN_BW_HZ     = 1e6
ADJ_OFFSET_HZ  = 1e6
ADJ_BW_HZ      = 1e6

def parse_args():
    p = argparse.ArgumentParser(description="Measure ACPR on FieldFox via SCPI")
    p.add_argument("-i", "--ip",        dest="ip",          default=INSTRUMENT_IP, help="Instrument IP or hostname")
    p.add_argument("-p", "--port",      dest="port",        type=int, default=INSTRUMENT_PORT, help="Instrument port (TCP)")
    p.add_argument("-c", "--center-freq", dest="center_freq", type=float, default=CENTER_FREQ_HZ, help="Center frequency in Hz")
    p.add_argument("-m", "--main-bw",     dest="main_bw",     type=float, default=MAIN_BW_HZ, help="Main channel bandwidth in Hz")
    p.add_argument("-o", "--adj-offset",  dest="adj_offset",  type=float, default=ADJ_OFFSET_HZ, help="Adjacent channel offset in Hz")
    p.add_argument("-b", "--adj-bw",      dest="adj_bw",      type=float, default=ADJ_BW_HZ, help="Adjacent channel bandwidth in Hz")
    return p.parse_args()

# ------------------
# Setup ACPR
# ------------------

def setup_acpr(sock, center_freq=CENTER_FREQ_HZ, main_bw=MAIN_BW_HZ, adj_offset=ADJ_OFFSET_HZ, adj_bw=ADJ_BW_HZ):
    # Select SA mode
    scpih.send(sock, 'INST:SEL "SA"')
    scpih.query_singleline(sock, "*OPC?")  # wait until mode switch completed

    # Center frequency
    scpih.send(sock, f"SENS:FREQ:CENT {center_freq}")

    # Select ACPR as the channel measurement
    scpih.send(sock, "SENS:MEAS:CHAN ACPR")

    # Main channel integration bandwidth
    scpih.send(sock, f"SENS:CME:IBW {main_bw}")

    # Adjacent channels: ± offset at adj bandwidth
    scpih.send(sock, f"SENS:ACPower:OFFS1:BWID {adj_bw}")
    scpih.send(sock, f"SENS:ACPower:OFFS1:FREQ {adj_offset}")
    scpih.send(sock, "SENS:ACPower:OFFS1:STAT ON")

    # Turn off other offsets
    scpih.send(sock, "SENS:ACPower:OFFS2:STAT OFF")
    scpih.send(sock, "SENS:ACPower:OFFS3:STAT OFF")

    # Use single-sweep mode
    scpih.send(sock, "INIT:CONT 0")
    scpih.query_singleline(sock, "*OPC?")


# ------------------
# Perform 1 ACPR measurement
# ------------------

def measure_acpr(sock):
    # Trigger sweep
    scpih.send(sock, "INIT:IMM")
    scpih.query_singleline(sock, "*OPC?")  # wait until sweep finishes

    # Read ACPR results
    resp = scpih.query_singleline(sock, "CALC:MEAS:DATA?")
    values = [float(v) for v in resp.split(",")]

    if len(values) < 9:
        raise ValueError(f"Unexpected ACPR response: {len(values)} values")

    result = {
        "main_pwr_dBm":              values[0],
        "main_psd_dBm_per_Hz":       values[1],

        "lower_adj_pwr_dBm":         values[3],
        "lower_adj_psd_dBm_per_Hz":  values[4],
        "lower_adj_rel_dBc":         values[5],

        "upper_adj_pwr_dBm":         values[6],
        "upper_adj_psd_dBm_per_Hz":  values[7],
        "upper_adj_rel_dBc":         values[8],
    }

    scpih.send(sock, "INIT:CONT 1")  # restore continuous sweep mode
    scpih.query_singleline(sock, "*OPC?")

    return result


# ------------------
# Main execution
# ------------------

def main():
    args = parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5.0)
    sock.connect((args.ip, args.port))

    try:
        print("Connected to:", scpih.query_singleline(sock, "*IDN?"))

        # Autoscale display
        scpih.autoscale(sock)

        # pause for 1 seconds to allow autoscale to complete
        time.sleep(1)

        # Setup ACPR measurement with CLI parameters
        setup_acpr(sock, center_freq=args.center_freq, main_bw=args.main_bw, adj_offset=args.adj_offset, adj_bw=args.adj_bw)

        # Trigger Measure ACPR
        acpr = measure_acpr(sock)

        print("\n=== ACPR Measurement ===")
        print("Main channel power:      {:.1f} dBm".format(acpr["main_pwr_dBm"]))
        print("Lower adjacent power:    {:.1f} dBm ({:.1f} dBc rel)".format(
            acpr["lower_adj_pwr_dBm"], acpr["lower_adj_rel_dBc"]))
        print("Upper adjacent power:    {:.1f} dBm ({:.1f} dBc rel)".format(
            acpr["upper_adj_pwr_dBm"], acpr["upper_adj_rel_dBc"]))

    finally:
        sock.close()


if __name__ == "__main__":
    main()
