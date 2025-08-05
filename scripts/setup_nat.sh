#!/bin/bash

# ByteBill NAT Setup Script
# This script configures NAT rules for the WiFi hotspot management system

# Configuration
WAN1_INTERFACE="enx1"  # USB-to-Ethernet adapter 1
WAN2_INTERFACE="enx2"  # USB-to-Ethernet adapter 2
LAN_INTERFACE="eth0"   # Built-in Ethernet for LAN
LAN_SUBNET="192.168.88.0/24"

echo "Setting up ByteBill NAT configuration..."

# Enable IP forwarding
echo "Enabling IP forwarding..."
sysctl -w net.ipv4.ip_forward=1
sysctl -w net.ipv4.conf.all.forwarding=1

# Make IP forwarding permanent
if ! grep -q "net.ipv4.ip_forward=1" /etc/sysctl.conf; then
    echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
fi

if ! grep -q "net.ipv4.conf.all.forwarding=1" /etc/sysctl.conf; then
    echo "net.ipv4.conf.all.forwarding=1" >> /etc/sysctl.conf
fi

# Clear existing iptables rules
echo "Clearing existing iptables rules..."
iptables -F
iptables -t nat -F
iptables -t mangle -F
iptables -X

# Set default policies
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# Setup NAT rules for both WAN interfaces
echo "Setting up NAT rules..."
iptables -t nat -A POSTROUTING -o $WAN1_INTERFACE -j MASQUERADE
iptables -t nat -A POSTROUTING -o $WAN2_INTERFACE -j MASQUERADE

# Setup forward rules
echo "Setting up forward rules..."
iptables -A FORWARD -i $LAN_INTERFACE -o $WAN1_INTERFACE -j ACCEPT
iptables -A FORWARD -i $LAN_INTERFACE -o $WAN2_INTERFACE -j ACCEPT
iptables -A FORWARD -i $WAN1_INTERFACE -o $LAN_INTERFACE -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -i $WAN2_INTERFACE -o $LAN_INTERFACE -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow loopback traffic
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow SSH (port 22)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP and HTTPS for captive portal
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow Flask API (port 5000)
iptables -A INPUT -p tcp --dport 5000 -j ACCEPT

# Allow DNS
iptables -A INPUT -p udp --dport 53 -j ACCEPT
iptables -A INPUT -p tcp --dport 53 -j ACCEPT

# Allow DHCP
iptables -A INPUT -p udp --dport 67 -j ACCEPT
iptables -A INPUT -p udp --dport 68 -j ACCEPT

# Allow LAN traffic
iptables -A INPUT -i $LAN_INTERFACE -j ACCEPT

# Allow established connections
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Save iptables rules
echo "Saving iptables rules..."
if command -v iptables-save > /dev/null; then
    iptables-save > /etc/iptables/rules.v4
elif command -v netfilter-persistent > /dev/null; then
    netfilter-persistent save
else
    echo "Warning: Could not save iptables rules permanently"
fi

# Display current rules
echo "Current NAT rules:"
iptables -t nat -L -n

echo "Current filter rules:"
iptables -L -n

echo "NAT setup complete!"
echo "WAN1 Interface: $WAN1_INTERFACE"
echo "WAN2 Interface: $WAN2_INTERFACE"
echo "LAN Interface: $LAN_INTERFACE"
echo "LAN Subnet: $LAN_SUBNET"
