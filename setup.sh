#!/bin/bash
if [ "$EUID" -ne 0 ]; then
  exit
fi

dnf install -y nginx mariadb-server python3 python3-pip git

useradd teacher || true
echo "teacher:12345678" | chpasswd
usermod -aG wheel teacher
chage -d 0 teacher

useradd -r -s /sbin/nologin app || true

usermod -s /bin/bash operator || true
echo "operator:12345678" | chpasswd
chage -d 0 operator

echo "operator ALL=(ALL) /usr/bin/systemctl start mywebapp, /usr/bin/systemctl stop mywebapp, /usr/bin/systemctl restart mywebapp, /usr/bin/systemctl status mywebapp, /usr/bin/systemctl reload nginx" > /etc/sudoers.d/operator

systemctl enable --now mariadb
mysql -u root -e "CREATE DATABASE IF NOT EXISTS inventory_db;"
mysql -u root -e "CREATE USER IF NOT EXISTS 'app_user'@'localhost' IDENTIFIED BY 'secret';"
mysql -u root -e "GRANT ALL PRIVILEGES ON inventory_db.* TO 'app_user'@'localhost';"
mysql -u root -e "FLUSH PRIVILEGES;"

mkdir -p /opt/mywebapp
cp -r $(pwd)/* /opt/mywebapp/
chown -R app:app /opt/mywebapp
cd /opt/mywebapp
python3 -m venv venv
/opt/mywebapp/venv/bin/pip install Flask PyMySQL

cat << 'EOF' > /etc/systemd/system/mywebapp.service
[Unit]
Description=Simple Inventory Web Application
After=network.target mariadb.service

[Service]
User=app
WorkingDirectory=/opt/mywebapp
Environment="PATH=/opt/mywebapp/venv/bin"
ExecStartPre=/opt/mywebapp/venv/bin/python migrate.py --db-user app_user --db-pass secret --db-name inventory_db
ExecStart=/opt/mywebapp/venv/bin/python app.py --interface 127.0.0.1 --port 5000 --db-user app_user --db-pass secret --db-name inventory_db
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now mywebapp

setsebool -P httpd_can_network_connect 1

cat << 'EOF' > /etc/nginx/conf.d/mywebapp.conf
server {
    listen 80;
    server_name _;
    access_log /var/log/nginx/mywebapp_access.log;
    
    location = / {
        proxy_pass http://127.0.0.1:5000;
    }
    location /items {
        proxy_pass http://127.0.0.1:5000;
    }
    location /health {
        return 403;
    }
}
EOF

sed -i 's/listen       80;/listen       8080;/g' /etc/nginx/nginx.conf
sed -i 's/listen       \[::\]:80;/listen       \[::\]:8080;/g' /etc/nginx/nginx.conf

systemctl restart nginx
systemctl enable nginx

firewall-cmd --add-port=80/tcp --permanent
firewall-cmd --reload

echo "14" > "$HOME/gradebook"

usermod -L loneliness
