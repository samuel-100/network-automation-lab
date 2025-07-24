#!/usr/bin/env python3
"""
EVE-NG Network Device Manager
Complete automation toolkit for EVE-NG lab environments
"""

import os
import sys
import yaml
import json
import subprocess
import socket
import time
import logging
from datetime import datetime
from pathlib import Path
from netmiko import ConnectHandler, NetMikoTimeoutException
from dotenv import load_dotenv
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/network-automation/logs/automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EVENetworkManager:
    """Complete network automation manager for EVE-NG"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv('/opt/network-automation/.env')
        
        # Initialize paths
        self.base_path = Path('/opt/network-automation')
        self.inventory_path = self.base_path / 'inventory'
        self.backup_path = self.base_path / 'backups'
        self.logs_path = self.base_path / 'logs'
        
        # Create directories if they don't exist
        for path in [self.inventory_path, self.backup_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Default credentials
        self.default_username = os.getenv('DEFAULT_USERNAME', 'cisco')
        self.default_password = os.getenv('DEFAULT_PASSWORD', 'cisco')
        self.default_secret = os.getenv('DEFAULT_ENABLE_SECRET', 'cisco')
        
        self.devices = {}
        
    def discover_lab_devices(self):
        """Discover EVE-NG lab devices"""
        logger.info("🔍 Starting lab device discovery...")
        
        # Common lab network ranges
        network_ranges = [
            "192.168.1.0/24",
            "10.0.0.0/24", 
            "172.16.0.0/24"
        ]
        
        discovered_devices = {}
        device_counter = 1
        
        for network in network_ranges:
            logger.info(f"📡 Scanning network: {network}")
            active_hosts = self._scan_network(network)
            
            for host in active_hosts:
                # Skip gateway addresses
                if host.split('.')[-1] in ['1', '254']:
                    continue
                    
                logger.info(f"🔍 Analyzing device: {host}")
                device_info = self._identify_device(host)
                
                if device_info:
                    device_name = f"R{device_counter}" if device_counter <= 5 else f"SW{device_counter-5}"
                    discovered_devices[device_name] = device_info
                    device_counter += 1
        
        # Save discovered devices
        inventory_data = {
            'discovered_at': datetime.now().isoformat(),
            'lab_devices': discovered_devices
        }
        
        inventory_file = self.inventory_path / 'lab_devices.yaml'
        with open(inventory_file, 'w') as f:
            yaml.dump(inventory_data, f, default_flow_style=False)
        
        logger.info(f"✅ Discovery complete! Found {len(discovered_devices)} devices")
        logger.info(f"📁 Inventory saved to: {inventory_file}")
        
        self.devices = discovered_devices
        return discovered_devices
    
    def _scan_network(self, network_cidr):
        """Scan network for active hosts using nmap"""
        try:
            result = subprocess.run([
                'nmap', '-sn', '-T4', '--max-retries=1', network_cidr
            ], capture_output=True, text=True, timeout=30)
            
            active_hosts = []
            for line in result.stdout.split('\n'):
                if 'Nmap scan report for' in line:
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        ip = ip_match.group(1)
                        # Quick ping test to confirm
                        if self._ping_host(ip):
                            active_hosts.append(ip)
            
            logger.info(f"Found {len(active_hosts)} active hosts in {network_cidr}")
            return active_hosts
            
        except Exception as e:
            logger.error(f"Error scanning network {network_cidr}: {e}")
            return []
    
    def _ping_host(self, host):
        """Quick ping test"""
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '2', host], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _identify_device(self, ip_address):
        """Identify device type and gather basic information"""
        # Test if SSH port is open
        if not self._test_port(ip_address, 22):
            return None
        
        device_types = ['cisco_ios', 'cisco_xe', 'juniper_junos', 'arista_eos']
        
        for device_type in device_types:
            try:
                connection_params = {
                    'device_type': device_type,
                    'host': ip_address,
                    'username': self.default_username,
                    'password': self.default_password,
                    'secret': self.default_secret,
                    'timeout': 10,
                    'session_timeout': 15
                }
                
                with ConnectHandler(**connection_params) as conn:
                    prompt = conn.find_prompt()
                    version = conn.send_command('show version', delay_factor=1)
                    
                    device_info = {
                        'hostname': ip_address,
                        'device_type': device_type,
                        'username': self.default_username,
                        'password': self.default_password,
                        'secret': self.default_secret,
                        'port': 22,
                        'prompt': prompt.strip(),
                        'version_snippet': version[:150] + '...' if len(version) > 150 else version,
                        'discovered_at': datetime.now().isoformat()
                    }
                    
                    logger.info(f"✅ Identified {ip_address} as {device_type}")
                    return device_info
                    
            except Exception as e:
                logger.debug(f"Failed to connect to {ip_address} with {device_type}: {e}")
                continue
        
        return None
    
    def _test_port(self, host, port, timeout=3):
        """Test if port is open"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                return result == 0
        except:
            return False
    
    def load_inventory(self):
        """Load device inventory from file"""
        inventory_file = self.inventory_path / 'lab_devices.yaml'
        
        try:
            with open(inventory_file, 'r') as f:
                data = yaml.safe_load(f)
                self.devices = data.get('lab_devices', {})
                logger.info(f"📋 Loaded {len(self.devices)} devices from inventory")
                return self.devices
        except FileNotFoundError:
            logger.warning("No inventory file found. Run discovery first.")
            return {}
        except Exception as e:
            logger.error(f"Error loading inventory: {e}")
            return {}
    
    def backup_all_configurations(self):
        """Backup configurations from all devices"""
        if not self.devices:
            self.load_inventory()
        
        if not self.devices:
            logger.error("No devices found. Run discovery first.")
            return {}
        
        logger.info(f"🔄 Starting configuration backup for {len(self.devices)} devices")
        
        results = {}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for device_name, device_config in self.devices.items():
            result = self._backup_single_device(device_name, device_config, timestamp)
            results[device_name] = result
        
        # Summary
        successful = sum(1 for r in results.values() if r.get('success'))
        logger.info(f"✅ Backup Summary: {successful}/{len(results)} successful")
        
        return results
    
    def _backup_single_device(self, device_name, device_config, timestamp):
        """Backup single device configuration"""
        try:
            connection_params = {
                'device_type': device_config.get('device_type', 'cisco_ios'),
                'host': device_config['hostname'],
                'username': device_config.get('username', self.default_username),
                'password': device_config.get('password', self.default_password),
                'secret': device_config.get('secret', self.default_secret),
                'timeout': 30
            }
            
            with ConnectHandler(**connection_params) as conn:
                config = conn.send_command('show running-config', delay_factor=2)
                
                # Save to file
                backup_filename = f"{device_name}_{timestamp}.cfg"
                backup_file = self.backup_path / backup_filename
                
                with open(backup_file, 'w') as f:
                    f.write(f"! Configuration backup for {device_name}\n")
                    f.write(f"! Device: {device_config['hostname']}\n")
                    f.write(f"! Backup Date: {datetime.now()}\n!\n")
                    f.write(config)
                
                logger.info(f"✅ Backed up {device_name}")
                return {'success': True, 'filename': backup_filename}
                
        except Exception as e:
            logger.error(f"❌ Backup failed for {device_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def monitor_devices(self):
        """Monitor all devices and collect status"""
        if not self.devices:
            self.load_inventory()
        
        if not self.devices:
            logger.error("No devices found. Run discovery first.")
            return {}
        
        logger.info(f"📊 Starting device monitoring for {len(self.devices)} devices")
        
        results = {}
        for device_name, device_config in self.devices.items():
            result = self._monitor_single_device(device_name, device_config)
            results[device_name] = result
            
            status = "🟢 UP" if result['status'] == 'UP' else "🔴 DOWN"
            logger.info(f"{status} {device_name} ({result.get('hostname', 'N/A')})")
        
        # Summary
        up_count = sum(1 for r in results.values() if r.get('status') == 'UP')
        down_count = len(results) - up_count
        logger.info(f"📈 Status Summary: {up_count} UP, {down_count} DOWN")
        
        return results
    
    def _monitor_single_device(self, device_name, device_config):
        """Monitor single device"""
        try:
            start_time = time.time()
            
            connection_params = {
                'device_type': device_config.get('device_type', 'cisco_ios'),
                'host': device_config['hostname'],
                'username': device_config.get('username', self.default_username),
                'password': device_config.get('password', self.default_password),
                'secret': device_config.get('secret', self.default_secret),
                'timeout': 15
            }
            
            with ConnectHandler(**connection_params) as conn:
                uptime = conn.send_command('show version | include uptime', delay_factor=1)
                interfaces = conn.send_command('show ip interface brief', delay_factor=1)
                
                response_time = time.time() - start_time
                
                return {
                    'status': 'UP',
                    'hostname': device_config['hostname'],
                    'uptime': uptime.strip(),
                    'interface_count': len([l for l in interfaces.split('\n') if l.strip() and 'Interface' not in l]),
                    'response_time': round(response_time, 2),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'status': 'DOWN',
                'hostname': device_config['hostname'],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def list_devices(self):
        """List all devices in inventory"""
        if not self.devices:
            self.load_inventory()
        
        if not self.devices:
            print("No devices found. Run discovery first with: python3 scripts/eve_network_manager.py discover")
            return
        
        print("\n📋 Lab Device Inventory")
        print("=" * 60)
        for device_name, config in self.devices.items():
            print(f"Device: {device_name}")
            print(f"  IP: {config.get('hostname')}")
            print(f"  Type: {config.get('device_type')}")
            print(f"  Status: {'✅ Configured' if config else '❌ Not configured'}")
            print()

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='EVE-NG Network Automation Manager')
    parser.add_argument('action', choices=['discover', 'backup', 'monitor', 'list'], 
                       help='Action to perform')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    manager = EVENetworkManager()
    
    if args.action == 'discover':
        print("🔍 Starting device discovery...")
        devices = manager.discover_lab_devices()
        print(f"✅ Discovery complete! Found {len(devices)} devices")
        
    elif args.action == 'backup':
        print("💾 Starting configuration backup...")
        results = manager.backup_all_configurations()
        successful = sum(1 for r in results.values() if r.get('success'))
        print(f"✅ Backup complete! {successful}/{len(results)} successful")
        
    elif args.action == 'monitor':
        print("📊 Starting device monitoring...")
        results = manager.monitor_devices()
        
    elif args.action == 'list':
        manager.list_devices()

if __name__ == "__main__":
    main()
