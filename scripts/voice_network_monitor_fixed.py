#!/usr/bin/env python3
"""
Voice-Enabled Network Monitor (Cloud-Compatible)
Works with screen recording and voice-over for cloud environments
No physical microphone/speakers required - ALSA errors fixed
"""

import sys
import os
import time
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.mcp_network_server import NetworkMCPServer

class CloudVoiceNetworkMonitor:
    def __init__(self):
        print("🎤 Initializing Cloud Voice Network Monitor...")
        print("📱 Optimized for screen recording with voice-over")
        print("🌐 Perfect for Google Cloud and remote environments")
        
        # Initialize network server
        self.network_server = NetworkMCPServer()
        print("✅ Network server initialized")
        
        # Voice commands mapping (with typo tolerance)
        self.commands = {
            'ospf neighbors': self.get_ospf_neighbors,
            'ospf neighbour': self.get_ospf_neighbors,
            'ospf neighbor': self.get_ospf_neighbors,
            'ospf neigbor': self.get_ospf_neighbors,  # Common typo
            'ospf neigbors': self.get_ospf_neighbors,  # Common typo
            'ospf neigbour': self.get_ospf_neighbors,  # Common typo
            'show ospf': self.get_ospf_neighbors,
            'ospf status': self.get_ospf_neighbors,
            'ospf': self.get_ospf_neighbors,  # Short form
            'bgp summary': self.get_bgp_summary,
            'bgp status': self.get_bgp_summary,
            'show bgp': self.get_bgp_summary,
            'bgp neighbors': self.get_bgp_summary,
            'bgp neighbour': self.get_bgp_summary,
            'bgp neighbor': self.get_bgp_summary,
            'bgp neigbor': self.get_bgp_summary,
            'bgp': self.get_bgp_summary,  # Short form
            'routing table': self.get_routing_table,
            'show routes': self.get_routing_table,
            'routes': self.get_routing_table,
            'routing': self.get_routing_table,
            'interface status': self.get_interface_status,
            'show interfaces': self.get_interface_status,
            'interfaces': self.get_interface_status,
            'interface': self.get_interface_status,
            'ospf database': self.check_ospf_database,
            'bgp routes': self.check_bgp_routes,
            'network status': self.get_network_overview,
            'network overview': self.get_network_overview,
            'full status': self.get_network_overview,
            'network': self.get_network_overview,
            'help': self.show_help,
            'commands': self.show_help,
            'quit': self.quit_monitor,
            'exit': self.quit_monitor,
            'stop': self.quit_monitor,
            'bye': self.quit_monitor
        }
        
        self.running = True
    
    def display_response(self, title, content, voice_text):
        """Display formatted response for screen recording (no audio errors)"""
        print("\n" + "="*80)
        print(f"🎤 VOICE COMMAND RESPONSE: {title}")
        print("="*80)
        print(f"📢 VOICE OUTPUT: {voice_text}")
        print("-"*80)
        print(f"📊 DETAILED DATA:")
        print(content)
        print("="*80)
        
        # Pause for voice-over recording
        print("⏸️  [PAUSE FOR VOICE-OVER - Press Enter to continue]")
        input()
    
    def process_command(self, command):
        """Process voice command with enhanced fuzzy matching"""
        command = command.lower().strip()
        
        if not command:
            return
        
        print(f"\n🎤 VOICE INPUT: '{command.upper()}'")
        print("🔄 Processing command...")
        
        # Enhanced command matching with fuzzy logic
        matched_command = None
        matched_func = None
        
        # Direct match first
        for key, func in self.commands.items():
            if key in command:
                matched_command = key
                matched_func = func
                break
        
        # Fuzzy matching for common typos and variations
        if not matched_command:
            # OSPF variations
            if any(word in command for word in ['ospf', 'neighbor', 'neighbour', 'neigbor', 'neigbour']):
                matched_command = 'ospf neighbors'
                matched_func = self.get_ospf_neighbors
            # BGP variations
            elif any(word in command for word in ['bgp', 'summary', 'status', 'peer']):
                matched_command = 'bgp summary'
                matched_func = self.get_bgp_summary
            # Routing variations
            elif any(word in command for word in ['routing', 'route', 'table']):
                matched_command = 'routing table'
                matched_func = self.get_routing_table
            # Interface variations
            elif any(word in command for word in ['interface', 'int', 'status']):
                matched_command = 'interface status'
                matched_func = self.get_interface_status
            # Network variations
            elif any(word in command for word in ['network', 'overview', 'full']):
                matched_command = 'network overview'
                matched_func = self.get_network_overview
            # Help variations
            elif any(word in command for word in ['help', 'command', 'available']):
                matched_command = 'help'
                matched_func = self.show_help
            # Exit variations
            elif any(word in command for word in ['quit', 'exit', 'stop', 'bye', 'end']):
                matched_command = 'quit'
                matched_func = self.quit_monitor
        
        if matched_func:
            print(f"✅ Command recognized: {matched_command}")
            matched_func()
        else:
            error_msg = "Sorry, I didn't understand that command. Say 'help' to see available commands."
            self.display_response("COMMAND NOT RECOGNIZED", f"Input: {command}", error_msg)
    
    def get_ospf_neighbors(self):
        """Get OSPF neighbor information with voice response"""
        try:
            result = self.network_server.get_ospf_neighbors()
            
            # Build voice response
            voice_response = "OSPF Neighbors Report: "
            detailed_output = ""
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    neighbor_count = summary['neighbor_count']
                    
                    if neighbor_count == 0:
                        voice_response += f"{device} has no OSPF neighbors. "
                    elif neighbor_count == 1:
                        voice_response += f"{device} has 1 OSPF neighbor. "
                    else:
                        voice_response += f"{device} has {neighbor_count} OSPF neighbors. "
                    
                    # Add detailed information
                    detailed_output += f"\n{device} OSPF Neighbors:\n"
                    detailed_output += "-" * 40 + "\n"
                    
                    if neighbor_count > 0:
                        for neighbor in summary['neighbors']:
                            state = neighbor['state']
                            neighbor_id = neighbor['neighbor_id']
                            interface = neighbor.get('interface', 'Unknown')
                            
                            voice_response += f"Neighbor {neighbor_id} is in {state} state. "
                            detailed_output += f"  Neighbor ID: {neighbor_id}\n"
                            detailed_output += f"  State: {state}\n"
                            detailed_output += f"  Interface: {interface}\n\n"
                    else:
                        detailed_output += "  No neighbors found\n\n"
                else:
                    voice_response += f"Cannot connect to {device}. "
                    detailed_output += f"\n{device}: Connection failed\n\n"
            
            self.display_response("OSPF NEIGHBORS", detailed_output, voice_response)
            
        except Exception as e:
            error_msg = f"Error getting OSPF neighbors: {str(e)}"
            self.display_response("ERROR", str(e), error_msg)
    
    def get_bgp_summary(self):
        """Get BGP summary information with voice response"""
        try:
            result = self.network_server.get_bgp_summary()
            
            voice_response = "BGP Summary Report: "
            detailed_output = ""
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    neighbors = [n for n in summary['neighbors'] if 'neighbor' in n and n['neighbor'] != 'BGP']
                    neighbor_count = len(neighbors)
                    
                    if neighbor_count == 0:
                        voice_response += f"{device} has no BGP neighbors configured. "
                    else:
                        voice_response += f"{device} has {neighbor_count} BGP neighbors. "
                    
                    # Add detailed information
                    detailed_output += f"\n{device} BGP Summary:\n"
                    detailed_output += "-" * 40 + "\n"
                    
                    if neighbor_count > 0:
                        for neighbor in neighbors:
                            neighbor_ip = neighbor['neighbor']
                            as_number = neighbor.get('as', 'unknown')
                            state = neighbor.get('state', 'unknown')
                            
                            if state.isdigit():
                                voice_response += f"Neighbor {neighbor_ip} in AS {as_number} is established with {state} routes. "
                                detailed_output += f"  Neighbor: {neighbor_ip}\n"
                                detailed_output += f"  AS: {as_number}\n"
                                detailed_output += f"  State: Established ({state} routes)\n\n"
                            else:
                                voice_response += f"Neighbor {neighbor_ip} in AS {as_number} is in {state} state. "
                                detailed_output += f"  Neighbor: {neighbor_ip}\n"
                                detailed_output += f"  AS: {as_number}\n"
                                detailed_output += f"  State: {state}\n\n"
                    else:
                        detailed_output += "  No BGP neighbors configured\n\n"
                else:
                    voice_response += f"Cannot connect to {device}. "
                    detailed_output += f"\n{device}: Connection failed\n\n"
            
            self.display_response("BGP SUMMARY", detailed_output, voice_response)
            
        except Exception as e:
            error_msg = f"Error getting BGP summary: {str(e)}"
            self.display_response("ERROR", str(e), error_msg)
    
    def get_routing_table(self):
        """Get routing table information with voice response"""
        try:
            result = self.network_server.get_routing_table()
            
            voice_response = "Routing Table Report: "
            detailed_output = ""
            
            total_ospf = 0
            total_bgp = 0
            total_connected = 0
            total_static = 0
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    ospf_routes = summary['ospf']
                    bgp_routes = summary['bgp']
                    connected_routes = summary['connected']
                    static_routes = summary['static']
                    
                    total_ospf += ospf_routes
                    total_bgp += bgp_routes
                    total_connected += connected_routes
                    total_static += static_routes
                    
                    voice_response += f"{device} has {ospf_routes} OSPF routes, {bgp_routes} BGP routes, {connected_routes} connected routes, and {static_routes} static routes. "
                    
                    # Add detailed information
                    detailed_output += f"\n{device} Routing Table:\n"
                    detailed_output += "-" * 40 + "\n"
                    detailed_output += f"  OSPF Routes: {ospf_routes}\n"
                    detailed_output += f"  BGP Routes: {bgp_routes}\n"
                    detailed_output += f"  Connected Routes: {connected_routes}\n"
                    detailed_output += f"  Static Routes: {static_routes}\n\n"
                else:
                    voice_response += f"Cannot connect to {device}. "
                    detailed_output += f"\n{device}: Connection failed\n\n"
            
            voice_response += f"Network totals: {total_ospf} OSPF routes, {total_bgp} BGP routes, {total_connected} connected routes, and {total_static} static routes across all devices."
            
            detailed_output += f"\nNETWORK TOTALS:\n"
            detailed_output += "-" * 40 + "\n"
            detailed_output += f"Total OSPF Routes: {total_ospf}\n"
            detailed_output += f"Total BGP Routes: {total_bgp}\n"
            detailed_output += f"Total Connected Routes: {total_connected}\n"
            detailed_output += f"Total Static Routes: {total_static}\n"
            
            self.display_response("ROUTING TABLE", detailed_output, voice_response)
            
        except Exception as e:
            error_msg = f"Error getting routing table: {str(e)}"
            self.display_response("ERROR", str(e), error_msg)
    
    def get_interface_status(self):
        """Get interface status information with voice response"""
        try:
            result = self.network_server.get_interface_status()
            
            voice_response = "Interface Status Report: "
            detailed_output = ""
            
            total_up = 0
            total_down = 0
            total_admin_down = 0
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    up_interfaces = summary['up']
                    down_interfaces = summary['down']
                    admin_down_interfaces = summary['admin_down']
                    
                    total_up += up_interfaces
                    total_down += down_interfaces
                    total_admin_down += admin_down_interfaces
                    
                    voice_response += f"{device} has {up_interfaces} interfaces up, {down_interfaces} interfaces down, and {admin_down_interfaces} administratively down. "
                    
                    # Add detailed information
                    detailed_output += f"\n{device} Interface Status:\n"
                    detailed_output += "-" * 40 + "\n"
                    detailed_output += f"  Interfaces UP: {up_interfaces}\n"
                    detailed_output += f"  Interfaces DOWN: {down_interfaces}\n"
                    detailed_output += f"  Admin DOWN: {admin_down_interfaces}\n\n"
                else:
                    voice_response += f"Cannot connect to {device}. "
                    detailed_output += f"\n{device}: Connection failed\n\n"
            
            if total_down > 0:
                voice_response += f"Warning: {total_down} interfaces are down across the network. "
            else:
                voice_response += "All operational interfaces are up. "
            
            detailed_output += f"\nNETWORK TOTALS:\n"
            detailed_output += "-" * 40 + "\n"
            detailed_output += f"Total UP: {total_up}\n"
            detailed_output += f"Total DOWN: {total_down}\n"
            detailed_output += f"Total Admin DOWN: {total_admin_down}\n"
            
            self.display_response("INTERFACE STATUS", detailed_output, voice_response)
            
        except Exception as e:
            error_msg = f"Error getting interface status: {str(e)}"
            self.display_response("ERROR", str(e), error_msg)
    
    def check_ospf_database(self):
        """Check OSPF database with voice response"""
        try:
            result = self.network_server.check_ospf_database()
            
            voice_response = "OSPF Database Report: "
            detailed_output = ""
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    lsa_count = summary['lsa_count']
                    voice_response += f"{device} has {lsa_count} LSA entries in its OSPF database. "
                    
                    detailed_output += f"\n{device} OSPF Database:\n"
                    detailed_output += "-" * 40 + "\n"
                    detailed_output += f"  LSA Entries: {lsa_count}\n\n"
                else:
                    voice_response += f"Cannot connect to {device}. "
                    detailed_output += f"\n{device}: Connection failed\n\n"
            
            self.display_response("OSPF DATABASE", detailed_output, voice_response)
            
        except Exception as e:
            error_msg = f"Error checking OSPF database: {str(e)}"
            self.display_response("ERROR", str(e), error_msg)
    
    def check_bgp_routes(self):
        """Check BGP routes with voice response"""
        try:
            result = self.network_server.check_bgp_routes()
            
            voice_response = "BGP Routes Report: "
            detailed_output = ""
            total_routes = 0
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    route_count = summary['route_count']
                    total_routes += route_count
                    voice_response += f"{device} has {route_count} BGP routes. "
                    
                    detailed_output += f"\n{device} BGP Routes:\n"
                    detailed_output += "-" * 40 + "\n"
                    detailed_output += f"  Route Count: {route_count}\n\n"
                else:
                    voice_response += f"Cannot connect to {device}. "
                    detailed_output += f"\n{device}: Connection failed\n\n"
            
            voice_response += f"Total BGP routes in network: {total_routes}."
            
            detailed_output += f"\nNETWORK TOTAL:\n"
            detailed_output += "-" * 40 + "\n"
            detailed_output += f"Total BGP Routes: {total_routes}\n"
            
            self.display_response("BGP ROUTES", detailed_output, voice_response)
            
        except Exception as e:
            error_msg = f"Error checking BGP routes: {str(e)}"
            self.display_response("ERROR", str(e), error_msg)
    
    def get_network_overview(self):
        """Get complete network overview with voice response"""
        overview_text = "Getting complete network overview. This includes interface status, OSPF neighbors, BGP summary, and routing table information."
        
        self.display_response("NETWORK OVERVIEW", "Gathering comprehensive network data...", overview_text)
        
        print("📊 Gathering network information...")
        
        # Get all network information
        self.get_interface_status()
        self.get_ospf_neighbors()
        self.get_bgp_summary()
        self.get_routing_table()
        
        completion_text = "Network overview complete. All network components have been analyzed and reported."
        self.display_response("OVERVIEW COMPLETE", "All network data has been collected and presented.", completion_text)
    
    def show_help(self):
        """Show available voice commands"""
        help_content = """
AVAILABLE VOICE COMMANDS (Typo-Tolerant):

Network Status Commands:
• "OSPF neighbors" (or "OSPF neigbor", "Show OSPF") - Get OSPF neighbor information
• "BGP summary" (or "BGP status", "BGP") - Get BGP peer status
• "Routing table" (or "Routes", "Routing") - Get routing table analysis
• "Interface status" (or "Interfaces") - Get interface status
• "OSPF database" - Check OSPF LSA database
• "BGP routes" - Check BGP route table
• "Network status" (or "Network", "Full status") - Complete network overview

Control Commands:
• "Help" or "Commands" - Show this help message
• "Quit", "Exit", "Stop", or "Bye" - End session

FEATURES:
✅ Typo-tolerant command recognition
✅ Screen recording optimized
✅ Voice-over text provided
✅ No audio hardware required
✅ Google Cloud compatible

USAGE:
1. Type any command above (typos are OK!)
2. System processes and displays results
3. Voice-over text provided for recording
4. Press Enter after each response to continue
        """
        
        help_voice = "Available commands include: OSPF neighbors, BGP summary, routing table, interface status, OSPF database, BGP routes, network overview, help, and quit. The system is typo-tolerant and optimized for screen recording with voice-over support."
        
        self.display_response("HELP", help_content, help_voice)
    
    def quit_monitor(self):
        """Quit the voice monitor"""
        goodbye_text = "Goodbye! Cloud Voice Network Monitor shutting down. Thank you for using the voice-enabled network monitoring system."
        self.display_response("GOODBYE", "Session ended successfully.", goodbye_text)
        self.running = False
    
    def run(self):
        """Main loop for voice monitoring"""
        print("\n🎤 Cloud Voice Network Monitor Started!")
        print("=" * 80)
        print("📱 Optimized for screen recording with voice-over")
        print("🌐 Perfect for Google Cloud environments")
        print("💬 Type commands as if you're speaking them")
        print("🔊 Voice-over text provided for each response")
        print("✅ Typo-tolerant command recognition")
        print("🚫 No audio hardware required")
        print("📝 Type 'help' to see available commands")
        print("=" * 80)
        
        startup_text = "Cloud Voice Network Monitor started successfully. This system is optimized for screen recording with voice-over capabilities and includes typo-tolerant command recognition. Type help to see available commands."
        self.display_response("SYSTEM STARTUP", "Network monitoring system initialized and ready.", startup_text)
        
        while self.running:
            try:
                # Get text input (simulating voice input)
                user_input = input("\n🎤 VOICE COMMAND: ").strip()
                
                if user_input:
                    self.process_command(user_input)
                
            except KeyboardInterrupt:
                print("\n⚠️ Keyboard interrupt received")
                self.quit_monitor()
                break
            except EOFError:
                print("\n👋 Session ended")
                self.quit_monitor()
                break
            except Exception as e:
                error_msg = f"An unexpected error occurred: {str(e)}. Please try again."
                self.display_response("SYSTEM ERROR", str(e), error_msg)

def main():
    """Main function"""
    print("🚀 Starting Cloud Voice-Enabled Network Monitor")
    print("🎙️ Screen Recording & Voice-Over Compatible")
    print("☁️ Google Cloud Optimized")
    print("🔧 ALSA Audio Errors Fixed")
    print("=" * 80)
    
    try:
        monitor = CloudVoiceNetworkMonitor()
        monitor.run()
    except Exception as e:
        print(f"❌ Failed to start voice monitor: {e}")

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()