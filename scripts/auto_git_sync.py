#!/usr/bin/env python3
"""
Automatic Git Sync Script
Automatically commits and pushes changes to GitHub
"""

import subprocess
import time
import os
from datetime import datetime

def run_git_command(command, description):
    """Run a git command and handle errors"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            print(f"✅ {description}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {str(e)}")
        return False

def auto_sync_to_github():
    """Automatically sync changes to GitHub"""
    print("🔄 Starting automatic GitHub sync...")
    print("=" * 50)
    
    # Add all changes
    if not run_git_command("git add .", "Adding all changes"):
        return False
    
    # Check if there are changes to commit
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        print("ℹ️ No changes to commit")
        return True
    
    # Create commit message with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Auto-sync: Voice network monitor updates - {timestamp}"
    
    # Commit changes
    if not run_git_command(f'git commit -m "{commit_message}"', "Committing changes"):
        return False
    
    # Push to GitHub
    if not run_git_command("git push origin main", "Pushing to GitHub"):
        return False
    
    print("🎉 Successfully synced to GitHub!")
    return True

def watch_and_sync(interval=300):  # 5 minutes default
    """Watch for changes and auto-sync"""
    print(f"👀 Watching for changes every {interval} seconds...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            auto_sync_to_github()
            print(f"⏰ Next sync in {interval} seconds...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n🛑 Auto-sync stopped by user")

def main():
    """Main function"""
    print("🚀 Git Auto-Sync Tool")
    print("=" * 30)
    print("1. Sync now")
    print("2. Start auto-sync (every 5 minutes)")
    print("3. Custom interval auto-sync")
    print("4. Exit")
    print("=" * 30)
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == '1':
        auto_sync_to_github()
    elif choice == '2':
        watch_and_sync(300)  # 5 minutes
    elif choice == '3':
        try:
            interval = int(input("Enter sync interval in seconds: "))
            watch_and_sync(interval)
        except ValueError:
            print("❌ Invalid interval")
    elif choice == '4':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()