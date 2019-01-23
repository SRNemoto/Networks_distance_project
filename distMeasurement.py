import datagram_comm
import parse_bytes
import socket

#constants
TARG_PORT = 33434
ICMP = socket.getprotobyname('icmp')

#indexes in the sites_list's inner lists
SITE_NAME = 0
SITE_IP = 1
RTT = 2
PACKET = 3
HOPS = 4
PAYLOAD_BYTES = 5

def main():
	"""
	requires the 'sudo' argument when run
	"""
	sites = get_sites('sites.txt', 30)
	
	recv_sock = make_recv_socket()
	sites_list = datagram_comm.send_datagrams(sites)
	
	for site_info in sites_list:
		site_ip = site_info[SITE_IP]
		send_time = site_info[RTT]
		print("sent to " + site_ip + " at " + str(send_time))
		
	sites_list = datagram_comm.receive_datagrams(recv_sock, sites_list)
	sites_list = extract_info(sites_list)
	read_list(sites_list)
		
	
def make_recv_socket():
	"""
	binds the raw socket to receive messages even while messages
	are still being sent
	"""
	raw_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP)
	raw_sock.bind(('', TARG_PORT)) #binds to host's ip and port
	raw_sock.setblocking(False)
	return raw_sock
	
def get_sites(filename, num):
	"""
	Reads a certain number of site names from the text file
	"""
	textfile = open(filename)
	sites = ["" for i in range(num)]
	for j in range(len(sites)):
		sites[j] = textfile.readline().replace('\n', '')
	return sites
		
def extract_info(sites_list):
	"""
	Extracts the hops and number of bytes in the payload_bytes
	from sites that returned a ICMP packet.
	"""
	for site_info in sites_list:
		if site_info[PACKET] is not None:
			hops, payload_bytes = parse_bytes.parse_info(site_info[PACKET])
			site_info[HOPS] = hops
			site_info[PAYLOAD_BYTES] = payload_bytes
			print("Parsed bytes for " + site_info[SITE_IP])
		else:
			site_info[HOPS] = "No Response"
			site_info[PAYLOAD_BYTES] = "No Response"
			site_info[RTT] = "No response"
	return sites_list
	
def read_list(sites_list):
	"""
	Reads the relevant info in the list of relevant site information
	"""
	for site_info in sites_list:
		print("Website: " + site_info[SITE_NAME])
		print("    IP: " + str(site_info[SITE_IP]))
		if site_info[PACKET] is not None:
			print("    RTT: " + str(site_info[RTT]))
			print("    Hops: " + str(site_info[HOPS]))
			print("    Payload Bytes: " + str(site_info[PAYLOAD_BYTES]))
		else:
			print("    " + site_info[RTT])
		print("")

if __name__ == '__main__':
	"""
	requires the 'sudo' argument when run
	"""
	main()