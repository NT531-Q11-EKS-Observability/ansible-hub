#!/bin/sh
set -e
mkdir -p /etc/icingaweb2
echo "[users]" > /etc/icingaweb2/authentication.ini
echo 'backend = "ini"' >> /etc/icingaweb2/authentication.ini

echo "[admin]" > /etc/icingaweb2/users.ini
echo 'password = admin' >> /etc/icingaweb2/users.ini

echo "[Administrators]" > /etc/icingaweb2/roles.ini
echo 'users = "admin"' >> /etc/icingaweb2/roles.ini
echo 'permissions = "*"' >> /etc/icingaweb2/roles.ini

chown -R www-data:www-data /etc/icingaweb2 2>/dev/null || true
echo "[OK] Plaintext Icinga admin user created (admin/admin)"
