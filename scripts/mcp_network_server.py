#!/usr/bin/env python3
"""
MCP Network Server for OSPF and BGP Monitoring
Provides real-time network information via MCP protocol
"""

import asyncio
import json
import sys
from typing import Any, Dict, List
from netmiko import ConnectHandler
import yaml

# MCP Server Implementation
class NetworkMCPServer:
    def __init__(self):
        self.devices = [
            {'device_type': 'cisco_xe', 'host': '192.168.100.10', 'username': 'admin', 'password': 'cisco', 'secret': 'cisco', 'name': 'CSR1'},
            {'device_type': 'cisco_xe', 'host': '192.168.100.11', 'username': 'admin', 'password': 'cisco', 'secret': 'cisco', 'name': 'CSR2'},
            {'device_type': 'cisco_xe', 'host': '192.168.100.12', 'username': 'admin', 'password': 'cisco', 'secret': 'cisco', 'name': 'CSR3'}
        ]
    
    def connect_to_device(self, device_info):
        """Connect to a network device"""
        device_params = {k: v for k, v in device_info.items() if k != 'name'}
        return ConnectHandler(**device_params)
    
    def get_ospf_neighbors(self, device_name=None):
        """Get OSPF neighbor information"""
        results = {}
        devices_to_check = [d for d in self.devices if d['name'] == device_name] if device_name else self.devices
        
        for device in devices_to_check:
            try:
                connection = self.connect_to_device(device)
                connection.enable()
                output = connection.send_command("show ip ospf neighbor")
                results[device['name']] = {
                    'status': 'success',
                    'data': output,
                    'summary': self._parse_ospf_neighbors(output)
                }
                connection.disconnect()
            except Exception as e:
                results[device['name']] = {'status': 'error', 'error': str(e)}
        
        return results
    
    def get_bgp_summary(self, device_name=None):
        """Get BGP summary information"""
        results = {}
        devices_to_check = [d for d in self.devices if d['name'] == device_name] if device_name else self.devices
        
        for device in devices_to_check:
            try:
                connection = self.connect_to_device(device)
                connection.enable()
                output = connection.send_command("show ip bgp summary")
                results[device['name']] = {
                    'status': 'success',
                    'data': output,
                    'summary': self._parse_bgp_summary(output)
                }
                connection.disconnect()
            except Exception as e:
                results[device['name']] = {'status': 'error', 'error': str(e)}
        
        return results
    
    def get_routing_table(self, device_name=None):
        """Get routing table information"""
        results = {}
        devices_to_check = [d for d in self.devices if d['name'] == device_name] if device_name else self.devices
        
        for device in devices_to_check:
            try:
                connection = self.connect_to_device(device)
                connection.enable()
                output = connection.send_command("show ip route")
                results[device['name']] = {
                    'status': 'success',
                    'data': output,
                    'summary': self._parse_routing_table(output)
                }
                connection.disconnect()
            except Exception as e:
                results[device['name']] = {'status': 'error', 'error': str(e)}
        
        return results
    
    def get_interface_status(self, device_name=None):
        """Get interface status"""
        results = {}
        devices_to_check = [d for d in self.devices if d['name'] == device_name] if device_name else self.devices
        
        for device in devices_to_check:
            try:
                connection = self.connect_to_device(device)
                connection.enable()
                output = connection.send_command("show ip interface brief")
                results[device['name']] = {
                    'status': 'success',
                    'data': output,
                    'summary': self._parse_interface_status(output)
                }
                connection.disconnect()
            except Exception as e:
                results[device['name']] = {'status': 'error', 'error': str(e)}
        
        return results
    
    def check_ospf_database(self, device_name=None):
        """Check OSPF database"""
        results = {}
        devices_to_check = [d for d in self.devices if d['name'] == device_name] if device_name else self.devices
        
        for device in devices_to_check:
            try:
                connection = self.connect_to_device(device)
                connection.enable()
                output = connection.send_command("show ip ospf database")
                results[device['name']] = {
                    'status': 'success',
                    'data': output,
                    'summary': self._parse_ospf_database(output)
                }
                connection.disconnect()
            except Exception as e:
                results[device['name']] = {'status': 'error', 'error': str(e)}
        
        return results
    
    def check_bgp_routes(self, device_name=None):
        """Check BGP routes"""
        results = {}
        devices_to_check = [d for d in self.devices if d['name'] == device_name] if device_name else self.devices
        
        for device in devices_to_check:
            try:
                connection = self.connect_to_device(device)
                connection.enable()
                output = connection.send_command("show ip bgp")
                results[device['name']] = {
                    'status': 'success',
                    'data': output,
                    'summary': self._parse_bgp_routes(output)
                }
                connection.disconnect()
            except Exception as e:
                results[device['name']] = {'status': 'error', 'error': str(e)}
        
        return results
    
    def _parse_ospf_neighbors(self, output):
        """Parse OSPF neighbor output"""
        lines = output.split('\n')
        neighbors = []
        for line in lines:
            if 'FULL' in line or 'INIT' in line or 'EXSTART' in line:
                parts = line.split()
                if len(parts) >= 4:
                    neighbors.append({
                        'neighbor_id': parts[0],
                        'state': parts[2],
                        'interface': parts[-1] if len(parts) > 4 else 'Unknown'
                    })
        return {'neighbor_count': len(neighbors), 'neighbors': neighbors}
    
    def _parse_bgp_summary(self, output):
        """Parse BGP summary output"""
        lines = output.split('\n')
        neighbors = []
        for line in lines:
            if '65001' in line or '65002' in line or '65003' in line:
                parts = line.split()
                if len(parts) >= 4:
                    neighbors.append({
                        'neighbor': parts[0],
                        'as': parts[2],
                        'state': parts[-1]
                    })
        return {'neighbor_count': len(neighbors), 'neighbors': neighbors}
    
    def _parse_routing_table(self, output):
        """Parse routing table output"""
        lines = output.split('\n')
        routes = {'ospf': 0, 'bgp': 0, 'connected': 0, 'static': 0}
        for line in lines:
            if line.startswith('O '):
                routes['ospf'] += 1
            elif line.startswith('B '):
                routes['bgp'] += 1
            elif line.startswith('C '):
                routes['connected'] += 1
            elif line.startswith('S '):
                routes['static'] += 1
        return routes
    
    def _parse_interface_status(self, output):
        """Parse interface status output"""
        lines = output.split('\n')
        interfaces = {'up': 0, 'down': 0, 'admin_down': 0}
        for line in lines:
            if 'up' in line and 'up' in line.split()[-1]:
                interfaces['up'] += 1
            elif 'administratively down' in line:
                interfaces['admin_down'] += 1
            elif 'down' in line:
                interfaces['down'] += 1
        return interfaces
    
    def _parse_ospf_database(self, output):
        """Parse OSPF database output"""
        lines = output.split('\n')
        lsa_count = 0
        for line in lines:
            if 'Link ID' in line or 'ADV Router' in line:
                continue
            if line.strip() and not line.startswith(' ') and '.' in line:
                lsa_count += 1
        return {'lsa_count': lsa_count}
    
    def _parse_bgp_routes(self, output):
        """Parse BGP routes output"""
        lines = output.split('\n')
        route_count = 0
        for line in lines:
            if line.startswith('*') or line.startswith(' *'):
                route_count += 1
        return {'route_count': route_count}

# MCP Protocol Handler
async def handle_mcp_request(server, method, params=None):
    """Handle MCP requests"""
    if params is None:
        params = {}
    
    device_name = params.get('device_name')
    
    if method == 'get_ospf_neighbors':
        return server.get_ospf_neighbors(device_name)
    elif method == 'get_bgp_summary':
        return server.get_bgp_summary(device_name)
    elif method == 'get_routing_table':
        return server.get_routing_table(device_name)
    elif method == 'get_interface_status':
        return server.get_interface_status(device_name)
    elif method == 'check_ospf_database':
        return server.check_ospf_database(device_name)
    elif method == 'check_bgp_routes':
        return server.check_bgp_routes(device_name)
    else:
        return {'error': f'Unknown method: {method}'}

async def main():
    """Main MCP server loop"""
    server = NetworkMCPServer()
    
    # MCP initialization
    print(json.dumps({
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "get_ospf_neighbors": {
                        "description": "Get OSPF neighbor information from network devices",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "device_name": {"type": "string", "description": "Specific device name (CSR1, CSR2, CSR3) or all devices"}
                            }
                        }
                    },
                    "get_bgp_summary": {
                        "description": "Get BGP summary information from network devices",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "device_name": {"type": "string", "description": "Specific device name (CSR1, CSR2, CSR3) or all devices"}
                            }
                        }
                    },
                    "get_routing_table": {
                        "description": "Get routing table from network devices",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "device_name": {"type": "string", "description": "Specific device name (CSR1, CSR2, CSR3) or all devices"}
                            }
                        }
                    },
                    "get_interface_status": {
                        "description": "Get interface status from network devices",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "device_name": {"type": "string", "description": "Specific device name (CSR1, CSR2, CSR3) or all devices"}
                            }
                        }
                    },
                    "check_ospf_database": {
                        "description": "Check OSPF database information",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "device_name": {"type": "string", "description": "Specific device name (CSR1, CSR2, CSR3) or all devices"}
                            }
                        }
                    },
                    "check_bgp_routes": {
                        "description": "Check BGP routes information",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "device_name": {"type": "string", "description": "Specific device name (CSR1, CSR2, CSR3) or all devices"}
                            }
                        }
                    }
                }
            },
            "serverInfo": {
                "name": "network-monitor",
                "version": "1.0.0"
            }
        }
    }))
    
    # Handle incoming requests
    try:
        while True:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            try:
                request = json.loads(line.strip())
                method = request.get('method')
                params = request.get('params', {})
                request_id = request.get('id')
                
                if method in ['get_ospf_neighbors', 'get_bgp_summary', 'get_routing_table', 
                             'get_interface_status', 'check_ospf_database', 'check_bgp_routes']:
                    result = await handle_mcp_request(server, method, params)
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"}
                    }
                
                print(json.dumps(response))
                
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get('id') if 'request' in locals() else None,
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                }
                print(json.dumps(error_response))
    
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    asyncio.run(main())