# ByteBill - WiFi Hotspot Management System

ByteBill is a comprehensive, self-hosted WiFi Hotspot Management System designed to run on a single device (Lenovo M910q). It combines routing, bandwidth/load balancing, user management, captive portal authentication, voucher generation, M-PESA integration, and a visual admin dashboard.

## 🌟 Features

### Core Functionality
- **Dual-WAN Routing & Load Balancing** - Automatic failover between two ISP connections
- **Captive Portal** - User authentication via vouchers or M-PESA payments
- **Voucher Management** - Generate and manage single/bulk vouchers
- **M-PESA Integration** - Accept payments via Safaricom M-PESA
- **Session Management** - Time and data-based session limits
- **User Tracking** - Monitor active users, data usage, and session history
- **Real-time Dashboard** - Visual analytics and system monitoring

### Network Features
- **Multi-WAN Support** - Built-in Ethernet + 2x USB-to-Ethernet adapters
- **Dynamic Load Balancing** - Intelligent routing based on connection quality
- **Bandwidth Monitoring** - Real-time ISP performance tracking
- **Network Isolation** - Secure client isolation and access control

### Business Features
- **Revenue Tracking** - Comprehensive billing and payment analytics
- **Plan Management** - Flexible pricing plans (hourly, daily, weekly, monthly)
- **Reporting** - Usage statistics and financial reports
- **Multi-tenancy** - Support for different user categories

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   ISP 1 (WAN1)  │    │   ISP 2 (WAN2)  │
│   (Unlimited)   │    │   (FUP-based)   │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          │ USB-Ethernet         │ USB-Ethernet
          │ (enx1)               │ (enx2)
          │                      │
    ┌─────┴──────────────────────┴─────┐
    │        Lenovo M910q              │
    │      (ByteBill Server)           │
    │                                  │
    │  ┌─────────────────────────────┐ │
    │  │     Load Balancer           │ │
    │  │   + Captive Portal          │ │
    │  │   + Admin Dashboard         │ │
    │  └─────────────────────────────┘ │
    └─────┬───────────────────────────┘
          │ Built-in Ethernet (eth0)
          │
    ┌─────┴─────┐
    │  LAN/WiFi │
    │  Clients  │
    └───────────┘
```

## 📁 Project Structure

```
bytebill/
├── frontend/                 # React Admin Dashboard
│   ├── public/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── api/            # API integration
│   │   ├── context/        # React context
│   │   └── utils/          # Utility functions
│   └── package.json
│
├── backend/                 # Flask API Server
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── init_database.py    # Database initialization
│   ├── routes/             # API route handlers
│   │   ├── auth.py         # Authentication routes
│   │   ├── users.py        # User management
│   │   ├── vouchers.py     # Voucher operations
│   │   ├── sessions.py     # Session management
│   │   ├── isp.py          # ISP monitoring
│   │   └── dashboard.py    # Dashboard data
│   ├── models/             # Database models
│   │   ├── user.py
│   │   ├── voucher.py
│   │   ├── session.py
│   │   └── plan.py
│   ├── utils/              # Utility modules
│   │   ├── mpesa.py        # M-PESA integration
│   │   ├── monitor.py      # Network monitoring
│   │   └── router.py       # Routing management
│   └── requirements.txt
│
├── scripts/                # System scripts
│   ├── setup_nat.sh        # NAT configuration
│   ├── dynamic_load_balance.py  # Load balancing daemon
│   └── isp_speedtest.sh    # Speed testing
│
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- MySQL 8.0+
- Node.js 16+
- Python 3.8+
- Root/sudo access for network configuration

### Hardware Requirements

- **Lenovo M910q** (or similar mini PC)
- **1x Built-in Ethernet port** (for LAN)
- **2x UGREEN USB-to-Ethernet adapters** (for WAN connections)
- **Optional: WiFi Access Point** (connected to LAN)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Maundu-Anthony/bytebill.git
   cd bytebill
   ```

2. **Set up the database**
   ```bash
   # Install MySQL
   sudo apt update
   sudo apt install mysql-server mysql-client

   # Install Python MySQL connector
   pip install mysql-connector-python

   # Initialize the database
   cd backend
   python init_database.py
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

5. **Configure environment**
   ```bash
   # Copy example environment file
   cp backend/.env.example backend/.env
   
   # Edit configuration
   nano backend/.env
   ```

6. **Set up network interfaces**
   ```bash
   # Make setup script executable
   chmod +x scripts/setup_nat.sh
   
   # Run NAT setup (requires root)
   sudo ./scripts/setup_nat.sh
   ```

7. **Start the services**
   ```bash
   # Start backend API
   cd backend
   python app.py

   # In another terminal, start frontend
   cd frontend
   npm start
   ```

### Default Access

- **Admin Dashboard**: http://localhost:3000
- **API Server**: http://localhost:5000
- **Captive Portal**: http://hotspot.local/portal

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

## ⚙️ Configuration

### Network Interfaces

Edit `/backend/config.py` to match your network setup:

```python
# Network Settings
LAN_INTERFACE = 'eth0'       # Built-in Ethernet
WAN1_INTERFACE = 'enx1'      # USB-Ethernet adapter 1  
WAN2_INTERFACE = 'enx2'      # USB-Ethernet adapter 2
LAN_SUBNET = '192.168.88.0/24'
GATEWAY_IP = '192.168.88.1'
```

### M-PESA Integration

To enable M-PESA payments, configure your Daraja API credentials:

```python
# M-PESA Settings
MPESA_CONSUMER_KEY = 'your_consumer_key'
MPESA_CONSUMER_SECRET = 'your_consumer_secret'
MPESA_PASSKEY = 'your_passkey'
MPESA_SHORTCODE = 'your_shortcode'
```

### Database Configuration

Update MySQL settings in `/backend/config.py`:

```python
# Database Settings
MYSQL_HOST = 'localhost'
MYSQL_USER = 'bytebill'
MYSQL_PASSWORD = 'bytebill123'
MYSQL_DATABASE = 'bytebill'
```

## 🔧 Network Setup

### Interface Configuration

1. **Connect ISP 1** to first USB-Ethernet adapter (enx1)
2. **Connect ISP 2** to second USB-Ethernet adapter (enx2)  
3. **Connect WiFi AP** to built-in Ethernet port (eth0)

### DHCP Configuration

Configure dnsmasq for LAN DHCP:

```bash
# Install dnsmasq
sudo apt install dnsmasq

# Configure DHCP
echo "interface=eth0
dhcp-range=192.168.88.10,192.168.88.100,255.255.255.0,12h
dhcp-option=3,192.168.88.1
dhcp-option=6,8.8.8.8,1.1.1.1" | sudo tee -a /etc/dnsmasq.conf

# Restart dnsmasq
sudo systemctl restart dnsmasq
```

### Load Balancing Daemon

Set up the automatic load balancing daemon:

```bash
# Make script executable
chmod +x scripts/dynamic_load_balance.py

# Create systemd service
sudo cp scripts/dynamic_load_balance.py /usr/local/bin/
sudo systemctl enable bytebill-loadbalancer
sudo systemctl start bytebill-loadbalancer
```

## 📊 Usage

### Admin Dashboard

Access the admin dashboard at `http://localhost:3000` to:

- Monitor active users and sessions
- Generate and manage vouchers
- View revenue and usage analytics
- Monitor ISP connections
- Configure system settings

### Voucher Management

```bash
# Generate vouchers via API
curl -X POST http://localhost:5000/api/vouchers/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "count": 10,
    "plan": "daily",
    "duration": 86400,
    "expires_in_days": 30
  }'
```

### User Connection

Users connect via the captive portal at `http://hotspot.local/portal` using:
- **Voucher codes** (pre-generated)
- **M-PESA payments** (real-time)

## 🔍 Monitoring

### System Status

Check system status:

```bash
# View load balancer logs
sudo journalctl -u bytebill-loadbalancer -f

# Check ISP connectivity  
sudo ./scripts/isp_speedtest.sh

# Monitor network interfaces
ip addr show
ip route show
```

### Performance Metrics

The dashboard provides real-time metrics for:
- Active user count
- Bandwidth usage per ISP
- Revenue tracking
- Session statistics
- System alerts

## 🛠️ API Documentation

### Authentication

```bash
# Admin login
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}

# User portal login
POST /api/auth/user-login  
{
  "voucher_code": "BYTE123456",
  "mac_address": "00:11:22:33:44:55",
  "ip_address": "192.168.88.10"
}
```

### Voucher Management

```bash
# Get vouchers
GET /api/vouchers?page=1&per_page=20&status=unused

# Generate vouchers
POST /api/vouchers/generate
{
  "count": 10,
  "plan": "daily", 
  "duration": 86400,
  "data_limit": 1073741824,
  "expires_in_days": 7
}

# Redeem voucher
POST /api/vouchers/{code}/redeem
{
  "mac_address": "00:11:22:33:44:55",
  "ip_address": "192.168.88.10"
}
```

### Session Management

```bash
# Get active sessions
GET /api/sessions/active

# Terminate session
POST /api/sessions/{id}/terminate

# Get session statistics
GET /api/sessions/stats
```

## 🔒 Security

### Firewall Configuration

ByteBill automatically configures iptables rules for:
- NAT/MASQUERADE for internet sharing
- Port restrictions for security
- Client isolation between users

### Access Control

- Admin dashboard requires authentication
- API endpoints protected with JWT tokens
- User sessions tracked by MAC address
- Automatic session termination on limits

## 📈 Production Deployment

### Systemd Services

Create systemd services for auto-start:

```bash
# ByteBill API service
sudo systemctl enable bytebill-api
sudo systemctl start bytebill-api

# Load balancer service  
sudo systemctl enable bytebill-loadbalancer
sudo systemctl start bytebill-loadbalancer
```

### Nginx Reverse Proxy

Configure Nginx for production:

```nginx
server {
    listen 80;
    server_name hotspot.local;
    
    # Serve React frontend
    location / {
        root /var/www/bytebill/frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSL Configuration

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d hotspot.local
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Report bugs on GitHub Issues
- **Community**: Join our Discord server for discussions
- **Email**: support@bytebill.local

## 🙏 Acknowledgments

- **CoovaChilli** for captive portal inspiration
- **Safaricom** for M-PESA API integration
- **React** and **Flask** communities
- **Ubuntu** for the solid foundation

---

**ByteBill** - Transforming small-scale internet sharing with enterprise-grade features! 🚀
