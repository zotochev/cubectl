def create_nginx_config(services_by_port: dict[int, str]):
    upstreams = []
    locations = []
    rewrites = []

    for port in services_by_port.keys():

        for svc in services_by_port[port]:
            upstreams.append(f'upstream {svc} {{ ip_hash; server localhost:{port} max_fails=3  fail_timeout=600s; }}')

            locations.append(f'location /api/v3/{svc} {{ resolver 8.8.8.8; proxy_pass http://{svc};   '
                             f'proxy_redirect off; proxy_set_header Host $host; '
                             f'proxy_set_header X-Real-IP $remote_addr; proxy_set_header X-Forwarded-For '
                             f'$remote_addr; }}')
            rewrites.append(f'rewrite ^/api/v3/{svc}/(.*)$ /api/v3/{svc}/$1 break;')

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
