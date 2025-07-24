#!/usr/bin/env python3
from netmiko import ConnectHandler

devices = [
    {'device_type': 'cisco_xe', 'host': '192.168.100.10', 'username': 'admin', 'password': 'cisco', 'secret': 'cisco'},
    {'device_type': 'cisco_xe', 'host': '192.168.100.11', 'username': 'admin', 'password': 'cisco', 'secret': 'cisco'},
    {'device_type': 'cisco_xe', 'host': '192.168.100.12', 'username': 'admin', 'password': 'cisco', 'secret': 'cisco'}
]

device_names = ['CSR1', 'CSR2', 'CSR3']

print("🔍 Testing CSR Lab Connectivity...")
print("=" * 50)

for i, device in enumerate(devices):
    device_name = device_names[i]
    try:
        print(f"Connecting to {device_name} ({device['host']})...")
        connection = ConnectHandler(**device)
        prompt = connection.find_prompt()
        print(f"✅ {device_name}: Connected! Prompt: {prompt}")
        
        # Execute show commands
        print(f"\n📋 {device_name} - Show Version:")
        print("-" * 40)
        version_output = connection.send_command("show version")
        print(version_output[:500] + "..." if len(version_output) > 500 else version_output)
        
        print(f"\n📋 {device_name} - Show IP Interface Brief:")
        print("-" * 40)
        ip_int_brief = connection.send_command("show ip interface brief")
        print(ip_int_brief)
        
        connection.disconnect()
        print(f"\n🔌 {device_name}: Disconnected\n")
        
    except Exception as e:
        print(f"❌ {device_name}: Failed - {str(e)}\n")

print("\n✅ Test completed!")
