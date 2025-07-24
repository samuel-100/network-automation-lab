#!/usr/bin/env python3
from netmiko import ConnectHandler
import time

# Device configurations
devices = [
    {'device_type': 'cisco_xe', 'host': '192.168.100.10', 'username': 'admin', 'password': 'cisco', 'secret': 'cisco'},
    {'device_type': 'cisco_xe', 'host': '192.168.100.11', 'username': 'admin', 'password': 'cisco', 'secret': 'cisco'},
    {'device_type': 'cisco_xe', 'host': '192.168.100.12', 'username': 'admin', 'password': 'cisco', 'secret': 'cisco'}
]

device_names = ['CSR1', 'CSR2', 'CSR3']

# Configuration templates for each router
configs = {
    'CSR1': [
        'hostname CSR1',
        'interface loopback0',
        'ip address 1.1.1.1 255.255.255.255',
        'no shutdown',
        'exit',
        'interface GigabitEthernet2',
        'ip address 10.1.12.1 255.255.255.0',
        'no shutdown',
        'exit',
        'interface GigabitEthernet3', 
        'ip address 10.1.13.1 255.255.255.0',
        'no shutdown',
        'exit',
        'router ospf 1',
        'router-id 1.1.1.1',
        'network 1.1.1.1 0.0.0.0 area 0',
        'network 10.1.12.0 0.0.0.255 area 0',
        'network 10.1.13.0 0.0.0.255 area 0',
        'exit',
        'router bgp 65001',
        'bgp router-id 1.1.1.1',
        'neighbor 2.2.2.2 remote-as 65002',
        'neighbor 2.2.2.2 update-source loopback0',
        'neighbor 3.3.3.3 remote-as 65003',
        'neighbor 3.3.3.3 update-source loopback0',
        'exit'
    ],
    'CSR2': [
        'hostname CSR2',
        'interface loopback0',
        'ip address 2.2.2.2 255.255.255.255',
        'no shutdown',
        'exit',
        'interface GigabitEthernet2',
        'ip address 10.1.12.2 255.255.255.0',
        'no shutdown',
        'exit',
        'interface GigabitEthernet3',
        'ip address 10.2.23.2 255.255.255.0', 
        'no shutdown',
        'exit',
        'router ospf 1',
        'router-id 2.2.2.2',
        'network 2.2.2.2 0.0.0.0 area 0',
        'network 10.1.12.0 0.0.0.255 area 0',
        'network 10.2.23.0 0.0.0.255 area 0',
        'exit',
        'router bgp 65002',
        'bgp router-id 2.2.2.2',
        'neighbor 1.1.1.1 remote-as 65001',
        'neighbor 1.1.1.1 update-source loopback0',
        'neighbor 3.3.3.3 remote-as 65003',
        'neighbor 3.3.3.3 update-source loopback0',
        'exit'
    ],
    'CSR3': [
        'hostname CSR3',
        'interface loopback0',
        'ip address 3.3.3.3 255.255.255.255',
        'no shutdown',
        'exit',
        'interface GigabitEthernet2',
        'ip address 10.1.13.3 255.255.255.0',
        'no shutdown',
        'exit',
        'interface GigabitEthernet3',
        'ip address 10.2.23.3 255.255.255.0',
        'no shutdown', 
        'exit',
        'router ospf 1',
        'router-id 3.3.3.3',
        'network 3.3.3.3 0.0.0.0 area 0',
        'network 10.1.13.0 0.0.0.255 area 0',
        'network 10.2.23.0 0.0.0.255 area 0',
        'exit',
        'router bgp 65003',
        'bgp router-id 3.3.3.3',
        'neighbor 1.1.1.1 remote-as 65001',
        'neighbor 1.1.1.1 update-source loopback0',
        'neighbor 2.2.2.2 remote-as 65002',
        'neighbor 2.2.2.2 update-source loopback0',
        'exit'
    ]
}

print("🔧 Configuring Network Lab...")
print("=" * 50)

for i, device in enumerate(devices):
    device_name = device_names[i]
    try:
        print(f"Connecting to {device_name} ({device['host']})...")
        connection = ConnectHandler(**device)
        connection.enable()
        
        print(f"📝 Configuring {device_name}...")
        
        # Send configuration commands
        config_commands = configs[device_name]
        output = connection.send_config_set(config_commands)
        
        # Save configuration
        connection.send_command('write memory')
        
        print(f"✅ {device_name}: Configuration completed!")
        print(f"📋 Configuration output preview:")
        print("-" * 40)
        print(output[:300] + "..." if len(output) > 300 else output)
        
        connection.disconnect()
        print(f"🔌 {device_name}: Disconnected\n")
        
    except Exception as e:
        print(f"❌ {device_name}: Configuration failed - {str(e)}\n")

print("✅ Network configuration completed!")
print("\n📊 Network Topology:")
print("CSR1 (1.1.1.1/32) - AS65001")
print("├── Gi2: 10.1.12.1/24 ↔ CSR2")  
print("└── Gi3: 10.1.13.1/24 ↔ CSR3")
print("\nCSR2 (2.2.2.2/32) - AS65002")
print("├── Gi2: 10.1.12.2/24 ↔ CSR1")
print("└── Gi3: 10.2.23.2/24 ↔ CSR3")
print("\nCSR3 (3.3.3.3/32) - AS65003") 
print("├── Gi2: 10.1.13.3/24 ↔ CSR1")
print("└── Gi3: 10.2.23.3/24 ↔ CSR2")