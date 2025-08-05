import subprocess
import ipaddress
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RouterManager:
    def __init__(self):
        self.wan1_interface = 'enx1'
        self.wan2_interface = 'enx2'
        self.lan_interface = 'eth0'
        self.lan_subnet = '192.168.88.0/24'
        self.gateway_ip = '192.168.88.1'
        
        # Routing table IDs for policy routing
        self.wan1_table = 101
        self.wan2_table = 102
        
    def run_command(self, command: List[str], check_output: bool = True) -> Optional[str]:
        """Run a system command safely"""
        try:
            if check_output:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.strip()
            else:
                subprocess.run(command, check=True)
                return None
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(command)}, Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error running command: {e}")
            return None
    
    def enable_ip_forwarding(self):
        """Enable IP forwarding"""
        commands = [
            ['sysctl', '-w', 'net.ipv4.ip_forward=1'],
            ['sysctl', '-w', 'net.ipv4.conf.all.forwarding=1']
        ]
        
        for cmd in commands:
            self.run_command(cmd, check_output=False)
        
        # Make it permanent
        try:
            with open('/etc/sysctl.conf', 'a') as f:
                f.write('\n# ByteBill IP Forwarding\n')
                f.write('net.ipv4.ip_forward=1\n')
                f.write('net.ipv4.conf.all.forwarding=1\n')
        except Exception as e:
            logger.error(f"Failed to update sysctl.conf: {e}")
    
    def setup_nat_rules(self):
        """Setup NAT rules for both WAN interfaces"""
        # Clear existing NAT rules
        self.run_command(['iptables', '-t', 'nat', '-F'], check_output=False)
        
        # Setup MASQUERADE for both WAN interfaces
        nat_commands = [
            ['iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', self.wan1_interface, '-j', 'MASQUERADE'],
            ['iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', self.wan2_interface, '-j', 'MASQUERADE'],
        ]
        
        for cmd in nat_commands:
            self.run_command(cmd, check_output=False)
        
        logger.info("NAT rules configured for both WAN interfaces")
    
    def setup_firewall_rules(self):
        """Setup basic firewall rules"""
        # Allow established and related connections
        firewall_commands = [
            ['iptables', '-A', 'FORWARD', '-m', 'conntrack', '--ctstate', 'ESTABLISHED,RELATED', '-j', 'ACCEPT'],
            ['iptables', '-A', 'FORWARD', '-i', self.lan_interface, '-o', self.wan1_interface, '-j', 'ACCEPT'],
            ['iptables', '-A', 'FORWARD', '-i', self.lan_interface, '-o', self.wan2_interface, '-j', 'ACCEPT'],
            
            # Allow SSH access (be careful with this in production)
            ['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', '22', '-j', 'ACCEPT'],
            
            # Allow HTTP/HTTPS for captive portal
            ['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', '80', '-j', 'ACCEPT'],
            ['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', '443', '-j', 'ACCEPT'],
            
            # Allow Flask API
            ['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', '5000', '-j', 'ACCEPT'],
            
            # Allow loopback
            ['iptables', '-A', 'INPUT', '-i', 'lo', '-j', 'ACCEPT'],
            
            # Allow LAN access
            ['iptables', '-A', 'INPUT', '-i', self.lan_interface, '-j', 'ACCEPT'],
        ]
        
        for cmd in firewall_commands:
            self.run_command(cmd, check_output=False)
    
    def setup_policy_routing(self):
        """Setup policy-based routing for load balancing"""
        # Clear existing rules
        self.run_command(['ip', 'rule', 'flush'], check_output=False)
        self.run_command(['ip', 'route', 'flush', 'table', str(self.wan1_table)], check_output=False)
        self.run_command(['ip', 'route', 'flush', 'table', str(self.wan2_table)], check_output=False)
        
        # Get WAN gateway IPs
        wan1_gateway = self.get_interface_gateway(self.wan1_interface)
        wan2_gateway = self.get_interface_gateway(self.wan2_interface)
        
        if not wan1_gateway or not wan2_gateway:
            logger.error("Could not determine WAN gateways")
            return False
        
        # Setup routing tables
        routing_commands = [
            # WAN1 table
            ['ip', 'route', 'add', 'default', 'via', wan1_gateway, 'dev', self.wan1_interface, 'table', str(self.wan1_table)],
            ['ip', 'route', 'add', self.lan_subnet, 'dev', self.lan_interface, 'table', str(self.wan1_table)],
            
            # WAN2 table
            ['ip', 'route', 'add', 'default', 'via', wan2_gateway, 'dev', self.wan2_interface, 'table', str(self.wan2_table)],
            ['ip', 'route', 'add', self.lan_subnet, 'dev', self.lan_interface, 'table', str(self.wan2_table)],
            
            # Default rules
            ['ip', 'rule', 'add', 'from', 'all', 'table', 'main', 'pref', '32766'],
            ['ip', 'rule', 'add', 'from', 'all', 'table', 'default', 'pref', '32767'],
        ]
        
        for cmd in routing_commands:
            self.run_command(cmd, check_output=False)
        
        logger.info("Policy routing configured")
        return True
    
    def get_interface_gateway(self, interface: str) -> Optional[str]:
        """Get the gateway IP for a network interface"""
        try:
            result = self.run_command(['ip', 'route', 'show', 'dev', interface])
            if result:
                lines = result.split('\n')
                for line in lines:
                    if 'default via' in line:
                        parts = line.split()
                        gateway_index = parts.index('via') + 1
                        if gateway_index < len(parts):
                            return parts[gateway_index]
            return None
        except Exception as e:
            logger.error(f"Error getting gateway for {interface}: {e}")
            return None
    
    def set_primary_wan(self, wan_interface: str):
        """Set primary WAN interface for routing"""
        if wan_interface == self.wan1_interface:
            table_id = self.wan1_table
        elif wan_interface == self.wan2_interface:
            table_id = self.wan2_table
        else:
            logger.error(f"Invalid WAN interface: {wan_interface}")
            return False
        
        # Remove existing default route
        self.run_command(['ip', 'route', 'del', 'default'], check_output=False)
        
        # Add new default route from specified table
        gateway = self.get_interface_gateway(wan_interface)
        if gateway:
            self.run_command([
                'ip', 'route', 'add', 'default', 'via', gateway, 'dev', wan_interface
            ], check_output=False)
            logger.info(f"Primary WAN set to {wan_interface}")
            return True
        
        return False
    
    def setup_load_balancing(self):
        """Setup load balancing between WAN interfaces"""
        wan1_gateway = self.get_interface_gateway(self.wan1_interface)
        wan2_gateway = self.get_interface_gateway(self.wan2_interface)
        
        if not wan1_gateway or not wan2_gateway:
            logger.error("Cannot setup load balancing - missing gateways")
            return False
        
        # Remove existing default route
        self.run_command(['ip', 'route', 'del', 'default'], check_output=False)
        
        # Add load-balanced default route
        self.run_command([
            'ip', 'route', 'add', 'default',
            'nexthop', 'via', wan1_gateway, 'dev', self.wan1_interface, 'weight', '1',
            'nexthop', 'via', wan2_gateway, 'dev', self.wan2_interface, 'weight', '1'
        ], check_output=False)
        
        logger.info("Load balancing configured")
        return True
    
    def block_user(self, ip_address: str, mac_address: str):
        """Block a user by IP and MAC address"""
        block_commands = [
            ['iptables', '-A', 'FORWARD', '-s', ip_address, '-j', 'DROP'],
            ['iptables', '-A', 'FORWARD', '-m', 'mac', '--mac-source', mac_address, '-j', 'DROP']
        ]
        
        for cmd in block_commands:
            self.run_command(cmd, check_output=False)
        
        logger.info(f"Blocked user: IP {ip_address}, MAC {mac_address}")
    
    def unblock_user(self, ip_address: str, mac_address: str):
        """Unblock a user by removing iptables rules"""
        unblock_commands = [
            ['iptables', '-D', 'FORWARD', '-s', ip_address, '-j', 'DROP'],
            ['iptables', '-D', 'FORWARD', '-m', 'mac', '--mac-source', mac_address, '-j', 'DROP']
        ]
        
        for cmd in unblock_commands:
            self.run_command(cmd, check_output=False)
        
        logger.info(f"Unblocked user: IP {ip_address}, MAC {mac_address}")
    
    def get_routing_table(self):
        """Get current routing table"""
        result = self.run_command(['ip', 'route', 'show'])
        return result.split('\n') if result else []
    
    def get_iptables_rules(self):
        """Get current iptables rules"""
        nat_rules = self.run_command(['iptables', '-t', 'nat', '-L', '-n'])
        filter_rules = self.run_command(['iptables', '-L', '-n'])
        
        return {
            'nat': nat_rules.split('\n') if nat_rules else [],
            'filter': filter_rules.split('\n') if filter_rules else []
        }
    
    def initialize_routing(self):
        """Initialize complete routing setup"""
        logger.info("Initializing ByteBill routing...")
        
        # Enable IP forwarding
        self.enable_ip_forwarding()
        
        # Setup NAT rules
        self.setup_nat_rules()
        
        # Setup firewall rules
        self.setup_firewall_rules()
        
        # Setup policy routing
        self.setup_policy_routing()
        
        # Setup load balancing
        self.setup_load_balancing()
        
        logger.info("Routing initialization complete")

# Convenience functions
def initialize_router():
    """Initialize router configuration"""
    router = RouterManager()
    router.initialize_routing()

def switch_primary_wan(wan_interface: str):
    """Switch primary WAN interface"""
    router = RouterManager()
    return router.set_primary_wan(wan_interface)

def block_client(ip_address: str, mac_address: str):
    """Block a client"""
    router = RouterManager()
    router.block_user(ip_address, mac_address)

def unblock_client(ip_address: str, mac_address: str):
    """Unblock a client"""
    router = RouterManager()
    router.unblock_user(ip_address, mac_address)
