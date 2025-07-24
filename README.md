# Network Automation Lab - OSPF & BGP with MCP Integration

A comprehensive network automation project featuring OSPF and BGP configuration and monitoring using Cisco CSR routers with Model Context Protocol (MCP) integration for real-time network insights.

## 🏗️ Network Topology

```
CSR1 (1.1.1.1/32) - AS65001
├── Gi2: 10.1.12.1/24 ↔ CSR2
└── Gi3: 10.1.13.1/24 ↔ CSR3

CSR2 (2.2.2.2/32) - AS65002  
├── Gi2: 10.1.12.2/24 ↔ CSR1
└── Gi3: 10.2.23.2/24 ↔ CSR3

CSR3 (3.3.3.3/32) - AS65003
├── Gi2: 10.1.13.3/24 ↔ CSR1  
└── Gi3: 10.2.23.3/24 ↔ CSR2
```

## 🚀 Features

- **Automated Network Configuration**: OSPF and BGP setup across multiple routers
- **Real-time Monitoring**: MCP server for live network status queries
- **Protocol Analysis**: OSPF neighbor states, BGP summary, routing tables
- **Interface Management**: Monitor interface status and connectivity
- **Scalable Architecture**: Easy to extend for additional devices and protocols

## 📋 Prerequisites

- Python 3.8+
- EVE-NG or similar network emulation platform
- Cisco CSR 1000v routers (or compatible devices)
- Network connectivity to management interfaces

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/network-automation-lab.git
cd network-automation-lab
```

2. **Create virtual environment**:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure device credentials**:
Edit `configs/network_devices.yaml` with your device details.

## 🔧 Quick Start

### 1. Test Connectivity
```bash
python scripts/test_connectivity.py
```

### 2. Configure Network
```bash
python scripts/configure_network.py
```

### 3. Start MCP Server
```bash
python scripts/mcp_network_server.py
```

## 🔍 MCP Integration

The project includes a Model Context Protocol (MCP) server that provides real-time network information. Available tools:

- `get_ospf_neighbors` - OSPF neighbor information
- `get_bgp_summary` - BGP peer status and summary
- `get_routing_table` - Complete routing table analysis
- `get_interface_status` - Interface status and statistics
- `check_ospf_database` - OSPF LSA database information
- `check_bgp_routes` - BGP route table details

### MCP Configuration

Add to your `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "network-monitor": {
      "command": ".venv/bin/python",
      "args": ["scripts/mcp_network_server.py"],
      "env": {
        "PYTHONPATH": ".",
        "NETWORK_CONFIG_PATH": "configs/network_devices.yaml"
      },
      "disabled": false,
      "autoApprove": [
        "get_ospf_neighbors",
        "get_bgp_summary",
        "get_routing_table",
        "get_interface_status",
        "check_ospf_database",
        "check_bgp_routes"
      ]
    }
  }
}
```

## 📊 Usage Examples

### Query OSPF Neighbors
```python
# Via MCP: get_ospf_neighbors
# Returns neighbor states, router IDs, and interface information
```

### Check BGP Status
```python
# Via MCP: get_bgp_summary  
# Returns peer status, AS numbers, and session states
```

### Monitor Routing Table
```python
# Via MCP: get_routing_table
# Returns route counts by protocol (OSPF, BGP, Connected, Static)
```

## 📁 Project Structure

```
network-automation-lab/
├── scripts/
│   ├── configure_network.py      # Network configuration automation
│   ├── test_connectivity.py      # Connectivity testing
│   ├── mcp_network_server.py     # MCP server for real-time monitoring
│   └── __init__.py
├── configs/
│   └── network_devices.yaml      # Device configuration
├── .kiro/
│   └── settings/
│       └── mcp.json              # MCP server configuration
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🔧 Configuration Details

### OSPF Configuration
- **Process ID**: 1
- **Area**: 0 (Backbone)
- **Router IDs**: Loopback interfaces (1.1.1.1, 2.2.2.2, 3.3.3.3)
- **Networks**: All point-to-point links and loopbacks

### BGP Configuration  
- **AS Numbers**: 65001, 65002, 65003
- **Peering**: iBGP via loopback interfaces
- **Router IDs**: Same as OSPF (loopback addresses)

## 🚨 Troubleshooting

### Common Issues

1. **Connection Timeout**: Verify device IP addresses and credentials
2. **OSPF Neighbors Down**: Check interface status and network connectivity
3. **BGP Sessions Not Established**: Verify AS numbers and loopback reachability
4. **MCP Server Not Responding**: Check Python path and dependencies

### Debug Commands

```bash
# Test individual device connectivity
python -c "from netmiko import ConnectHandler; print(ConnectHandler({'device_type': 'cisco_xe', 'host': '192.168.100.10', 'username': 'admin', 'password': 'cisco'}).send_command('show version'))"

# Verify OSPF status
# Via MCP: get_ospf_neighbors with device_name: "CSR1"

# Check BGP peers
# Via MCP: get_bgp_summary
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Netmiko library for network device automation
- Model Context Protocol (MCP) for real-time integration
- EVE-NG for network emulation platform
- Cisco for CSR 1000v router images

## 📞 Support

For questions and support:
- Create an issue in this repository
- Check the troubleshooting section
- Review the configuration examples

---

**Happy Networking! 🌐**