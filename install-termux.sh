#!/data/data/com.termux/files/usr/bin/bash

set -e  # Exit on error

echo "=========================================="
echo "YT-CLI Installation for Termux"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Update Termux packages
echo -e "${YELLOW}Step 1: Updating Termux packages...${NC}"
pkg update -y && pkg upgrade -y

# Step 2: Install system dependencies
echo -e "${YELLOW}Step 2: Installing system dependencies...${NC}"
pkg install -y python rust clang make libffi openssl

# Step 3: Install cryptography from Termux packages
echo -e "${YELLOW}Step 3: Installing cryptography from Termux packages...${NC}"
# Try to detect Python version
PYTHON_VERSION=$(python --version 2>&1 | grep -oP '\d+\.\d+' | head -1 | cut -d. -f1,2 | tr -d '.')
echo "Detected Python version: $(python --version)"

# Try to install cryptography package
if pkg install -y py${PYTHON_VERSION}-cryptography 2>/dev/null; then
    echo -e "${GREEN}✓ cryptography installed from Termux packages${NC}"
else
    echo -e "${YELLOW}⚠ Could not install cryptography from Termux packages${NC}"
    echo "Attempting to install via pip (this may take a while)..."
    pip install --upgrade pip setuptools wheel
    pip install cryptography || {
        echo -e "${RED}✗ Failed to install cryptography${NC}"
        echo "Please install manually: pkg install py312-cryptography (or py311-cryptography, etc.)"
        exit 1
    }
fi

# Step 4: Upgrade pip
echo -e "${YELLOW}Step 4: Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel

# Step 5: Install Python dependencies (cryptography already installed)
echo -e "${YELLOW}Step 5: Installing Python dependencies...${NC}"
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv yt-dlp mutagen

# Step 6: Verify installation
echo -e "${YELLOW}Step 6: Verifying installation...${NC}"
python -c "import google.auth; print('✓ google-auth OK')" || echo -e "${RED}✗ google-auth failed${NC}"
python -c "import yt_dlp; print('✓ yt-dlp OK')" || echo -e "${RED}✗ yt-dlp failed${NC}"
python -c "import mutagen; print('✓ mutagen OK')" || echo -e "${RED}✗ mutagen failed${NC}"
python -c "import cryptography; print('✓ cryptography OK')" || echo -e "${RED}✗ cryptography failed${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "✓ Installation complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Configure OAuth2: python setup.py"
echo "  2. Login: python main.py --login"
echo "  3. Test: python main.py --search 'python tutorial'"
echo ""
