from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import psutil
import subprocess
import time
from datetime import datetime

isp_bp = Blueprint('isp', __name__)

def ping_host(host, count=3):
    """Ping a host and return average response time"""
    try:
        result = subprocess.run(
            ['ping', '-c', str(count), host],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'avg' in line:
                    # Extract average time from ping output
                    parts = line.split('/')
                    if len(parts) >= 5:
                        return float(parts[4])
            return 0.0
        else:
            return None
    except Exception as e:
        print(f"Ping error: {e}")
        return None

def get_interface_stats(interface):
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
        print(f"Interface stats error: {e}")
        return None

def check_interface_status(interface):
    """Check if network interface is up"""
    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        if interface in addrs and interface in stats:
            return {
                'is_up': stats[interface].isup,
                'speed': stats[interface].speed,
                'mtu': stats[interface].mtu,
                'ip_addresses': [addr.address for addr in addrs[interface] 
                               if addr.family == 2]  # IPv4 addresses
            }
        return None
    except Exception as e:
        print(f"Interface status error: {e}")
        return None

@isp_bp.route('/status', methods=['GET'])
@jwt_required()
def get_isp_status():
    """Get ISP connection status"""
    
    # Test connectivity to common DNS servers
    test_hosts = ['8.8.8.8', '1.1.1.1', '208.67.222.222']
    
    wan1_interface = 'enx1'  # USB-to-Ethernet adapter 1
    wan2_interface = 'enx2'  # USB-to-Ethernet adapter 2
    
    # Check WAN1 status
    wan1_status = check_interface_status(wan1_interface)
    wan1_stats = get_interface_stats(wan1_interface)
    wan1_ping = None
    if wan1_status and wan1_status['is_up']:
        wan1_ping = ping_host(test_hosts[0])
    
    # Check WAN2 status
    wan2_status = check_interface_status(wan2_interface)
    wan2_stats = get_interface_stats(wan2_interface)
    wan2_ping = None
    if wan2_status and wan2_status['is_up']:
        wan2_ping = ping_host(test_hosts[1])
    
    # Determine which ISP is primary based on routing table or current config
    primary_isp = 'wan1'  # Default or based on load balancing logic
    
    status = {
        'timestamp': datetime.now().isoformat(),
        'wan1': {
            'name': 'ISP 1 (Unlimited)',
            'interface': wan1_interface,
            'status': wan1_status,
            'stats': wan1_stats,
            'ping_ms': wan1_ping,
            'is_connected': wan1_ping is not None,
            'is_primary': primary_isp == 'wan1'
        },
        'wan2': {
            'name': 'ISP 2 (FUP)',
            'interface': wan2_interface,
            'status': wan2_status,
            'stats': wan2_stats,
            'ping_ms': wan2_ping,
            'is_connected': wan2_ping is not None,
            'is_primary': primary_isp == 'wan2'
        },
        'primary_isp': primary_isp,
        'load_balancing_active': True,  # Based on actual config
        'failover_active': wan1_ping is None or wan2_ping is None
    }
    
    return jsonify(status)

@isp_bp.route('/speedtest', methods=['POST'])
@jwt_required()
def run_speedtest():
    """Run speed test on specified interface"""
    data = request.get_json()
    interface = data.get('interface', 'wan1')
    
    # TODO: Implement actual speed test using speedtest-cli or similar
    # For now, return mock data
    
    mock_results = {
        'wan1': {
            'download_mbps': 15.5,
            'upload_mbps': 8.2,
            'ping_ms': 45.3,
            'server': 'Local ISP Server',
            'timestamp': datetime.now().isoformat()
        },
        'wan2': {
            'download_mbps': 25.8,
            'upload_mbps': 12.1,
            'ping_ms': 32.1,
            'server': 'Safaricom Server',
            'timestamp': datetime.now().isoformat()
        }
    }
    
    interface_key = interface if interface in mock_results else 'wan1'
    
    return jsonify({
        'interface': interface,
        'results': mock_results[interface_key]
    })

@isp_bp.route('/switch-primary', methods=['POST'])
@jwt_required()
def switch_primary_isp():
    """Switch primary ISP for load balancing"""
    data = request.get_json()
    new_primary = data.get('primary_isp')  # 'wan1' or 'wan2'
    
    if new_primary not in ['wan1', 'wan2']:
        return jsonify({'error': 'Invalid ISP specified'}), 400
    
    # TODO: Implement actual routing table updates
    # This would involve updating iptables rules and routing tables
    
    return jsonify({
        'message': f'Primary ISP switched to {new_primary}',
        'primary_isp': new_primary,
        'timestamp': datetime.now().isoformat()
    })

@isp_bp.route('/bandwidth', methods=['GET'])
@jwt_required()
def get_bandwidth_usage():
    """Get bandwidth usage statistics"""
    
    wan1_stats = get_interface_stats('enx1')
    wan2_stats = get_interface_stats('enx2')
    lan_stats = get_interface_stats('eth0')
    
    # Calculate total usage (you might want to store historical data)
    total_download = 0
    total_upload = 0
    
    if wan1_stats:
        total_download += wan1_stats['bytes_recv']
        total_upload += wan1_stats['bytes_sent']
    
    if wan2_stats:
        total_download += wan2_stats['bytes_recv']
        total_upload += wan2_stats['bytes_sent']
    
    usage = {
        'total_download_bytes': total_download,
        'total_upload_bytes': total_upload,
        'total_download_mb': round(total_download / (1024 * 1024), 2),
        'total_upload_mb': round(total_upload / (1024 * 1024), 2),
        'wan1_stats': wan1_stats,
        'wan2_stats': wan2_stats,
        'lan_stats': lan_stats,
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(usage)

@isp_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_isp_logs():
    """Get ISP monitoring logs"""
    # TODO: Implement actual log reading from system logs or database
    
    mock_logs = [
        {
            'timestamp': '2024-01-01T10:00:00',
            'level': 'INFO',
            'message': 'WAN1 connection stable - 15.2 Mbps',
            'interface': 'wan1'
        },
        {
            'timestamp': '2024-01-01T10:05:00',
            'level': 'WARNING',
            'message': 'WAN2 latency increased to 150ms',
            'interface': 'wan2'
        },
        {
            'timestamp': '2024-01-01T10:10:00',
            'level': 'INFO',
            'message': 'Load balancing switched to WAN1',
            'interface': 'system'
        }
    ]
    
    return jsonify({'logs': mock_logs})
