#!/usr/bin/env python3
import struct
import hashlib
from collections import defaultdict, Counter

def parse_pcap():
    packets = []
    with open('/home/engine/project/tcpdump.pcap', 'rb') as f:
        f.read(24)
        
        while True:
            header = f.read(16)
            if len(header) < 16:
                break
                
            ts_sec, ts_usec, incl_len, orig_len = struct.unpack('<IIII', header)
            packet_data = f.read(incl_len)
            
            if len(packet_data) < incl_len:
                break
            
            if len(packet_data) >= 44:
                ip_header = packet_data[16:36]
                src_ip = ip_header[12:16]
                src_ip_str = '.'.join(str(b) for b in src_ip)
                payload = packet_data[44:]
                
                if len(payload) > 0:
                    packets.append((src_ip_str, payload))
    
    return packets

packets = parse_pcap()

by_ip = defaultdict(list)
for src_ip, payload in packets:
    by_ip[src_ip].append(payload)

# Get most common payload for each worker and extract last 2 bytes
print("Last 2 bytes of most common payloads:")
flag_parts = []
for i in range(1, 33):
    ip = f"12.34.56.{i}"
    payloads = by_ip[ip]
    counter = Counter(payloads)
    most_common = counter.most_common(1)[0][0]
    last_2 = most_common[-2:]
    flag_parts.append(last_2.hex())
    print(f"Worker {i:2d}: {last_2.hex()}")

# Try as flag
flag_inner = ''.join(flag_parts)
flag = f"DH{{{flag_inner}}}"
flag_md5 = hashlib.md5(flag.encode()).hexdigest()

print(f"\nFlag: {flag}")
print(f"Flag MD5: {flag_md5}")

with open('/home/engine/project/flag_hint.txt', 'r') as f:
    hint = f.read().strip()
print(f"Hint MD5: {hint}")
print(f"Match: {flag_md5 == hint}")
