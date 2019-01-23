import urllib.request
import geoip2.database
import distMeasurement
import socket
from math import radians, sin, cos, sqrt, asin

SITE_IP = 1

def haversine(lat1, lon1, lat2, lon2):
	"""
	From https://rosettacode.org/wiki/Haversine_formula#Python
	for calculating distance between two coordinate locations
	"""
	R = 6372.8 # Earth radius in kilometers

	dLat = radians(lat2 - lat1)
	dLon = radians(lon2 - lon1)
	lat1 = radians(lat1)
	lat2 = radians(lat2)

	a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
	c = 2*asin(sqrt(a))

	return R * c

def main():
	#to get my machine's public ip
	with urllib.request.urlopen('http://checkip.amazonaws.com') as response:
		html = response.read()

	my_ip = str(html)
	for char in my_ip:
		if char in "b'n\\":
			my_ip = my_ip.replace(char,'')

	#Get my machine's city and coordinates
	reader = geoip2.database.Reader('GeoLite2-City.mmdb')
	print("My IP: %s" % my_ip)
	my_info = reader.city(my_ip)
	my_lat = my_info.location.latitude
	my_lon = my_info.location.longitude
	print("    My City: %s" % my_info.city.name)
	print("    My latitude: %s" % my_lat)
	print("    My longitude: %s\n" % my_lon)
	
	#get a case machine's city and coordiantes
	case_ip = '129.22.12.21'
	response = reader.city(case_ip)
	cle_lat = response.location.latitude
	cle_lon = response.location.longitude
	print("\nCase IP %s City: %s" % (case_ip, response.city.name))
	print("    Cleveland latitude: %s" % cle_lat)
	print("    Cleveland longitude: %s\n" % cle_lon)
	

	#runs through the list of 30 sites, gets their 
	#IP, city, coordiantes, direct distance, and indirect distance
	sites_list = distMeasurement.get_sites('sites.txt', 30)
	for site in sites_list:
		site_ip = socket.gethostbyname(site)
		site_response = reader.city(site_ip)
		site_lat = site_response.location.latitude
		site_lon = site_response.location.longitude
		print(site)
		print("    Site IP: %s" % site_ip)
		print("    Site city: %s" % site_response.city.name)
		print("    Site latitude: %s" % site_lat)
		print("    Site longitude: %s" % site_lon)
		my_distance = haversine(site_lat, site_lon, my_lat, my_lon)
		print("    Site distance from me: %s" % my_distance)
		cle_distance = haversine(site_lat, site_lon, cle_lat, cle_lon)
		print("    Site distance from Cleveland/CWRU: %s\n" % cle_distance)

if __name__ == '__main__':
	main()

