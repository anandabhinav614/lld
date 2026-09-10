# 192.168.0.0 → 192.168.1.255 = 192.168.0.0/23
# each block no can go from 0 to 256 so 23 means all 23 bits are fix, left is only 9 
# coz 23+9 =32
# ipv4 is 32 bit
# from              to
# 192.168.0.10     # 192.168.0.100
# 192|168|0|10     # 192|168|0|100

# number = first × 256³ + second × 256² + third × 256 + fourth

def ip_to_int(ip:str):
    parts = ip.split('.')
    return (int(parts[0])*256**3+
            int(parts[1])*256**2+
            int(parts[2])*256+
            int(parts[3]))

def ip_to_cidr(st_ip, end_ip):
    st = ip_to_int(st_ip)
    ed = ip_to_int(end_ip)

def main():
    ips = [("192.168.0.0")]