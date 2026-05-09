#!/bin/bash

# GEMINIRECON Setup Script
# Distro support: Ubuntu, Kali, Debian, Termux

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}GEMINIRECON Production-Grade Setup Starting...${NC}"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
elif [ -d "/data/data/com.termux" ]; then
    OS="termux"
else
    OS=$(uname -s)
fi

echo -e "Detected OS: ${GREEN}$OS${NC}"

# Update & Install Base Dependencies
case $OS in
    ubuntu|debian|kali)
        sudo apt-get update -y
        sudo apt-get install -y git golang python3 python3-pip curl wget rustc cargo build-essential libpcap-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev
        BIN_DIR="/usr/local/bin"
        ;;
    termux)
        pkg update -y
        pkg install -y git golang python wget rust make clang libpcap openssl libffi libxml2 libxslt
        BIN_DIR="$PREFIX/bin"
        ;;
    *)
        echo -e "${RED}Unsupported OS: $OS${NC}"
        exit 1
        ;;
esac

# Function to verify tool
verify_tool() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}[OK] $1 is installed${NC}"
    else
        echo -e "${RED}[FAIL] $1 installation failed${NC}"
    fi
}

# 1. Install Go Tools
echo -e "${YELLOW}Installing Go-based tools...${NC}"
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin

GO_TOOLS=(
    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    "github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest"
    "github.com/projectdiscovery/httpx/cmd/httpx@latest"
    "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"
    "github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
    "github.com/projectdiscovery/katana/cmd/katana@latest"
    "github.com/OWASP/Amass/v3/...@master"
    "github.com/tomnomnom/assetfinder@latest"
    "github.com/tomnomnom/httprobe@latest"
    "github.com/OJ/gobuster/v3@latest"
)

for tool in "${GO_TOOLS[@]}"; do
    echo -e "Installing $tool..."
    go install -v $tool
done

# 2. Install Python Tools
echo -e "${YELLOW}Installing Python-based tools...${NC}"
pip install --upgrade pip
pip install sqlmap dirsearch xsstrike theHarvester recon-ng

# 3. Binary Downloads (Findomain, RustScan, Feroxbuster, Network tools)
echo -e "${YELLOW}Downloading binaries...${NC}"

# Findomain
wget https://github.com/Findomain/Findomain/releases/latest/download/findomain-linux.zip
unzip findomain-linux.zip && chmod +x findomain && mv findomain $BIN_DIR/
rm findomain-linux.zip

# Network tools (wireshark, tcpdump)
case $OS in
    ubuntu|debian|kali)
        sudo apt-get install -y wireshark tcpdump
        ;;
    termux)
        pkg install -y wireshark-cli tcpdump
        ;;
esac

# RustScan (if on PC)
if [ "$OS" != "termux" ]; then
    wget https://github.com/RustScan/RustScan/releases/latest/download/rustscan_2.3.0_amd64.deb
    sudo dpkg -i rustscan_2.3.0_amd64.deb || sudo apt-get install -f -y
    rm rustscan_2.3.0_amd64.deb
fi

# Feroxbuster
cargo install feroxbuster

# 4. Move Go Binaries to System Path (Optional, but recommended)
cp $HOME/go/bin/* $BIN_DIR/

# 5. Final Verification
echo -e "${YELLOW}Final Verification...${NC}"
TOOLS=(subfinder nuclei httpx naabu dnsx katana amass assetfinder findomain nmap sqlmap ffuf)
for t in "${TOOLS[@]}"; do
    verify_tool $t
done

echo -e "${GREEN}GEMINIRECON Setup Complete!${NC}"
