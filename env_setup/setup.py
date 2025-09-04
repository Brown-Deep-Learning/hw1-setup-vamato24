#!/usr/bin/env python3
"""
CSCI 1470 Deep Learning Environment Setup Script
Cross-platform virtual environment setup for Mac, Windows, and Linux

Authors: Armaan Patankar
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# Configuration
ENV_NAME = "csci1470"
PYTHON_VERSION_REQUIRED = (3, 11)
REQUIREMENTS_FILE = "env_setup/requirements.txt"
INSTALL_IN_PARENT = True # This makes sure you install it in the directory you are cloning to

class Colors:
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[1;36m'
    NC = '\033[0m'  # No Color

def print_colored(message, color=Colors.NC):
    print(f"{color}{message}{Colors.NC}")

def run_command(cmd, check=True, capture_output=False):
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, check=check, 
                                 capture_output=capture_output, text=True)
        else:
            result = subprocess.run(cmd, check=check, 
                                 capture_output=capture_output, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print_colored(f"Command failed: {cmd}", Colors.RED)
        print_colored(f"Error: {e}", Colors.RED)
        return None

def check_python_version():
    version = sys.version_info
    print_colored(f"Found Python {version.major}.{version.minor}.{version.micro}", Colors.CYAN)
    
    # TensorFlow 2.15 requires Python 3.11-3.12 only for our tensorflow version
    if version[:2] < (3, 11):
        print_colored(f"Error: Python 3.11+ required, found {version.major}.{version.minor}", Colors.RED)
        print_colored("Install Python 3.11 from: https://python.org/downloads/", Colors.YELLOW)
        return False
    elif version[:2] > (3, 12):
        print_colored(f"Error: Python {version.major}.{version.minor} not supported by TensorFlow 2.15", Colors.RED)
        print_colored("Please install Python 3.11 or 3.12:", Colors.YELLOW)
        print_colored("macOS: brew install python@3.11", Colors.YELLOW)
        print_colored("Windows/Linux: https://python.org/downloads/release/python-3119/", Colors.YELLOW)
        return False
    
    print_colored(f"✓ Python {version.major}.{version.minor} is compatible", Colors.GREEN)
    return True

def get_os_info():
    system = platform.system().lower()
    architecture = platform.machine().lower()
    
    if system == "darwin":
        os_type = "mac"
        is_apple_silicon = architecture in ["arm64", "aarch64"]
    elif system == "windows":
        os_type = "windows"
        is_apple_silicon = False
    else:
        os_type = "linux"
        is_apple_silicon = False
    
    print_colored(f"Detected: {system} ({architecture})", Colors.CYAN)
    return os_type, is_apple_silicon

def check_system_dependencies(os_type):
    """Check and install system dependencies"""
    print_colored("Checking system dependencies...", Colors.CYAN)
    
    if os_type == "mac":
        # Check for Homebrew
        if not shutil.which("brew"):
            print_colored("Homebrew not found. Please install it first:", Colors.YELLOW)
            print_colored("Visit: https://brew.sh/", Colors.YELLOW)
            print_colored("Or run: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"", Colors.YELLOW)
            return False
        
        # Install system dependencies via Homebrew if needed
        deps = ["python@3.11", "hdf5", "pkg-config"]
        for dep in deps:
            result = run_command(f"brew list {dep}", check=False, capture_output=True)
            if result and result.returncode != 0:
                run_command(f"brew install {dep}")
    
    elif os_type == "linux":
        # Check for common package managers and install dependencies
        if shutil.which("apt-get"):  # Ubuntu/Debian
            deps = ["python3.11", "python3.11-venv", "python3.11-dev", 
                   "libhdf5-dev", "pkg-config", "build-essential"]
            run_command(f"sudo apt-get update")
            run_command(f"sudo apt-get install -y {' '.join(deps)}")
        
        elif shutil.which("yum"):  # CentOS/RHEL/Fedora
            deps = ["python311", "python311-devel", "hdf5-devel", 
                   "pkgconfig", "gcc", "gcc-c++"]
            run_command(f"sudo yum install -y {' '.join(deps)}")
        
        elif shutil.which("dnf"):  # Fedora
            deps = ["python3.11", "python3-devel", "hdf5-devel", 
                   "pkgconfig", "gcc", "gcc-c++"]
            run_command(f"sudo dnf install -y {' '.join(deps)}")
    
    return True

def create_virtual_environment():
    if INSTALL_IN_PARENT:
        # Install in parent directory
        env_path = Path("..") / ENV_NAME
        print_colored(f"Installing virtual environment in parent directory: {env_path.resolve()}", Colors.CYAN)
    else:
        # Install in current directory
        env_path = Path(ENV_NAME)
    
    if env_path.exists():
        print_colored(f"Virtual environment '{ENV_NAME}' already exists at {env_path.resolve()}.", Colors.YELLOW)
        response = input("Do you want to recreate it? (y/N): ").strip().lower()
        if response == 'y':
            print_colored(f"Removing existing environment...", Colors.YELLOW)
            shutil.rmtree(env_path)
        else:
            return env_path
    
    print_colored(f"Creating virtual environment '{ENV_NAME}' at {env_path.resolve()}...", Colors.CYAN)
    result = run_command([sys.executable, "-m", "venv", str(env_path)])
    if not result:
        return None
    
    print_colored(f"Virtual environment created successfully!", Colors.GREEN)
    return env_path

def get_activation_command(env_path, os_type):
    if os_type == "windows":
        activate_script = "../csci1470/Scripts/activate"
        return str(activate_script)
    else:
        activate_script = "../csci1470/bin/activate"
        return f"source {activate_script}"

def install_requirements(env_path, os_type):
    if not Path(REQUIREMENTS_FILE).exists():
        print_colored(f"Error: {REQUIREMENTS_FILE} not found!", Colors.RED)
        return False
    
    # Get Python executable in virtual environment
    if os_type == "windows":
        python_exe = env_path / "Scripts" / "python.exe"
        pip_exe = env_path / "Scripts" / "pip.exe"
    else:
        python_exe = env_path / "bin" / "python"
        pip_exe = env_path / "bin" / "pip"
    
    print_colored("Upgrading pip...", Colors.CYAN)
    result = run_command([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])
    if not result:
        return False
    
    print_colored("Installing packages from requirements.txt...", Colors.CYAN)
    result = run_command([str(pip_exe), "install", "-r", REQUIREMENTS_FILE])
    if not result:
        print_colored("Package installation failed. Trying with --no-cache-dir...", Colors.YELLOW)
        result = run_command([str(pip_exe), "install", "--no-cache-dir", "-r", REQUIREMENTS_FILE])
        if not result:
            return False
    
    return True

def setup_jupyter_kernel(env_path, os_type):
    if os_type == "windows":
        python_exe = env_path / "Scripts" / "python.exe"
    else:
        python_exe = env_path / "bin" / "python"
    
    print_colored("Setting up Jupyter kernel...", Colors.CYAN)
    kernel_name = ENV_NAME
    display_name = f"DL-S25 (3.11) - {ENV_NAME}"
    
    result = run_command([
        str(python_exe), "-m", "ipykernel", "install", 
        "--user", "--name", kernel_name, "--display-name", display_name
    ])
    
    if result:
        print_colored("Jupyter kernel installed successfully!", Colors.GREEN)
        return True
    else:
        print_colored("Jupyter kernel installation failed", Colors.RED)
        return False

def verify_installation(env_path, os_type):
    if os_type == "windows":
        python_exe = env_path / "Scripts" / "python.exe"
    else:
        python_exe = env_path / "bin" / "python"
    
    print_colored("Verifying installation...", Colors.CYAN)
    
    test_imports = [
        "numpy", "tensorflow", "pandas", "matplotlib", 
        "sklearn", "PIL", "h5py"
    ]
    
    for package in test_imports:
        result = run_command([
            str(python_exe), "-c", f"import {package}; print(f'{package} OK')"
        ], capture_output=True)
        
        if result and result.returncode == 0:
            print_colored(f"✓ {package}", Colors.GREEN)
        else:
            print_colored(f"✗ {package} - Import failed", Colors.RED)
            return False
    
    return True

def print_next_steps(env_path, os_type):
    activation_cmd = get_activation_command(env_path, os_type)
    
    print_colored("\n" + "="*60, Colors.GREEN)
    print_colored("SETUP COMPLETE!", Colors.GREEN)
    print_colored("="*60, Colors.GREEN)
    
    print_colored(f"\nVirtual environment created at: {env_path.resolve()}", Colors.CYAN)
    
    print_colored("\nIntended Directory Structure:", Colors.CYAN)
    parent_name = Path("..").resolve().name
    current_name = Path.cwd().name
    print_colored(f"  {parent_name}/", Colors.YELLOW)
    print_colored(f"  ├── {ENV_NAME}/          # Virtual environment", Colors.YELLOW)
    print_colored(f"  └── {current_name}/      # Assignment repo (current directory)", Colors.YELLOW)
    
    print_colored("\nTo activate your environment:", Colors.CYAN)
    print_colored(f"  {activation_cmd}", Colors.YELLOW)
    
    print_colored("\nTo deactivate:", Colors.CYAN)
    print_colored("  deactivate", Colors.YELLOW)
    
    if INSTALL_IN_PARENT:
        print_colored("\nWorking on Future Assignments!!!", Colors.CYAN)
        print_colored("  1. Clone new assignment repos in the parent directory", Colors.YELLOW)
        print_colored("  2. Activate the environment from any assignment directory", Colors.YELLOW)
        print_colored("  3. The same environment will be used for all assignments", Colors.YELLOW)
    
def main():
    """Main setup function"""
    print_colored("CSCI 1470 Deep Learning Environment Setup", Colors.CYAN)
    print_colored("="*50, Colors.CYAN)
    
    # Check Python version
    if not check_python_version():
        print_colored("\nPlease install Python 3.11.x and run this script again.", Colors.RED)
        print_colored("Follow the troubleshooting steps on the handout if you are having issues!", Colors.YELLOW)
        sys.exit(1)
    
    # Detect OS
    os_type, is_apple_silicon = get_os_info()
    
    # Check system dependencies
    if not check_system_dependencies(os_type):
        print_colored("Please install required system dependencies and run again. Follow the troubleshooting steps on the handout if you are having issues!", Colors.RED)
        sys.exit(1)
    
    # Create virtual environment
    env_path = create_virtual_environment()
    if not env_path:
        print_colored("Failed to create virtual environment. Follow the troubleshooting steps on the handout if you are having issues!", Colors.RED)
        sys.exit(1)
    
    # Install requirements
    if not install_requirements(env_path, os_type):
        print_colored("Failed to install requirements. Follow the troubleshooting steps on the handout if you are having issues!", Colors.RED)
        sys.exit(1)
    
    # Setup Jupyter kernel
    setup_jupyter_kernel(env_path, os_type)
    
    # Verify installation
    if not verify_installation(env_path, os_type):
        print_colored("Installation verification failed. Some packages may not work correctly.", Colors.YELLOW)
        print_colored("\nTroubleshooting:", Colors.CYAN)
        print_colored(" -  Follow the troubleshooting steps on the handout if you are having issues!", Colors.YELLOW)
    
    # Print next steps
    print_next_steps(env_path, os_type)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\nSetup interrupted by user.", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\nUnexpected error: {e}", Colors.RED)
        sys.exit(1)