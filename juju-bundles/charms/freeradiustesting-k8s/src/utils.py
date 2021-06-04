import netifaces
import socket

from netaddr import IPNetwork


def get_local_ipv4_networks():
    networks = []
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            ipv4_addr = addresses[netifaces.AF_INET][0]
            network = IPNetwork(
                '{addr}/{netmask}'.format(
                    addr=ipv4_addr["addr"],
                    netmask=ipv4_addr["netmask"]
                )
            )
            networks.append(network)
    return networks


def get_network_from_iface(host: str) -> str:
    target_network = IPNetwork(host)
    networks = get_local_ipv4_networks()
    for network in networks:
        if network.ip in target_network:
            return str(network.cidr)


def get_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)
