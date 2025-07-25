#!/usr/bin/env python3
# File: verify_network.py

import napalm
import yaml
from concurrent.futures import ThreadPoolExecutor
import json

def load_inventory():
    with open('napalm_inventory.yaml', 'r') as f:
        return yaml.safe_load(f)

def connect_device(device_name, device_info):
    try:
        driver = napalm.get_network_driver(device_info['driver'])
        device = driver(
            hostname=device_info['hostname'],
            username=device_info['username'],
            password=device_info['password'],
            optional_args=device_info.get('optional_args', {})
        )
        device.open()
        return device_name, device, None
    except Exception as e:
        return device_name, None, str(e)

def verify_ospf_neighbors():
    print("=== VERIFYING OSPF NEIGHBORS ===")
    inventory = load_inventory()
    all_devices = {**inventory['spine_switches'], **inventory['leaf_switches']}
    
    connections = {}
    
    # Connect to all devices
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(connect_device, name, info) 
                  for name, info in all_devices.items()]
        
        for future in futures:
            device_name, device, error = future.result()
            if device:
                connections[device_name] = device
                print(f"✓ Connected to {device_name}")
            else:
                print(f"✗ Failed to connect to {device_name}: {error}")
    
    # Check OSPF neighbors
    for device_name, device in connections.items():
        try:
            device_info = all_devices[device_name]
            driver = device_info['driver']
            
            if driver == 'eos':
                output = device.cli(['show ip ospf neighbor'])
                neighbors = output['show ip ospf neighbor']
            elif driver == 'nxos':
                output = device.cli(['show ip ospf neighbors'])
                neighbors = output['show ip ospf neighbors']
            elif driver == 'junos':
                output = device.cli(['show ospf neighbor'])
                neighbors = output['show ospf neighbor']
            elif driver == 'ce':
                output = device.cli(['display ospf peer'])
                neighbors = output['display ospf peer']
            
            print(f"\n{device_name} OSPF Neighbors:")
            print(neighbors[:200] + "..." if len(neighbors) > 200 else neighbors)
            
        except Exception as e:
            print(f"✗ Failed to get OSPF neighbors from {device_name}: {e}")
    
    # Close connections
    for device in connections.values():
        device.close()

def verify_bgp_evpn():
    print("\n=== VERIFYING BGP EVPN ===")
    inventory = load_inventory()
    all_devices = {**inventory['spine_switches'], **inventory['leaf_switches']}
    
    connections = {}
    
    # Connect to all devices
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(connect_device, name, info) 
                  for name, info in all_devices.items()]
        
        for future in futures:
            device_name, device, error = future.result()
            if device:
                connections[device_name] = device
    
    # Check BGP neighbors
    for device_name, device in connections.items():
        try:
            bgp_neighbors = device.get_bgp_neighbors()
            
            print(f"\n{device_name} BGP Summary:")
            if bgp_neighbors and 'global' in bgp_neighbors:
                peers = bgp_neighbors['global']['peers']
                for peer_ip, peer_info in peers.items():
                    state = "UP" if peer_info['is_up'] else "DOWN"
                    print(f"  Peer {peer_ip}: {state}")
            
        except Exception as e:
            print(f"✗ Failed to get BGP neighbors from {device_name}: {e}")
    
    # Close connections
    for device in connections.values():
        device.close()

def test_loopback_reachability():
    print("\n=== TESTING LOOPBACK REACHABILITY ===")
    inventory = load_inventory()
    
    # Test from LEAF-01 to all other loopbacks
    leaf01_info = inventory['leaf_switches']['leaf-01']
    
    try:
        driver = napalm.get_network_driver(leaf01_info['driver'])
        device = driver(
            hostname=leaf01_info['hostname'],
            username=leaf01_info['username'],
            password=leaf01_info['password'],
            optional_args=leaf01_info.get('optional_args', {})
        )
        device.open()
        
        # Test connectivity to all loopbacks
        loopbacks = {
            'SPINE-01': '10.0.0.1',
            'SPINE-02': '10.0.0.2', 
            'SPINE-03': '10.0.0.3',
            'LEAF-01': '10.0.0.11',
            'LEAF-02': '10.0.0.12',
            'LEAF-03': '10.0.0.13',
            'LEAF-04': '10.0.0.14',
            'LEAF-05': '10.0.0.15',
            'LEAF-06': '10.0.0.16'
        }
        
        print("Ping test from LEAF-01:")
        for name, ip in loopbacks.items():
            try:
                result = device.ping(ip, count=3)
                status = "✓ SUCCESS" if result['success']['packet_loss'] < 100 else "✗ FAILED"
                loss = result['success']['packet_loss']
                print(f"  {name} ({ip}): {status} - {loss}% loss")
            except Exception as e:
                print(f"  {name} ({ip}): ✗ ERROR - {e}")
        
        device.close()
        
    except Exception as e:
        print(f"✗ Failed to connect to LEAF-01: {e}")

def main():
    print("Multi-Vendor Data Center Network Verification")
    print("=" * 50)
    
    # Run verification tests
    verify_ospf_neighbors()
    verify_bgp_evpn()
    test_loopback_reachability()
    
    print("\n" + "=" * 50)
    print("Network verification completed!")

if __name__ == "__main__":
    main()
