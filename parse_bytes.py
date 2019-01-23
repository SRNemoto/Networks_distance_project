import struct

TTL = 30

def parse_hops(icmp_packet):
	"""
	Checks the time to live field of the IP header in the 
	ICMP payload. Subtracts original time to live to find 
	number of hops
	"""
	hops = TTL - struct.unpack("!B", icmp_packet[36:37])[0] + 1 #hops from OG datagram + 1
	return hops
	
def parse_dest_ip(icmp_packet):
	"""
	Finds the original destination from the IP header in the 
	ICMP payload. Returns as a string
	"""
	byte1, byte2, byte3, byte4 = struct.unpack("!BBBB", icmp_packet[44:48]) #destination i
	dest_ip = "{0}.{1}.{2}.{3}".format(byte1, byte2, byte3, byte4)
	return dest_ip
	
def parse_payload_bytes(icmp_packet):
	"""
	Finds the number of bytes in the ICMP payload
	"""
	IP_ICMP_HEADER_LEN = 28
	payload_bytes = struct.unpack("!H", icmp_packet[2:4])[0] - IP_ICMP_HEADER_LEN #length of OG datagram contained
	return payload_bytes
	
def parse_UDP_checksum(icmp_packet):
	"""
	Finds the UDP checksum in the ICMP payload
	Not used.
	"""
	checksum = struct.unpack("!I", icmp_packet[54:56])[0]
	return checksum
	
def parse_info(icmp_packet):
	"""
	Parses the number of hops and bytes in the payload
	"""
	hops = parse_hops(icmp_packet)
	payload_bytes = parse_payload_bytes(icmp_packet)
	return hops, payload_bytes