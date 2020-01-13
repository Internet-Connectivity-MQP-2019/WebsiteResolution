from DigForPy.dig import run_dig
import sys
import geoip2.database
from itertools import product

geoip = geoip2.database.Reader('GeoIP2-City.mmdb')


def geolocate_ip(ip):
    try:
        response = geoip.city(ip)
        country = response.country.name
        state = None
        if response.subdivisions is not None and response.subdivisions.most_specific is not None:
            state = response.subdivisions.most_specific.name
        latitude = response.location.latitude
        longitude = response.location.longitude
        return (country, state, latitude, longitude)
    except geoip2.errors.AddressNotFoundError:
        return (None, None, None, None)



def run_lookup(recursive_ip, target_domain):
    result = run_dig(domain = target_domain, target_server = recursive_ip)

    if result is None:
        return

    recursive_country, recursive_state, recursive_latitude, recursive_longitude = geolocate_ip(recursive_ip)
    count = 0
    for answer in result.answer_section:
       if answer.record_type == "A" or answer.record_type == "AAAA":
            count += 1
            ip = answer.ip 
            uid = "{},{}".format(recursive_ip, ip)
            domain_country, domain_state, domain_latitude, domain_longitude = geolocate_ip(ip)
            
            print("{uid},recursive,{domain},{ip},{country},{state},{latitude},{longitude},ANSWER".format(ip=ip,uid=uid,domain=target_domain,country=recursive_country,state=recursive_state,latitude=recursive_latitude,longitude=recursive_longitude))
            print("{uid},authoritative,{domain},{ip},{country},{state},{latitude},{longitude},ANSWER".format(ip=ip,uid=uid,domain=target_domain,country=domain_country,state=domain_state,latitude=domain_latitude,longitude=domain_longitude))

    for answer in result.additional_section:
       if answer.record_type == "A" or answer.record_type == "AAAA":
            count += 1
            ip = answer.ip 
            uid = "{},{}".format(recursive_ip, ip)
            domain_country, domain_state, domain_latitude, domain_longitude = geolocate_ip(ip)
            
            print("{uid},recursive,{domain},{ip},{country},{state},{latitude},{longitude},ADDITIONAL".format(ip=ip,uid=uid,domain=target_domain,country=recursive_country,state=recursive_state,latitude=recursive_latitude,longitude=recursive_longitude))
            print("{uid},authoritative,{domain},{ip},{country},{state},{latitude},{longitude},ADDITIONAL".format(ip=ip,uid=uid,domain=target_domain,country=domain_country,state=domain_state,latitude=domain_latitude,longitude=domain_longitude))
   

recursive_ips = []
with open('recursive_confirmed.csv') as f:
    i = 0
    for line in f:
        if i == 0:
            i += 1
            continue
        recursive_ips.append(line.rstrip())

target_domains = []
with open('sitelist.csv') as f:
    i = 0
    for line in f:
        if i == 0:
            i += 1
            continue
        target_domains.append(line.rstrip().split(",")[1])


pairs = list(product(target_domains, recursive_ips))
print("recursive_ip,target_domain,auth_ip,recursive?,domain,country,state,latitude,longitude,section")
for target_domain,recursive_ip in pairs:
   run_lookup(recursive_ip, target_domain) 
