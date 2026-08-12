# VPS Security Hardening Checklist

For Hermes installations running on Linux VPS (cloud servers). Apply on day 1, before installing Hermes or any services.

## Threat Model

- Your VPS runs an AI agent with access to X API, GitHub, and web
- A compromised VPS = compromised X account + GitHub repos
- Build-in-public means your infra is discoverable (you'll post about it)
- Attackers scan new VPS IPs within hours of provisioning

## SSH Hardening (first 10 minutes)

```bash
# 1. Create non-root user
adduser hermes
usermod -aG sudo hermes

# 2. Copy SSH key to new user
mkdir -p /home/hermes/.ssh
cp /root/.ssh/authorized_keys /home/hermes/.ssh/
chown -R hermes:hermes /home/hermes/.ssh
chmod 700 /home/hermes/.ssh
chmod 600 /home/hermes/.ssh/authorized_keys

# 3. Harden sshd_config
cat >> /etc/ssh/sshd_config.d/hardening.conf << 'EOF'
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
PermitEmptyPasswords no
MaxAuthTries 3
X11Forwarding no
AllowAgentForwarding no
ClientAliveInterval 300
ClientAliveCountMax 2
AllowUsers hermes
EOF

# 4. Restart SSH
systemctl restart sshd

# 5. CRITICAL: test new user login before closing root session
# Open NEW terminal: ssh hermes@YOUR_VPS_IP
```

**Pitfall:** Keep root session open while testing. If you lock yourself out, you need VPS console access to fix it.

## Firewall — UFW (first 20 minutes)

```bash
apt install -y ufw

ufw default deny incoming
ufw default allow outgoing

# SSH only (restrict to your IP if possible)
ufw allow from YOUR_MAC_IP to any port 22
# Or: ufw allow 22/tcp

# DO NOT open unless explicitly needed:
# ufw allow 80/tcp    # HTTP
# ufw allow 443/tcp   # HTTPS
# ufw allow 8080/tcp  # Dev servers
# ufw allow 3000/tcp  # Node apps

ufw enable
ufw status verbose
```

**Key insight:** Hermes communicates outbound (to APIs), not inbound. You don't need to open any ports for Hermes to work — SSH is the only exception.

## Fail2Ban (automatic brute-force protection)

```bash
apt install -y fail2ban

cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

systemctl enable fail2ban
systemctl start fail2ban
```

## Automatic Security Updates

```bash
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

## System Hardening

```bash
# Disable unused services
systemctl disable cups 2>/dev/null
systemctl disable avahi-daemon 2>/dev/null

# Restrict cron access
echo "root" > /etc/cron.allow
echo "hermes" >> /etc/cron.allow

# Set restrictive umask
echo "umask 027" >> /etc/profile

# Disable core dumps
echo "* hard core 0" >> /etc/security/limits.conf

# Harden kernel
cat >> /etc/sysctl.conf << 'EOF'
net.ipv4.ip_forward = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.all.accept_source_route = 0
EOF
sysctl -p
```

## Audit Logging

```bash
apt install -y auditd

cat >> /etc/audit/rules.d/hermes.rules << 'EOF'
-w /etc/ssh/sshd_config -p wa -k sshd_config
-w /etc/ssh/sshd_config.d/ -p wa -k sshd_config
-w /etc/passwd -p wa -k user_changes
-w /etc/shadow -p wa -k password_changes
-w /etc/group -p wa -k group_changes
-w /etc/sudoers -p wa -k sudoers
-w /etc/sudoers.d/ -p wa -k sudoers
-w /etc/crontab -p wa -k cron
-w /var/spool/cron/ -p wa -k cron
EOF

systemctl restart auditd
```

## Verification

```bash
ufw status                           # Only SSH allowed
fail2ban-client status               # sshd jail active
systemctl is-enabled unattended-upgrades  # enabled
auditd status                        # running
```

## VPS Provider Comparison (for Hermes)

| Provider | Price/mo | CPU | RAM | Storage | Best For |
|----------|----------|-----|-----|---------|----------|
| Oracle Cloud Free | $0 | 4 ARM | 24 GB | 200 GB | Starting out, zero cost |
| Hetzner CX22 | ~$5 | 2 vCPU | 4 GB | 40 GB | Budget production |
| Hetzner CX32 | ~$8 | 4 vCPU | 8 GB | 80 GB NVMe | Browser automation, larger projects |
| DigitalOcean | $24 | 2 vCPU | 4 GB | 80 GB | Best docs, per-second billing |
| Contabo | $5 | 3 vCPU | 8 GB | 75 GB | Most RAM per dollar |

**Recommended path:** Oracle Free → Hetzner CX32 when you hit limits.

**Pitfalls:**
- Oracle signup often requires 2-3 attempts (fraud detection). Use real credit card, clean IP.
- Hetzner charges extra ~$0.60/mo for IPv4.
- 4 GB RAM is tight if running browser automation (Chromium takes 2-4 GB per session).
- ARM architecture (Oracle) has minor compatibility edge cases with some packages.
