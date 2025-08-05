#!/usr/bin/env python3

"""
ByteBill Dynamic Load Balancer
This script monitors both WAN connections and dynamically switches between them
based on connectivity, latency, and bandwidth availability.
"""

import subprocess
import time
import logging
import json
import os
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/bytebill-loadbalancer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LoadBalancer:
    def __init__(self):
        self.wan1_interface = 'enx1'
        self.wan2_interface = 'enx2'
        self.lan_interface = 'eth0'
        
        # Monitoring configuration
        self.test_hosts = ['8.8.8.8', '1.1.1.1', '208.67.222.222']
        self.ping_timeout = 5
        self.ping_count = 3
        self.check_interval = 30  # seconds
        
        # Failover thresholds
        self.max_latency = 200  # ms
        self.max_packet_loss = 30  # percentage
        self.min_connectivity_score = 50  # percentage
        
        # Load balancing weights
        self.wan1_weight = 1
        self.wan2_weight = 1
        
        # State tracking
        self.current_primary = None
        self.wan1_stats = {'online': False, 'latency': 0, 'packet_loss': 0}
        self.wan2_stats = {'online': False, 'latency': 0, 'packet_loss': 0}
        
        # History for trend analysis
        self.history_size = 10
        self.wan1_history = []
        self.wan2_history = []
        
        self.running = True
        
    def run_command(self, command: List[str]) -> Optional[str]:
        """Run a command and return output"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception as e:
            logger.error(f"Command failed: {' '.join(command)}, Error: {e}")
            return None
    
    def ping_host(self, host: str, interface: str) -> Dict:
        """Ping a host through specific interface"""
        try:
            cmd = ['ping', '-c', str(self.ping_count), '-W', str(self.ping_timeout), '-I', interface, host]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.ping_timeout + 5
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                
                # Extract packet loss
                packet_loss = 0
                for line in lines:
                    if '% packet loss' in line:
                        packet_loss = float(line.split('%')[0].split()[-1])
                        break
                
                # Extract average latency
                avg_latency = 0
                for line in lines:
                    if 'rtt min/avg/max/mdev' in line or 'round-trip' in line:
                        parts = line.split('/')
                        if len(parts) >= 5:
                            avg_latency = float(parts[4])
                        break
                
                return {
                    'success': True,
                    'latency': avg_latency,
                    'packet_loss': packet_loss
                }
            else:
                return {
                    'success': False,
                    'latency': 9999,
                    'packet_loss': 100
                }
                
        except Exception as e:
            logger.error(f"Ping error for {host} via {interface}: {e}")
            return {
                'success': False,
                'latency': 9999,
                'packet_loss': 100
            }
    
    def test_interface_connectivity(self, interface: str) -> Dict:
        """Test connectivity for an interface"""
        results = []
        
        for host in self.test_hosts:
            result = self.ping_host(host, interface)
            results.append(result)
        
        # Calculate averages
        successful_tests = [r for r in results if r['success']]
        
        if not successful_tests:
            return {
                'online': False,
                'latency': 9999,
                'packet_loss': 100,
                'connectivity_score': 0
            }
        
        avg_latency = sum(r['latency'] for r in successful_tests) / len(successful_tests)
        avg_packet_loss = sum(r['packet_loss'] for r in results) / len(results)
        connectivity_score = (len(successful_tests) / len(results)) * 100
        
        return {
            'online': connectivity_score > self.min_connectivity_score,
            'latency': avg_latency,
            'packet_loss': avg_packet_loss,
            'connectivity_score': connectivity_score
        }
    
    def get_interface_gateway(self, interface: str) -> Optional[str]:
        """Get gateway for interface"""
        result = self.run_command(['ip', 'route', 'show', 'dev', interface])
        if result:
            for line in result.split('\n'):
                if 'default via' in line:
                    parts = line.split()
                    try:
                        gateway_index = parts.index('via') + 1
                        return parts[gateway_index]
                    except (ValueError, IndexError):
                        continue
        return None
    
    def set_primary_route(self, interface: str) -> bool:
        """Set primary default route"""
        gateway = self.get_interface_gateway(interface)
        if not gateway:
            logger.error(f"No gateway found for {interface}")
            return False
        
        # Remove existing default routes
        self.run_command(['ip', 'route', 'del', 'default'])
        
        # Add new default route
        success = self.run_command(['ip', 'route', 'add', 'default', 'via', gateway, 'dev', interface])
        
        if success is not None:
            logger.info(f"Primary route set to {interface} via {gateway}")
            return True
        else:
            logger.error(f"Failed to set primary route to {interface}")
            return False
    
    def setup_load_balancing(self) -> bool:
        """Setup load balancing between both interfaces"""
        wan1_gateway = self.get_interface_gateway(self.wan1_interface)
        wan2_gateway = self.get_interface_gateway(self.wan2_interface)
        
        if not wan1_gateway or not wan2_gateway:
            logger.error("Cannot setup load balancing - missing gateways")
            return False
        
        # Remove existing default route
        self.run_command(['ip', 'route', 'del', 'default'])
        
        # Add load-balanced route
        cmd = [
            'ip', 'route', 'add', 'default',
            'nexthop', 'via', wan1_gateway, 'dev', self.wan1_interface, 'weight', str(self.wan1_weight),
            'nexthop', 'via', wan2_gateway, 'dev', self.wan2_interface, 'weight', str(self.wan2_weight)
        ]
        
        success = self.run_command(cmd)
        if success is not None:
            logger.info(f"Load balancing configured: WAN1 weight {self.wan1_weight}, WAN2 weight {self.wan2_weight}")
            return True
        else:
            logger.error("Failed to setup load balancing")
            return False
    
    def determine_best_interface(self) -> Optional[str]:
        """Determine which interface should be primary"""
        wan1_online = self.wan1_stats['online']
        wan2_online = self.wan2_stats['online']
        
        # If only one is online, use that one
        if wan1_online and not wan2_online:
            return self.wan1_interface
        elif wan2_online and not wan1_online:
            return self.wan2_interface
        elif not wan1_online and not wan2_online:
            return None
        
        # Both are online, choose based on performance
        wan1_score = self.calculate_interface_score(self.wan1_stats)
        wan2_score = self.calculate_interface_score(self.wan2_stats)
        
        logger.info(f"Interface scores - WAN1: {wan1_score:.2f}, WAN2: {wan2_score:.2f}")
        
        if wan1_score > wan2_score:
            return self.wan1_interface
        else:
            return self.wan2_interface
    
    def calculate_interface_score(self, stats: Dict) -> float:
        """Calculate a score for interface quality"""
        if not stats['online']:
            return 0
        
        # Lower latency is better, lower packet loss is better
        latency_score = max(0, 100 - (stats['latency'] / 2))  # 200ms = 0 points
        packet_loss_score = max(0, 100 - (stats['packet_loss'] * 2))  # 50% loss = 0 points
        
        # Weight the scores
        total_score = (latency_score * 0.6) + (packet_loss_score * 0.4)
        
        return total_score
    
    def update_statistics(self):
        """Update statistics for both interfaces"""
        logger.info("Testing WAN connectivity...")
        
        # Test WAN1
        wan1_result = self.test_interface_connectivity(self.wan1_interface)
        self.wan1_stats = wan1_result
        self.wan1_history.append(wan1_result)
        if len(self.wan1_history) > self.history_size:
            self.wan1_history.pop(0)
        
        # Test WAN2
        wan2_result = self.test_interface_connectivity(self.wan2_interface)
        self.wan2_stats = wan2_result
        self.wan2_history.append(wan2_result)
        if len(self.wan2_history) > self.history_size:
            self.wan2_history.pop(0)
        
        logger.info(f"WAN1 ({self.wan1_interface}): Online={wan1_result['online']}, "
                   f"Latency={wan1_result['latency']:.1f}ms, Loss={wan1_result['packet_loss']:.1f}%")
        logger.info(f"WAN2 ({self.wan2_interface}): Online={wan2_result['online']}, "
                   f"Latency={wan2_result['latency']:.1f}ms, Loss={wan2_result['packet_loss']:.1f}%")
    
    def make_routing_decision(self):
        """Make routing decision based on current statistics"""
        best_interface = self.determine_best_interface()
        
        if best_interface is None:
            logger.warning("No WAN interfaces are online!")
            return
        
        # Check if we need to change primary interface
        if self.current_primary != best_interface:
            logger.info(f"Switching primary interface from {self.current_primary} to {best_interface}")
            
            if self.wan1_stats['online'] and self.wan2_stats['online']:
                # Both online, use load balancing
                self.setup_load_balancing()
                self.current_primary = 'load_balanced'
            else:
                # Use failover
                if self.set_primary_route(best_interface):
                    self.current_primary = best_interface
                else:
                    logger.error("Failed to switch primary interface")
        
        elif self.current_primary == 'load_balanced':
            # Check if we should switch from load balancing to failover
            if not (self.wan1_stats['online'] and self.wan2_stats['online']):
                if self.set_primary_route(best_interface):
                    self.current_primary = best_interface
    
    def save_status(self):
        """Save current status to file"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'current_primary': self.current_primary,
            'wan1_stats': self.wan1_stats,
            'wan2_stats': self.wan2_stats,
            'wan1_interface': self.wan1_interface,
            'wan2_interface': self.wan2_interface
        }
        
        try:
            with open('/var/lib/bytebill/loadbalancer_status.json', 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save status: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def run(self):
        """Main monitoring loop"""
        logger.info("ByteBill Load Balancer starting...")
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Create status directory
        os.makedirs('/var/lib/bytebill', exist_ok=True)
        
        while self.running:
            try:
                self.update_statistics()
                self.make_routing_decision()
                self.save_status()
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Brief pause before retrying
        
        logger.info("ByteBill Load Balancer stopped")

if __name__ == '__main__':
    load_balancer = LoadBalancer()
    load_balancer.run()
