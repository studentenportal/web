upstream app_server {
    server studentenportal:8000 fail_timeout=0;
}

server {
    listen 8000;
    server_name www.studentenportal.ch studentenportal.ch;

    location /.well-known/acme-challenge {
      alias /var/www/dehydrated;
    }

    rewrite ^/(.*) https://studentenportal.ch/$1 permanent;
}

server {
    listen 8443 ssl http2;
    server_name www.studentenportal.ch;
    ssl_certificate /etc/dehydrated/certs/studentenportal.ch/fullchain.pem;
    ssl_certificate_key /etc/dehydrated/certs/studentenportal.ch/privkey.pem;

    rewrite ^/(.*) https://studentenportal.ch/$1 permanent;
}

server {
    listen 8443 ssl http2;
    server_name studentenportal.ch;

    ssl_certificate /etc/dehydrated/certs/studentenportal.ch/fullchain.pem;
    ssl_certificate_key /etc/dehydrated/certs/studentenportal.ch/privkey.pem;

    # HSTS (ngx_http_headers_module is required) (15768000 seconds = 6 months)
    add_header Strict-Transport-Security max-age=15768000;

    # OCSP Stapling ---
    # fetch OCSP records from URL in ssl_certificate and cache them
    ssl_stapling on;
    ssl_stapling_verify on;

    ## verify chain of trust of OCSP response using Root CA and Intermediate certs
    ssl_trusted_certificate /etc/dehydrated/certs/studentenportal.ch/fullchain.pem;

    # If DNS-resolution for OCSP is required, ask this host:
#    resolver 81.92.97.18;

    access_log /var/log/nginx/studentenportal.access.log;
    error_log /var/log/nginx/studentenportal.error.log info;

    keepalive_timeout 5;

    # support up to ~20MB uploads
    client_max_body_size 20M;

    # path for static files
    # TODO: Following static stuff is currently only inside the studentenportal container...
    root /srv/www/studentenportal/static/;

    rewrite ^/mitmachen$ https://github.com/studentenportal/web.git redirect;
    rewrite ^/zusammenfassungen/(.*) http://studentenportal.ch/dokumente/$1 permanent;

    location /static/ {
        alias /srv/www/studentenportal/static/;
    }

    location /media/ {
        alias /var/www/studentenportal/media/;
    }

    location /media/documents/ {
        internal;
        alias /var/www/studentenportal/media/documents/;
    }

    location /.well-known/acme-challenge {
      alias /var/www/dehydrated;
    }

    location / {
        if (-f $document_root/maintenance.html) {
            return 503;
        }

        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_redirect off;

        proxy_pass http://app_server;
        break;
    }

    error_page 503 @maintenance;
    location @maintenance {
        rewrite ^(.*)$ /maintenance.html break;
    }
}
