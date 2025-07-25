#!/usr/bin/env python3
"""
Web-Based Voice Interface for Network Monitoring
Uses browser's built-in speech recognition
"""

from flask import Flask, render_template, request, jsonify
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.mcp_network_server import NetworkMCPServer

app = Flask(__name__)
network_server = NetworkMCPServer()

@app.route('/')
def index():
    return render_template('voice_interface.html')

@app.route('/process_command', methods=['POST'])
def process_command():
    data = request.json
    command = data.get('command', '').lower().strip()
    
    try:
        if 'ospf' in command and ('neighbor' in command or 'neigbor' in command):
            result = network_server.get_ospf_neighbors()
            return jsonify({
                'success': True,
                'type': 'ospf_neighbors',
                'data': result,
                'voice_response': format_ospf_response(result)
            })
        
        elif 'bgp' in command:
            result = network_server.get_bgp_summary()
            return jsonify({
                'success': True,
                'type': 'bgp_summary',
                'data': result,
                'voice_response': format_bgp_response(result)
            })
        
        elif 'routing' in command or 'route' in command:
            result = network_server.get_routing_table()
            return jsonify({
                'success': True,
                'type': 'routing_table',
                'data': result,
                'voice_response': format_routing_response(result)
            })
        
        elif 'interface' in command:
            result = network_server.get_interface_status()
            return jsonify({
                'success': True,
                'type': 'interface_status',
                'data': result,
                'voice_response': format_interface_response(result)
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'Command not recognized. Try: OSPF neighbors, BGP summary, routing table, or interface status'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def format_ospf_response(result):
    response = "OSPF Neighbors Report: "
    for device, data in result.items():
        if data['status'] == 'success':
            count = data['summary']['neighbor_count']
            response += f"{device} has {count} OSPF neighbors. "
            for neighbor in data['summary']['neighbors']:
                response += f"Neighbor {neighbor['neighbor_id']} is in {neighbor['state']} state. "
    return response

def format_bgp_response(result):
    response = "BGP Summary Report: "
    for device, data in result.items():
        if data['status'] == 'success':
            neighbors = [n for n in data['summary']['neighbors'] if 'neighbor' in n and n['neighbor'] != 'BGP']
            response += f"{device} has {len(neighbors)} BGP neighbors. "
    return response

def format_routing_response(result):
    response = "Routing Table Report: "
    for device, data in result.items():
        if data['status'] == 'success':
            summary = data['summary']
            response += f"{device} has {summary['ospf']} OSPF routes, {summary['bgp']} BGP routes, {summary['connected']} connected routes. "
    return response

def format_interface_response(result):
    response = "Interface Status Report: "
    for device, data in result.items():
        if data['status'] == 'success':
            summary = data['summary']
            response += f"{device} has {summary['up']} interfaces up, {summary['down']} interfaces down. "
    return response

if __name__ == '__main__':
    app.run(host='0.