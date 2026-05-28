#!/bin/bash
echo "Setting up Target Node..."

echo "student ALL=(ALL) NOPASSWD: /usr/bin/docker, /bin/systemctl, /usr/bin/systemctl" | sudo tee /etc/sudoers.d/student-deploy

sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload

sudo dnf install nginx -y
sudo tee /etc/nginx/nginx.conf > /dev/null << 'EOF'
events {}
http {
    server {
        listen 80;
        location / {
            proxy_pass http://127.0.0.1:5000;
        }
    }
}
EOF

sudo setsebool -P httpd_can_network_connect 1

sudo systemctl enable --now nginx

echo "Setup complete!"
