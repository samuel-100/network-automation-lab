#!/usr/bin/env python3
# File: dc_automation.py

import napalm
import yaml
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import os

class DCNetworkManager:
    def __init__(self, inventory_file='napalm_inventory.yaml'):
        with open(inventory_file, 'r') as f:
            self.inventory = yaml.safe_load(f)
        self.connections = {}
    
    def connect_all_devices(self):
        """Connect to all devices"""
        all_devices = {**self.inventory['spine_switches'], 
                      **self.inventory['leaf_switches']}
        
        def connect_device(device_info):
            device_name, device_config = device_info
            try:
                driver = napalm.get_network_driver(device_config['driver'])
                device = driver(
                    hostname=device_config['hostname'],
                    username=device_config['username'],
                    password=device_config['password'],
                    optional_args=device_config.get('optional_args', {})
                )
                device.open()
                return device_name, device
            except Exception as e:
                print(f"Failed to connect to {device_name}: {e}")
                return device_name, None
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(connect_device, item) 
                      for item in all_devices.items()]
            
            for future in futures:
                device_name, device = future.result()
                if device:
                    self.connections[device_name] = device
                    print(f"✓ Connected to {device_name}")
    
    def backup_all_configs(self):
        """Backup configurations from all devices"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"backups/backup_{timestamp}"
        
        os.makedirs(backup_dir, exist_ok=True)
        
        for device_name, device in self.connections.items():
            try:
                config = device.get_config()
                
                # Save running config
                with open(f"{backup_dir}/{device_name}_running.txt", 'w') as f:
                    f.write(config['running'])
                
                # Save startup config if exists
                if 'startup' in config and config['startup']:
                    with open(f"{backup_dir}/{device_name}_startup.txt", 'w') as f:
                        f.write(config['startup'])
                
                print(f"✓ Backed up {device_name}")
                
            except Exception as e:
                print(f"✗ Failed to backup {device_name}: {e}")
        
        print(f"Backups saved to {backup_dir}")
    
    def get_network_facts(self):
        """Get facts from all devices"""
        facts = {}
        
        for device_name, device in self.connections.items():
            try:
                device_facts = device.get_facts()
                facts[device_name] = device_facts
                print(f"✓ Got facts from {device_name}")
            except Exception as e:
                print(f"✗ Failed to get facts from {device_name}: {e}")
                facts[device_name] = {'error': str(e)}
        
        # Save facts to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs('logs', exist_ok=True)
        with open(f'logs/network_facts_{timestamp}.json', 'w') as f:
            json.dump(facts, f, indent=2, default=str)
        
        return facts
    
    def monitor_network_health(self):
       """Monitor network health"""
       print("\n=== NETWORK HEALTH MONITORING ===")
       
       # Check BGP neighbors
       print("\nBGP Neighbor Status:")
       for device_name, device in self.connections.items():
           try:
               bgp_neighbors = device.get_bgp_neighbors()
               if bgp_neighbors and 'global' in bgp_neighbors:
                   peers = bgp_neighbors['global']['peers']
                   up_count = sum(1 for p in peers.values() if p['is_up'])
                   total_count = len(peers)
                   print(f"  {device_name}: {up_count}/{total_count} BGP peers UP")
               else:
                   print(f"  {device_name}: No BGP neighbors configured")
           except Exception as e:
               print(f"  {device_name}: Error checking BGP - {e}")
       
       # Check interface status
       print("\nInterface Status:")
       for device_name, device in self.connections.items():
           try:
               interfaces = device.get_interfaces()
               up_count = sum(1 for intf in interfaces.values() if intf['is_up'])
               total_count = len(interfaces)
               print(f"  {device_name}: {up_count}/{total_count} interfaces UP")
           except Exception as e:
               print(f"  {device_name}: Error checking interfaces - {e}")
   
   def disconnect_all(self):
       """Disconnect from all devices"""
       for device_name, device in self.connections.items():
           try:
               device.close()
               print(f"✓ Disconnected from {device_name}")
           except Exception as e:
               print(f"✗ Error disconnecting from {device_name}: {e}")

def main():
   print("Data Center Network Automation")
   print("=" * 40)
   
   # Initialize manager
   manager = DCNetworkManager()
   
   try:
       # Connect to all devices
       print("1. Connecting to all devices...")
       manager.connect_all_devices()
       print(f"Connected to {len(manager.connections)} devices\n")
       
       # Backup configurations
       print("2. Backing up configurations...")
       manager.backup_all_configs()
       print()
       
       # Get network facts
       print("3. Gathering network facts...")
       facts = manager.get_network_facts()
       print()
       
       # Monitor network health
       print("4. Monitoring network health...")
       manager.monitor_network_health()
       print()
       
       print("Automation tasks completed successfully!")
       
   except Exception as e:
       print(f"Error: {e}")
   
   finally:
       # Disconnect from all devices
       print("\nDisconnecting from all devices...")
       manager.disconnect_all()

if __name__ == "__main__":
   main()
