#!/usr/bin/env python3
"""Test Python network automation environment"""

import sys
import subprocess
from pathlib import Path

def test_packages():
    """Test required packages"""
    packages = ['netmiko', 'napalm', 'yaml', 'paramiko', 'jinja2']
    
    print("🧪 Testing Python packages...")
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")

def test_tools():
    """Test system tools"""
    tools = ['nmap', 'telnet', 'ssh', 'ping']
    
    print("\n🔧 Testing system tools...")
    for tool in tools:
        result = subprocess.run(['which', tool], capture_output=True)
        if result.returncode == 0:
            print(f"✅ {tool}")
        else:
            print(f"❌ {tool} - NOT FOUND")

def test_directories():
    """Test directory structure"""
    dirs = [
        '/opt/network-automation/scripts',
        '/opt/network-automation/logs',
        '/opt/network-automation/backups',
        '/opt/network-automation/inventory'
    ]
    
    print("\n📁 Testing directories...")
    for directory in dirs:
        if Path(directory).exists():
            print(f"✅ {directory}")
        else:
            print(f"❌ {directory} - MISSING")

if __name__ == "__main__":
    print("🚀 Testing EVE-NG Python Environment")
    print("=" * 50)
    test_packages()
    test_tools()
    test_directories()
    print("\n✨ Environment test completed!")
