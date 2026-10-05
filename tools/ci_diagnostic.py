import socket
import urllib.request
import subprocess
import sys

def check_dns(host):
    print(f"--- Checking DNS for {host} ---")
    try:
        addr = socket.gethostbyname(host)
        print(f"SUCCESS: {host} resolved to {addr}")
    except Exception as e:
        print(f"FAILURE: Could not resolve {host}: {e}")

def check_url(url):
    print(f"--- Checking URL Reachability: {url} ---")
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            print(f"SUCCESS: {url} returned {response.status}")
    except Exception as e:
        print(f"FAILURE: Could not reach {url}: {e}")

def check_lxd_network():
    print("--- Checking LXD Network Config ---")
    try:
        # Check for default bridge configuration
        res = subprocess.run(["lxc", "network", "show", "lxdbr0"], 
                             capture_output=True, text=True)
        if res.returncode == 0:
            print(res.stdout)
        else:
            print(f"LXD bridge 'lxdbr0' not found or lxc error: {res.stderr}")
    except FileNotFoundError:
        print("LXD command not found.")

if __name__ == "__main__":
    print("=== CI Environment Diagnostic Starting ===")
    
    # Check general connectivity
    check_dns("archive.ubuntu.com")
    check_dns("google.com")
    
    # Check Resolute mirror specifically
    # If this 404s, the release is not published or the URL template is wrong
    check_url("http://archive.ubuntu.com/ubuntu/dists/resolute/InRelease")
    check_url("http://security.ubuntu.com/ubuntu/dists/resolute-security/InRelease")
    
    # Check LXD environment
    check_lxd_network()
    
    print("=== Diagnostic Complete ===")
