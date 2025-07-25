#!/usr/bin/env python3
"""
Network Alert System with Audio Notifications
Monitors network and provides audio alerts for issues
"""

import pyttsx3
import time
import sys
import os
from datetime import datetime
import threading

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.mcp_network_server import NetworkMCPServer

class NetworkAlertSystem:
    def __init__(self):
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.9)
        
        # Initialize network server
        self.network_server = NetworkMCPServer()
        
        # Alert thresholds
        self.thresholds = {
            'ospf_neighbors_min': 1,  # Minimum OSPF neighbors expected
            'interfaces_down_max': 1,  # Maximum interfaces allowed to be down
            'bgp_neighbors_min': 1     # Minimum BGP neighbors expected
        }
        
        # Alert history to prevent spam
        self.alert_history = {}
        self.alert_cooldown = 300  # 5 minutes cooldown between same alerts
        
        self.monitoring = False
    
    def speak_alert(self, message, priority="normal"):
        """Speak alert message with priority"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if priority == "critical":
            alert_prefix = "CRITICAL ALERT! "
            print(f"🚨 [{timestamp}] CRITICAL: {message}")
        elif priority == "warning":
            alert_prefix = "WARNING! "
            print(f"⚠️ [{timestamp}] WARNING: {message}")
        else:
            alert_prefix = ""
            print(f"ℹ️ [{timestamp}] INFO: {message}")
        
        full_message = alert_prefix + message
        
        # Speak the alert
        self.tts_engine.say(full_message)
        self.tts_engine.runAndWait()
    
    def should_alert(self, alert_key):
        """Check if we should send alert (cooldown logic)"""
        current_time = time.time()
        
        if alert_key in self.alert_history:
            time_since_last = current_time - self.alert_history[alert_key]
            if time_since_last < self.alert_cooldown:
                return False
        
        self.alert_history[alert_key] = current_time
        return True
    
    def check_ospf_health(self):
        """Check OSPF health and generate alerts"""
        try:
            result = self.network_server.get_ospf_neighbors()
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    neighbor_count = summary['neighbor_count']
                    
                    # Check for insufficient neighbors
                    if neighbor_count < self.thresholds['ospf_neighbors_min']:
                        alert_key = f"ospf_neighbors_low_{device}"
                        if self.should_alert(alert_key):
                            self.speak_alert(
                                f"{device} has only {neighbor_count} OSPF neighbors. Expected at least {self.thresholds['ospf_neighbors_min']}",
                                "warning"
                            )
                    
                    # Check neighbor states
                    for neighbor in summary['neighbors']:
                        if 'FULL' not in neighbor['state']:
                            alert_key = f"ospf_neighbor_down_{device}_{neighbor['neighbor_id']}"
                            if self.should_alert(alert_key):
                                self.speak_alert(
                                    f"{device} OSPF neighbor {neighbor['neighbor_id']} is in {neighbor['state']} state",
                                    "critical"
                                )
                
                else:
                    alert_key = f"device_unreachable_{device}"
                    if self.should_alert(alert_key):
                        self.speak_alert(f"Cannot connect to {device}", "critical")
        
        except Exception as e:
            print(f"❌ Error checking OSPF health: {e}")
    
    def check_bgp_health(self):
        """Check BGP health and generate alerts"""
        try:
            result = self.network_server.get_bgp_summary()
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    
                    # Check BGP neighbor states
                    for neighbor in summary['neighbors']:
                        if 'neighbor' in neighbor and 'state' in neighbor:
                            if neighbor['state'] in ['Idle', 'Active', 'Connect']:
                                alert_key = f"bgp_neighbor_down_{device}_{neighbor['neighbor']}"
                                if self.should_alert(alert_key):
                                    self.speak_alert(
                                        f"{device} BGP neighbor {neighbor['neighbor']} is in {neighbor['state']} state",
                                        "warning"
                                    )
        
        except Exception as e:
            print(f"❌ Error checking BGP health: {e}")
    
    def check_interface_health(self):
        """Check interface health and generate alerts"""
        try:
            result = self.network_server.get_interface_status()
            
            for device, data in result.items():
                if data['status'] == 'success':
                    summary = data['summary']
                    down_interfaces = summary['down']
                    
                    if down_interfaces > self.thresholds['interfaces_down_max']:
                        alert_key = f"interfaces_down_{device}"
                        if self.should_alert(alert_key):
                            self.speak_alert(
                                f"{device} has {down_interfaces} interfaces down",
                                "warning"
                            )
        
        except Exception as e:
            print(f"❌ Error checking interface health: {e}")
    
    def run_health_check(self):
        """Run complete health check"""
        print(f"🔍 [{datetime.now().strftime('%H:%M:%S')}] Running network health check...")
        
        self.check_interface_health()
        time.sleep(1)
        self.check_ospf_health()
        time.sleep(1)
        self.check_bgp_health()
        
        print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Health check completed")
    
    def start_monitoring(self, interval=60):
        """Start continuous network monitoring"""
        self.monitoring = True
        self.speak_alert("Network monitoring started", "normal")
        
        print(f"🚀 Network Alert System Started!")
        print(f"📊 Monitoring interval: {interval} seconds")
        print(f"🔔 Alert cooldown: {self.alert_cooldown} seconds")
        print("=" * 50)
        
        try:
            while self.monitoring:
                self.run_health_check()
                
                # Wait for next check
                for i in range(interval):
                    if not self.monitoring:
                        break
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Monitoring stopped by user")
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring = False
        self.speak_alert("Network monitoring stopped", "normal")
        print("👋 Network monitoring stopped")
    
    def test_alerts(self):
        """Test all alert types"""
        print("🧪 Testing alert system...")
        
        self.speak_alert("Testing normal alert", "normal")
        time.sleep(2)
        self.speak_alert("Testing warning alert", "warning")
        time.sleep(2)
        self.speak_alert("Testing critical alert", "critical")
        
        print("✅ Alert test completed")

def main():
    """Main function"""
    print("🚀 Network Alert System")
    print("=" * 30)
    print("Commands:")
    print("1. Start monitoring (continuous)")
    print("2. Run single health check")
    print("3. Test alerts")
    print("4. Quit")
    print("=" * 30)
    
    alert_system = NetworkAlertSystem()
    
    while True:
        try:
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '1':
                interval = input("Enter monitoring interval in seconds (default 60): ").strip()
                interval = int(interval) if interval.isdigit() else 60
                
                # Run monitoring in separate thread
                monitor_thread = threading.Thread(
                    target=alert_system.start_monitoring,
                    args=(interval,)
                )
                monitor_thread.daemon = True
                monitor_thread.start()
                
                print("Press Enter to stop monitoring...")
                input()
                alert_system.stop_monitoring()
                
            elif choice == '2':
                alert_system.run_health_check()
                
            elif choice == '3':
                alert_system.test_alerts()
                
            elif choice == '4':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()