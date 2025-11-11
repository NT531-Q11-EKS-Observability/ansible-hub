#!/bin/bash
set -e

echo "[INIT] Starting Icinga Web 2 configuration..."

mkdir -p /etc/icingaweb2

# authentication.ini
cat <<EOF >/etc/icingaweb2/authentication.ini
[users]
backend = "ini"
EOF

# users.ini (plain text password for simplicity)
cat <<EOF >/etc/icingaweb2/users.ini
[admin]
password = admin
EOF

# roles.ini
cat <<EOF >/etc/icingaweb2/roles.ini
[Administrators]
users = "admin"
permissions = "*"
EOF

chown -R www-data:www-data /etc/icingaweb2 || true
echo "[OK] Icinga Web 2 admin user created successfully (admin/admin)"
