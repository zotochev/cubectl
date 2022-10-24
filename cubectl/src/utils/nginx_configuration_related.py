import os

from src.utils import read_yaml


def check_if_launched_as_root():
    return os.geteuid() == 0


def check_service_names_for_duplicates(ports_allocated_by_app: dict):
    """
    ports_allocated_by_app = {
        'enegan': {'service_0': 9308, 'service_1': 9309},
        'not_enegan': {'service_2': 9304, 'service_3': 9305}
    }
    """
    services_names = []
    services_app_names = dict()

    for app_name, services_ports in ports_allocated_by_app.items():
        services_names.extend(services_ports.keys())
        services_app_names[app_name] = list(services_ports.keys())

    if len(services_names) != len(set(services_names)):
        raise Exception(
            f'cubectl: setup-nginx: configuration has duplicated service names: '
            f'{services_app_names}'
        )


def get_next_port(ports_allocated_by_app: dict) -> int:
    ports = []

    for app_ports in ports_allocated_by_app.values():
        if app_ports:
            ports.extend(app_ports)
    if ports:
        return max(ports)


def get_all_allocated_ports_by_app(register: dict):
    ports_by_app = dict()

    for app_name in register.keys():
        try:
            status = read_yaml(register[app_name]['status_file'])
        except FileNotFoundError:
            continue
        services = status.get('services', [])
        # ports = []
        ports = dict()
        for service in services:
            service_data = service['service_data']
            service_name = service['init_config']['name']
            if not service_data:
                continue
            # ports.append(service_data['port'])
            ports[service_name] = service_data['port']
        ports_by_app[app_name] = ports
    return ports_by_app


def create_nginx_config(services_by_port: dict[int, str]):
    upstreams = []
    locations = []
    rewrites = []

    for port in services_by_port.keys():

        for svc in services_by_port[port]:
            upstreams.append(f'upstream {svc} {{ ip_hash; server localhost:{port} max_fails=3  fail_timeout=600s; }}')

            locations.append(' ' * 4 + f'location /api/v3/{svc} {{ resolver 8.8.8.8; proxy_pass http://{svc};   '
                             f'proxy_redirect off; proxy_set_header Host $host; '
                             f'proxy_set_header X-Real-IP $remote_addr; proxy_set_header X-Forwarded-For '
                             f'$remote_addr; }}')
            rewrites.append(' ' * 4 + f'rewrite ^/api/v3/{svc}/(.*)$ /api/v3/{svc}/$1 break;')

    upstreams = '\n'.join(upstreams)
    locations = '\n'.join(locations)
    rewrites = '\n'.join(rewrites)

    nginx = f'''{upstreams}

server {{

    listen 80 default_server;
    listen [::]:80 default_server;

    root /tmp;
    index index.html;

    server_name _;

    client_max_body_size 100M;
    proxy_connect_timeout       600;
    proxy_send_timeout          600;
    proxy_read_timeout          600;
    send_timeout                600;

{locations}
    proxy_buffering off;

{rewrites}

    rewrite ^/(.*)$ /$1 break;
}}'''

    return nginx
