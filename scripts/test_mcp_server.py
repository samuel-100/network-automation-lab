#!/usr/bin/env python3
"""
Test script for MCP Network Server
Tests all available MCP tools
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.mcp_network_server import NetworkMCPServer
import asyncio

async def test_mcp_functions():
    """Test all MCP server functions"""
    print("🧪 Testing MCP Network Server Functions")
    print("=" * 50)
    
    server = NetworkMCPServer()
    
    # Test functions
    test_functions = [
        ('get_ospf_neighbors', 'OSPF Neighbors'),
        ('get_bgp_summary', 'BGP Summary'),
        ('get_routing_table', 'Routing Table'),
        ('get_interface_status', 'Interface Status'),
        ('check_ospf_database', 'OSPF Database'),
        ('check_bgp_routes', 'BGP Routes')
    ]
    
    for func_name, description in test_functions:
        print(f"\n🔍 Testing {description}...")
        try:
            if func_name == 'get_ospf_neighbors':
                result = server.get_ospf_neighbors('CSR1')
            elif func_name == 'get_bgp_summary':
                result = server.get_bgp_summary('CSR1')
            elif func_name == 'get_routing_table':
                result = server.get_routing_table('CSR1')
            elif func_name == 'get_interface_status':
                result = server.get_interface_status('CSR1')
            elif func_name == 'check_ospf_database':
                result = server.check_ospf_database('CSR1')
            elif func_name == 'check_bgp_routes':
                result = server.check_bgp_routes('CSR1')
            
            if 'CSR1' in result and result['CSR1']['status'] == 'success':
                print(f"✅ {description}: SUCCESS")
                if 'summary' in result['CSR1']:
                    print(f"   Summary: {result['CSR1']['summary']}")
            else:
                print(f"❌ {description}: FAILED")
                if 'CSR1' in result and 'error' in result['CSR1']:
                    print(f"   Error: {result['CSR1']['error']}")
                    
        except Exception as e:
            print(f"❌ {description}: EXCEPTION - {str(e)}")
    
    print(f"\n✅ MCP Server testing completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_functions())