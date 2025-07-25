#!/usr/bin/env python3
"""
Fix BGP Configuration
Complete the BGP setup with proper iBGP configuration
"""

from netmiko import ConnectHandler
import time

# Device configurations
devices = [
    {'device_type': 'cisco_xe', 'host': '192.168.100.10', 'username': 'admin', 'password': 'cisco', 'secret': 'cisco'},
    {'device_type': 'cisco_xe', 'host': '192.168.100.11', 'username': 'admin', 'password': 'cisco', 'secret': 'cisco'},
    {'device_type': 'cisco_xe', 'host': '192.168.100.12', 'username': 'admin', 'password': 'cisco', 'secret': 'cisco'}
]

device_names = ['CSR1', 'CSR2', 'CSR3']

# Fixed BGP configurations
bgp_configs = {
    'CSR1': [
        'no router bgp 65001',  # Remove old config
        'router bgp 65001',
        'bgp router-id 1.1.1.1',
        'bgp log-neighbor-changes',
        'neighbor 2.2.2.2 remote-as 65001',  # iBGP to CSR2
        'neighbor 2.2.2.2 update-source loopback0',
        'neighbor 2.2.2.2 next-hop-self',
        'neighbor 3.3.3.3 remote-as 65001',  # iBGP to CSR3  
        'neighbor 3.3.3.3 update-source loopback0',
        'neighbor 3.3.3.3 next-hop-self',
        'address-family ipv4',
        'neighbor 2.2.2.2 activate',
        'neighbor 3.3.3.3 activate',
        'network 1.1.1.1 mask 255.255.255.255',
        'network 10.1.12.0 mask 255.255.255.0',
        'network 10.1.13.0 mask 255.255.255.0',
        'exit-address-family',
        'exit'
    ],
    'CSR2': [
        'no router bgp 65002',  # Remove old config
        'router bgp 65001',     # Same AS for iBGP
        'bgp router-id 2.2.2.2',
        'bgp log-neighbor-changes',
        'neighbor 1.1.1.1 remote-as 65001',  # iBGP to CSR1
        'neighbor 1.1.1.1 update-source loopback0',
        'neighbor 1.1.1.1 next-hop-self',
        'neighbor 3.3.3.3 remote-as 65001',  # iBGP to CSR3
        'neighbor 3.3.3.3 update-source loopback0', 
        'neighbor 3.3.3.3 next-hop-self',
        'address-family ipv4',
        'neighbor 1.1.1.1 activate',
        'neighbor 3.3.3.3 activate',
        'network 2.2.2.2 mask 255.255.255.255',
        'network 10.1.12.0 mask 255.255.255.0',
        'network 10.2.23.0 mask 255.255.255.0',
        'exit-address-family',
        'exit'
    ],
    'CSR3': [
        'no router bgp 65003',  # Remove old config
        'router bgp 65001',     # Same AS for iBGP
        'bgp router-id 3.3.3.3',
        'bgp log-neighbor-changes',
        'neighbor 1.1.1.1 remote-as 65001',  # iBGP to CSR1
        'neighbor 1.1.1.1 update-source loopback0',
        'neighbor 1.1.1.1 next-hop-self',
        'neighbor 2.2.2.2 remote-as 65001',  # iBGP to CSR2
        'neighbor 2.2.2.2 update-source loopback0',
        'neighbor 2.2.2.2 next-hop-self',
        'address-family ipv4',
        'neighbor 1.1.1.1 activate',
        'neighbor 2.2.2.2 activate',
        'network 3.3.3.3 mask 255.255.255.255',
        'network 10.1.13.0 mask 255.255.255.0',
        'network 10.2.23.0 mask 255.255.255.0',
        'exit-address-family',
        'exit'
    ]
}

print("🔧 Fixing BGP Configuration...")
print("=" * 50)

for i, device in enumerate(devices):
    device_name = device_names[i]
    try:
        print(f"Connecting to {device_name} ({device['host']})...")
        connection = ConnectHandler(**device)
        connection.enable()
        
        print(f"📝 Fixing BGP configuration on {device_name}...")
        
        # Send BGP configuration commands
        config_commands = bgp_configs[device_name]
        output = connection.send_config_set(config_commands)
        
        # Save configuration
        connection.send_command('write memory')
        
        print(f"✅ {device_name}: BGP configuration fixed!")
        print(f"📋 Configuration output preview:")
        print("-" * 40)
        print(output[:300] + "..." if len(output) > 300 else output)
        
        connection.disconnect()
        print(f"🔌 {device_name}: Disconnected\n")
        
    except Exception as e:
        print(f"❌ {device_name}: BGP configuration failed - {str(e)}\n")

print("✅ BGP configuration fix completed!")
print("\n📊 Updated Network Configuration:")
print("All routers now in AS65001 (iBGP)")
print("CSR1 (1.1.1.1/32) - BGP Router ID: 1.1.1.1")
print("├── iBGP peer: 2.2.2.2 (CSR2)")  
print("└── iBGP peer: 3.3.3.3 (CSR3)")
print("\nCSR2 (2.2.2.2/32) - BGP Router ID: 2.2.2.2")
print("├── iBGP peer: 1.1.1.1 (CSR1)")
print("└── iBGP peer: 3.3.3.3 (CSR3)")
print("\nCSR3 (3.3.3.3/32) - BGP Router ID: 3.3.3.3") 
print("├── iBGP peer: 1.1.1.1 (CSR1)")
print("└── iBGP peer: 2.2.2.2 (CSR2)")
print("\n💡 BGP neighbors should establish once OSPF provides reachability to loopbacks")