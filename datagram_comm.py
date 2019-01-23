#written by Shota Nemoto
#based off code written by jcjones
#https://gist.github.com/jcjones/0f3f11a785a833e0a216

import socket
import struct
import sys
import time
import selectors
import parse_bytes

#constants
TARG_PORT = 33434
BUFFER_SIZE = 1500
TTL = 30
SOCK_TIMEOUT = 1000 #in milliseconds
MESSAGE = "Measurement for class project. Questions to student srn24@case.edu"
ICMP = socket.getprotobyname('icmp')
UDP = socket.getprotobyname('udp')
IP_ICMP_HEADER_LEN = 28

#indexes in the sites_list
SITE_NAME = 0
SITE_IP = 1
RTT = 2
PACKET = 3


def send_to(send_socket, destination):
	"""Sends a payload with the given id to the destination via the given socket.
	
	:param send_socket: the socket to send with
	:param destination: where to send to
	:param id: used to distinguish packets
	:return TARG_IP, send_time: the ip it was sent to and the timestamp the packet was sent at
	"""
	TARG_IP = socket.gethostbyname(destination)
	#create payload to send
	#ID_MSG = "{0:0>3}".format(id) + ":" + MESSAGE
	payload = bytes(MESSAGE + 'a'*(1472 - len(MESSAGE)), 'ascii')

	send_time = None
	try:
		#send message
		send_socket.sendto(payload, (TARG_IP, TARG_PORT))
		send_time = time.time()
		print("Message sent to " + destination + " at " + str(TARG_IP))
		
		return TARG_IP, send_time
		
	except socket.error as msg:
		print('Error sending message to ' + str(TARG_IP))
	
	return None #if sockets could not be set up or packet was not received correctly
	
	
def send_datagrams(sites):
	"""
	sends datagrams to the sites in the given list at once from
	a single datagram socket. Returns a list of a list of relevant info to
	a site
	"""
	sites_list = list()
	send_sock = None
	
	try:
		#sending datagram socket
		send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, UDP) #create socket to send datagram
		send_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, TTL) #set TTL
	except socket.error as msg:
		print('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		
	#send the datagrams
	for site_name in sites:
		site_ip, send_time = send_to(send_sock, site_name)
		if send_time is not None:
			site_info = [site_name, site_ip, send_time, None, 0, 0]
			sites_list.append(site_info)
		
	send_sock.close()
	return sites_list
		
def receive_datagrams(recv_sock, sites_list):
	"""
	Uses the given raw socket to receive ICMP messages. Only receives them
	if they are in the list of sites that have been sent a datagram.
	"""
	#for select calls to check if the socket has a message ready
	poller = selectors.DefaultSelector()
	poller.register(recv_sock, selectors.EVENT_READ)
	
	#runs until all responses have been received or the select call times out
	messages = 0
	max_number = len(sites_list)
	while (messages < max_number):
		events = poller.select(3) #set the timeout to 3 seconds
		
		#if there is something to read from the socket
		if len(events) is not 0:
			icmp_packet, addr = recv_sock.recvfrom(BUFFER_SIZE)
			#I realize that this RTT may not be the most accurate for large numbers of sites
			#but I did not have the time to change my implementation to get a more accurate number
			recv_time = time.time() 
			messages += 1
			
			#to match this icmp packet with the site in the list
			dest_ip = parse_bytes.parse_dest_ip(icmp_packet)
			print("Recieved Message from: " + dest_ip)
			
			#match the packet with the correct site in the list
			index = -1
			for i, site in enumerate(sites_list):
				if dest_ip in site:
					index = i
			if index is not -1:
				sites_list[index][PACKET] = icmp_packet
				sites_list[index][RTT] = recv_time - sites_list[index][RTT]
		else:
			break;
			
	return sites_list
			
