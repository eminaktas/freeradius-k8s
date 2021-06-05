import socket

from netaddr import IPNetwork


def get_service_ip(hostname: str) -> str:
    return str(socket.gethostbyname(hostname))


def get_cidr_from_iface(host: str) -> str:
    return str(IPNetwork(host).cidr)
