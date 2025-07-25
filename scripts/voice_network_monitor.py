#!/usr/bin/env python3
"""
Voice-Enabled Network Monitor
Real voice input and speech output for network monitoring
"""

import speech_recognition as sr
import pyttsx3
import pyaudio
import threading
import time
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.mcp_network_server import NetworkMCPServer

class VoiceNetworkMonitor:
    def __init__(self):
        print("🎤 Initializing Voice Network Monitor...")
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Initialize text-to-speech
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.9)  # Volume level
            print("✅ Text-to-speech initialized")
        except Exception as e:
            print(f"❌ TTS initialization failed: {e}")
            self.tts_engine = None
        
        # Initialize microphone
        try:
            # List available microphones
            print("🎙️ Available microphones:")
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f"  {index}: {name}")
            
            # Use default microphone
            self.microphone = sr.Microphone()
            print("✅ Microphone initialized")
        except Exception as e:
            print(f"❌ Microphone initialization failed: {e}")
            self.microphone = None
        
        # Initialize network server
        self.network_server = NetworkMCPServer()
        print("✅ Network server initialized")
        
        # Voice commands mapping
        self.commands = {
            'ospf neighbors': self.get_ospf_neighbors,
            'ospf neighbour': self.get_ospf_neighbors,
            'show ospf': self.get_ospf_neighbors,
            'ospf status': self.get_ospf_neighbors,
            'bgp summary': self.get_bgp_summary,
            'bgp status': self.get_bgp_summary,
            'show bgp': self.get_bgp_summary,
            'bgp neighbors': self.get_bgp_summary,
            'routing table': self.get_routing_table,
            'show routes': self.get_routing_table,
            'routes': self.get_routing_table,
            'interface status': self.get_interface_status,
            'show interfaces': self.get_interface_status,
            'interfaces': self.get_interface_status,
            'ospf database': self.check_ospf_database,
            'bgp routes': self.check_bgp_routes,
            'network status': self.get_network_overview,
            'network overview': self.get_network_overview,
            'full status': self.get_network_overview,
            'help': self.show_help,
            'commands': self.show_help,
            'quit': self.quit_monitor,
            'exit': self.quit_monitor,
            'stop': self.quit_monitor,
            'bye': self.quit_monitor
        }
        
        self.running = True
        self.listening = False
        
        # Calibrate microphone if available
        if self.microphone:
            self.calibrate_microphone()
        else:
            print("⚠️ No microphone available - running in text mode")
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        print("🎤 Calibrating microphone for ambient noise...")
        self.speak("Calibrating microphone. Please wait.")
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("✅ Microphone calibrated!")
        self.speak("Microphone calibrated. Ready for voice commands.")
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"🔊 Speaking: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen_for_command(self):
        """Listen for voice commands"""
        try:
            with self.microphone as source:
                print("🎤 Listening for command...")
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
            
            print("🔄 Processing speech...")
            # Recognize speech using Google Speech Recognition
            command = self.recognizer.recognize_google(audio).lower()
            print(f"📝 Recognized: '{command}'")
            return command
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand audio")
            return "unknown"
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return "error"
    
    def process_command(self, command):
        """Process recognized voice command"""
        if not command or command in [None, "unknown", "error"]:
            return
        
        # Find matching command
        for key, func in self.commands.items():
            if key in command:
                print(f"🎯 Executing: {key}")
                self.speak(f"Getting {key}")
                func()
                return
        
        # If no command matched
        print(f"❓ Unknown command: {command}")
        self.speak("Sorry, I didn't recognize that command. Say help for available commands.")
    
    def get_ospf_neighbors(self):
        """Get OSPF neighbor information"""
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
                            response += f"Neighbor {neighbor['neighbor_id']} is in {neighbor['state']} state. "
                else:
                    response += f"{device} connection failed. "
            
            self.speak(response)
            print(f"📊 OSPF Report: {response}")
            
        except Exception as e:
            error_msg = f"Error getting OSPF neighbors: {str(e)}"
            self.speak(error_msg)
            print(f"❌ {error_msg}")
    
    def get_bgp_summary(self):
        """Get BGP summary information"""
        try:
            result = self.network_server.get_bgp_summary()
            response = "BGP Summary Report: "
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    neighbor_count = summary['neighbor_count']
                    response += f"{device} has {neighbor_count} BGP neighbors configured. "
                    
                    for neighbor in summary['neighbors']:
                        if 'state' in neighbor:
                            response += f"Neighbor {neighbor['neighbor']} in AS {neighbor['as']} is {neighbor['state']}. "
                else:
                    response += f"{device} connection failed. "
            
            self.speak(response)
            print(f"📊 BGP Report: {response}")
            
        except Exception as e:
            error_msg = f"Error getting BGP summary: {str(e)}"
            self.speak(error_msg)
            print(f"❌ {error_msg}")
    
    def get_routing_table(self):
        """Get routing table information"""
        try:
            result = self.network_server.get_routing_table()
            response = "Routing Table Report: "
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    response += f"{device} has {summary['ospf']} OSPF routes, {summary['bgp']} BGP routes, {summary['connected']} connected routes, and {summary['static']} static routes. "
                else:
                    response += f"{device} connection failed. "
            
            self.speak(response)
            print(f"📊 Routing Report: {response}")
            
        except Exception as e:
            error_msg = f"Error getting routing table: {str(e)}"
            self.speak(error_msg)
            print(f"❌ {error_msg}")
    
    def get_interface_status(self):
        """Get interface status information"""
        try:
            result = self.network_server.get_interface_status()
            response = "Interface Status Report: "
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    response += f"{device} has {summary['up']} interfaces up, {summary['down']} interfaces down, and {summary['admin_down']} administratively down. "
                else:
                    response += f"{device} connection failed. "
            
            self.speak(response)
            print(f"📊 Interface Report: {response}")
            
        except Exception as e:
            error_msg = f"Error getting interface status: {str(e)}"
            self.speak(error_msg)
            print(f"❌ {error_msg}")
    
    def check_ospf_database(self):
        """Check OSPF database"""
        try:
            result = self.network_server.check_ospf_database()
            response = "OSPF Database Report: "
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    lsa_count = summary['lsa_count']
                    response += f"{device} has {lsa_count} LSA entries in OSPF database. "
                else:
                    response += f"{device} connection failed. "
            
            self.speak(response)
            print(f"📊 OSPF Database Report: {response}")
            
        except Exception as e:
            error_msg = f"Error checking OSPF database: {str(e)}"
            self.speak(error_msg)
            print(f"❌ {error_msg}")
    
    def check_bgp_routes(self):
        """Check BGP routes"""
        try:
            result = self.network_server.check_bgp_routes()
            response = "BGP Routes Report: "
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    route_count = summary['route_count']
                    response += f"{device} has {route_count} BGP routes. "
                else:
                    response += f"{device} connection failed. "
            
            self.speak(response)
            print(f"📊 BGP Routes Report: {response}")
            
        except Exception as e:
            error_msg = f"Error checking BGP routes: {str(e)}"
            self.speak(error_msg)
            print(f"❌ {error_msg}")
    
    def get_network_overview(self):
        """Get complete network overview"""
        self.speak("Getting complete network overview")
        print("📊 Getting network overview...")
        
        self.get_interface_status()
        time.sleep(1)
        self.get_ospf_neighbors()
        time.sleep(1)
        self.get_bgp_summary()
    
    def show_help(self):
        """Show available voice commands"""
        help_text = """Available voice commands:
        - OSPF neighbors or Show OSPF
        - BGP summary or BGP status
        - Routing table or Show routes
        - Interface status or Show interfaces
        - OSPF database
        - BGP routes
        - Network status (complete overview)
        - Help (show this message)
        - Quit, Exit, or Stop (end session)
        """
        
        print(help_text)
        self.speak("Available commands include: OSPF neighbors, BGP summary, routing table, interface status, OSPF database, BGP routes, network status, help, and quit.")
    
    def quit_monitor(self):
        """Quit the voice monitor"""
        self.speak("Goodbye! Voice network monitor shutting down.")
        print("👋 Shutting down voice network monitor...")
        self.running = False
    
    def run(self):
        """Main loop for voice monitoring"""
        print("🎤 Voice Network Monitor Started!")
        print("=" * 50)
        self.speak("Voice network monitor started. Say help for available commands.")
        
        while self.running:
            try:
                command = self.listen_for_command()
                if command:
                    self.process_command(command)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\n⚠️ Keyboard interrupt received")
                self.quit_monitor()
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                self.speak("An error occurred. Please try again.")

def main():
    """Main function"""
    print("🚀 Starting Voice-Enabled Network Monitor")
    print("📋 Make sure your microphone is connected and working")
    print("🔊 Make sure your speakers/headphones are connected")
    print("=" * 60)
    
    try:
        monitor = VoiceNetworkMonitor()
        monitor.run()
    except Exception as e:
        print(f"❌ Failed to start voice monitor: {e}")
        print("💡 Make sure you have a microphone connected and audio drivers installed")

if __name__ == "__main__":
    main()