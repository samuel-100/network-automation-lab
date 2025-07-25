#!/usr/bin/env python3
"""
Text-to-Voice Network Monitor
Type commands and get voice responses about your network
"""

import pyttsx3
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.mcp_network_server import NetworkMCPServer

class TextVoiceMonitor:
    def __init__(self):
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.9)
        
        # Initialize network server
        self.network_server = NetworkMCPServer()
        
        # Command mapping
        self.commands = {
            'ospf': self.get_ospf_neighbors,
            'bgp': self.get_bgp_summary,
            'routes': self.get_routing_table,
            'interfaces': self.get_interface_status,
            'database': self.check_ospf_database,
            'bgp-routes': self.check_bgp_routes,
            'status': self.get_network_overview,
            'help': self.show_help,
            'quit': self.quit_monitor,
            'exit': self.quit_monitor
        }
        
        self.running = True
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"🔊 {text}")
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"❌ TTS Error: {e}")
    
    def get_ospf_neighbors(self):
        """Get OSPF neighbor information with voice response"""
        try:
            result = self.network_server.get_ospf_neighbors()
            response = "OSPF Neighbors Report: "
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    neighbor_count = summary['neighbor_count']
                    response += f"{device} has {neighbor_count} OSPF neighbors. "
                    
                    if neighbor_count > 0:
                        for neighbor in summary['neighbors']:
                            state = neighbor['state'].replace('/', ' ')
                            response += f"Neighbor {neighbor['neighbor_id']} is {state}. "
                else:
                    response += f"{device} connection failed. "
            
            self.speak(response)
            
            # Also print detailed info
            print("\n📊 Detailed OSPF Information:")
            for device, data in result.items():
                print(f"\n{device}:")
                if data['status'] == 'success':
                    print(data['data'][:500] + "..." if len(data['data']) > 500 else data['data'])
                else:
                    print(f"  Error: {data.get('error', 'Unknown error')}")
            
        except Exception as e:
            error_msg = f"Error getting OSPF neighbors: {str(e)}"
            self.speak(error_msg)
            print(f"❌ {error_msg}")
    
    def get_bgp_summary(self):
        """Get BGP summary with voice response"""
        try:
            result = self.network_server.get_bgp_summary()
            response = "BGP Summary Report: "
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    neighbor_count = summary['neighbor_count']
                    response += f"{device} has {neighbor_count} BGP neighbors. "
                    
                    established_count = 0
                    for neighbor in summary['neighbors']:
                        if 'state' in neighbor and neighbor['state'].isdigit():
                            established_count += 1
                    
                    response += f"{established_count} neighbors are established. "
                else:
                    response += f"{device} connection failed. "
            
            self.speak(response)
            
            # Print detailed info
            print("\n📊 Detailed BGP Information:")
            for device, data in result.items():
                print(f"\n{device}:")
                if data['status'] == 'success':
                    print(data['data'][:500] + "..." if len(data['data']) > 500 else data['data'])
                else:
                    print(f"  Error: {data.get('error', 'Unknown error')}")
            
        except Exception as e:
            error_msg = f"Error getting BGP summary: {str(e)}"
            self.speak(error_msg)
            print(f"❌ {error_msg}")
    
    def get_routing_table(self):
        """Get routing table with voice response"""
        try:
            result = self.network_server.get_routing_table()
            response = "Routing Table Report: "
            
            total_ospf = 0
            total_bgp = 0
            total_connected = 0
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    total_ospf += summary['ospf']
                    total_bgp += summary['bgp']
                    total_connected += summary['connected']
                    
                    response += f"{device} has {summary['ospf']} OSPF routes, {summary['bgp']} BGP routes, and {summary['connected']} connected routes. "
            
            response += f"Network totals: {total_ospf} OSPF, {total_bgp} BGP, {total_connected} connected routes."
            self.speak(response)
            
        except Exception as e:
            error_msg = f"Error getting routing table: {str(e)}"
            self.speak(error_msg)
            print(f"❌ {error_msg}")
    
    def get_interface_status(self):
        """Get interface status with voice response"""
        try:
            result = self.network_server.get_interface_status()
            response = "Interface Status Report: "
            
            total_up = 0
            total_down = 0
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    total_up += summary['up']
                    total_down += summary['down']
                    
                    response += f"{device} has {summary['up']} interfaces up and {summary['down']} down. "
            
            response += f"Network totals: {total_up} interfaces up, {total_down} interfaces down."
            self.speak(response)
            
        except Exception as e:
            error_msg = f"Error getting interface status: {str(e)}"
            self.speak(error_msg)
            print(f"❌ {error_msg}")
    
    def check_ospf_database(self):
        """Check OSPF database with voice response"""
        try:
            result = self.network_server.check_ospf_database()
            response = "OSPF Database Report: "
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    lsa_count = summary['lsa_count']
                    response += f"{device} has {lsa_count} LSA entries. "
            
            self.speak(response)
            
        except Exception as e:
            error_msg = f"Error checking OSPF database: {str(e)}"
            self.speak(error_msg)
            print(f"❌ {error_msg}")
    
    def check_bgp_routes(self):
        """Check BGP routes with voice response"""
        try:
            result = self.network_server.check_bgp_routes()
            response = "BGP Routes Report: "
            
            total_routes = 0
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    route_count = summary['route_count']
                    total_routes += route_count
                    response += f"{device} has {route_count} BGP routes. "
            
            response += f"Total BGP routes in network: {total_routes}."
            self.speak(response)
            
        except Exception as e:
            error_msg = f"Error checking BGP routes: {str(e)}"
            self.speak(error_msg)
            print(f"❌ {error_msg}")
    
    def get_network_overview(self):
        """Get complete network overview"""
        self.speak("Getting complete network status overview")
        print("📊 Network Overview:")
        print("=" * 40)
        
        self.get_interface_status()
        print()
        self.get_ospf_neighbors()
        print()
        self.get_bgp_summary()
        print()
        self.get_routing_table()
    
    def show_help(self):
        """Show available commands"""
        help_text = """
🎤 Available Voice Commands:
- ospf          : Get OSPF neighbors
- bgp           : Get BGP summary  
- routes        : Get routing table
- interfaces    : Get interface status
- database      : Check OSPF database
- bgp-routes    : Check BGP routes
- status        : Complete network overview
- help          : Show this help
- quit/exit     : Exit the monitor
        """
        
        print(help_text)
        self.speak("Available commands: OSPF, BGP, routes, interfaces, database, BGP routes, status, help, and quit.")
    
    def quit_monitor(self):
        """Quit the monitor"""
        self.speak("Goodbye! Text to voice network monitor shutting down.")
        print("👋 Shutting down...")
        self.running = False
    
    def run(self):
        """Main loop"""
        print("🎤 Text-to-Voice Network Monitor")
        print("=" * 40)
        print("Type commands and get voice responses!")
        print("Type 'help' for available commands")
        print("=" * 40)
        
        self.speak("Text to voice network monitor started. Type help for commands.")
        
        while self.running:
            try:
                command = input("\n🎯 Enter command: ").strip().lower()
                
                if not command:
                    continue
                
                # Find matching command
                found = False
                for key, func in self.commands.items():
                    if key in command:
                        print(f"🔄 Executing: {key}")
                        func()
                        found = True
                        break
                
                if not found:
                    print(f"❓ Unknown command: {command}")
                    self.speak("Unknown command. Type help for available commands.")
                
            except KeyboardInterrupt:
                print("\n⚠️ Keyboard interrupt")
                self.quit_monitor()
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                self.speak("An error occurred. Please try again.")

def main():
    """Main function"""
    try:
        monitor = TextVoiceMonitor()
        monitor.run()
    except Exception as e:
        print(f"❌ Failed to start monitor: {e}")

if __name__ == "__main__":
    main()