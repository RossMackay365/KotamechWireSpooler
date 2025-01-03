#!/usr/bin/env python3

import subprocess
import os

def git_pull():
    try:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
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

git_pull()