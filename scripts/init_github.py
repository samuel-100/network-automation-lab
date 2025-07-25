#!/usr/bin/env python3
"""
GitHub Repository Initialization Script
Prepares the project for GitHub upload
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} failed")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {str(e)}")
        return False
    return True

def main():
    print("🚀 Initializing GitHub Repository for Network Automation Lab")
    print("=" * 60)
    
    # Check if git is installed
    if not run_command("git --version", "Checking Git installation"):
        print("❌ Git is not installed. Please install Git first.")
        sys.exit(1)
    
    # Initialize git repository
    if not os.path.exists('.git'):
        run_command("git init", "Initializing Git repository")
    else:
        print("✅ Git repository already exists")
    
    # Create .gitignore file
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Environment variables
.env

# Backup files
backups/
*.bak

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Network device configs (if sensitive)
# configs/production_devices.yaml
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore file")
    
    # Add files to git
    run_command("git add .", "Adding files to Git")
    
    # Create initial commit
    run_command('git commit -m "Initial commit: Network Automation Lab with OSPF/BGP and MCP integration"', 
                "Creating initial commit")
    
    # Show git status
    run_command("git status", "Checking Git status")
    
    print("\n🎉 Repository initialized successfully!")
    print("\n📋 Next steps:")
    print("1. Create a new repository on GitHub")
    print("2. Add the remote origin:")
    print("   git remote add origin https://github.com/samuel-100/network-automation-lab.git")
    print("3. Push to GitHub:")
    print("   git branch -M main")
    print("   git push -u origin main")
    print("\n🔗 GitHub repository creation URL:")
    print("   https://github.com/new")

if __name__ == "__main__":
    main()