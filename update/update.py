#!/usr/bin/env python3

import subprocess
import socket
import os
from time import sleep

def is_connected():
    try:
        # Connect to Google's DNS server on port 53 (non-HTTP)
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except (OSError, socket.timeout):
        return False

def git_pull():
    try:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_dir = os.path.dirname(script_dir)
        
        # Change to the script's directory
        os.chdir(script_dir)
        
        # Ensure the directory is a git repository
        if not os.path.exists(os.path.join(script_dir, '.git')):
            raise Exception("This directory is not a Git repository.")
        
        # Run 'git pull'
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True, check=True)
        
        print("Git Pull Output:")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print("Error during git pull:", e.stderr)
    except Exception as e:
        print("Error:", str(e))


if(is_connected()):
    git_pull()
else:
    sleep(20)
    git_pull()