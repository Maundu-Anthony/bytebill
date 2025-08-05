import subprocess
import time
import psutil
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkMonitor:
    def __init__(self):
        self.wan1_interface = 'enx1'
        self.wan2_interface = 'enx2'
        self.lan_interface = 'eth0'
        self.test_hosts = ['8.8.8.8', '1.1.1.1', '208.67.222.222']
        
    def ping_host(self, host, interface=None, count=3, timeout=10):
        """Ping a host through specific interface"""
        try:
            cmd = ['ping', '-c', str(count), '-W', str(timeout)]
            
            # Add interface binding if specified
            if interface:
                cmd.extend(['-I', interface])
            
            cmd.append(host)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )
            
            if result.returncode == 0:
                # Extract average ping time
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'rtt min/avg/max/mdev' in line or 'round-trip' in line:
                        parts = line.split('/')
                        if len(parts) >= 5:
                            return float(parts[4])  # avg time
                return 0.0  # Connected but couldn't parse time
            else:
                return None  # Host unreachable
                
        except Exception as e:
            logger.error(f"Ping error for {host}: {e}")
            return None
    
    def check_interface_connectivity(self, interface):
        """Check connectivity through specific interface"""
        connectivity_results = []
        
        for host in self.test_hosts:
            ping_result = self.ping_host(host, interface)
            connectivity_results.append({
                'host': host,
                'ping_ms': ping_result,
                'is_reachable': ping_result is not None
            })
        
        # Calculate connectivity score
        reachable_count = sum(1 for result in connectivity_results if result['is_reachable'])
        connectivity_score = (reachable_count / len(self.test_hosts)) * 100
        
        # Calculate average ping time for reachable hosts
        reachable_pings = [r['ping_ms'] for r in connectivity_results if r['is_reachable']]
        avg_ping = sum(reachable_pings) / len(reachable_pings) if reachable_pings else None
        
        return {
            'interface': interface,
            'connectivity_score': connectivity_score,
            'avg_ping_ms': avg_ping,
            'test_results': connectivity_results,
            'is_online': connectivity_score > 0
        }
    
    def get_interface_stats(self, interface):
        """Get network interface statistics"""
        try:
            stats = psutil.net_io_counters(pernic=True)
            if interface in stats:
                return {
                    'bytes_sent': stats[interface].bytes_sent,
                    'bytes_recv': stats[interface].bytes_recv,
                    'packets_sent': stats[interface].packets_sent,
                    'packets_recv': stats[interface].packets_recv,
                    'errin': stats[interface].errin,
                    'errout': stats[interface].errout,
                    'dropin': stats[interface].dropin,
                    'dropout': stats[interface].dropout
                }
            return None
        except Exception as e:
            logger.error(f"Error getting stats for {interface}: {e}")
            return None
    
    def get_interface_status(self, interface):
        """Get interface status and configuration"""
        try:
            # Get interface addresses and status
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            if interface in addrs and interface in stats:
                ipv4_addresses = [
                    addr.address for addr in addrs[interface] 
                    if addr.family == 2  # AF_INET (IPv4)
                ]
                
                return {
                    'is_up': stats[interface].isup,
                    'speed': stats[interface].speed,
                    'mtu': stats[interface].mtu,
                    'ip_addresses': ipv4_addresses,
                    'has_ip': len(ipv4_addresses) > 0
                }
            return None
        except Exception as e:
            logger.error(f"Error getting status for {interface}: {e}")
            return None
    
    def monitor_all_interfaces(self):
        """Monitor all network interfaces"""
        timestamp = datetime.now()
        
        # Monitor WAN interfaces
        wan1_status = self.get_interface_status(self.wan1_interface)
        wan1_stats = self.get_interface_stats(self.wan1_interface)
        wan1_connectivity = None
        
        if wan1_status and wan1_status['is_up'] and wan1_status['has_ip']:
            wan1_connectivity = self.check_interface_connectivity(self.wan1_interface)
        
        wan2_status = self.get_interface_status(self.wan2_interface)
        wan2_stats = self.get_interface_stats(self.wan2_interface)
        wan2_connectivity = None
        
        if wan2_status and wan2_status['is_up'] and wan2_status['has_ip']:
            wan2_connectivity = self.check_interface_connectivity(self.wan2_interface)
        
        # Monitor LAN interface
        lan_status = self.get_interface_status(self.lan_interface)
        lan_stats = self.get_interface_stats(self.lan_interface)
        
        return {
            'timestamp': timestamp.isoformat(),
            'wan1': {
                'interface': self.wan1_interface,
                'status': wan1_status,
                'stats': wan1_stats,
                'connectivity': wan1_connectivity,
                'is_online': wan1_connectivity['is_online'] if wan1_connectivity else False
            },
            'wan2': {
                'interface': self.wan2_interface,
                'status': wan2_status,
                'stats': wan2_stats,
                'connectivity': wan2_connectivity,
                'is_online': wan2_connectivity['is_online'] if wan2_connectivity else False
            },
            'lan': {
                'interface': self.lan_interface,
                'status': lan_status,
                'stats': lan_stats
            }
        }
    
    def run_speed_test(self, interface):
        """Run speed test on specific interface"""
        try:
            # Bind speedtest to specific interface using --interface flag
            cmd = ['speedtest-cli', '--simple', '--interface', interface]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                speed_data = {}
                
                for line in lines:
                    if line.startswith('Ping:'):
                        speed_data['ping_ms'] = float(line.split(':')[1].strip().split()[0])
                    elif line.startswith('Download:'):
                        speed_data['download_mbps'] = float(line.split(':')[1].strip().split()[0])
                    elif line.startswith('Upload:'):
                        speed_data['upload_mbps'] = float(line.split(':')[1].strip().split()[0])
                
                speed_data['timestamp'] = datetime.now().isoformat()
                speed_data['interface'] = interface
                return speed_data
            else:
                logger.error(f"Speed test failed for {interface}: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"Speed test timeout for {interface}")
            return None
        except Exception as e:
            logger.error(f"Speed test error for {interface}: {e}")
            return None

# Convenience functions
def get_network_status():
    """Get current network status for all interfaces"""
    monitor = NetworkMonitor()
    return monitor.monitor_all_interfaces()

def check_wan_connectivity():
    """Quick check of WAN connectivity"""
    monitor = NetworkMonitor()
    wan1_conn = monitor.check_interface_connectivity('enx1')
    wan2_conn = monitor.check_interface_connectivity('enx2')
    
    return {
        'wan1_online': wan1_conn['is_online'] if wan1_conn else False,
        'wan2_online': wan2_conn['is_online'] if wan2_conn else False,
        'timestamp': datetime.now().isoformat()
    }
