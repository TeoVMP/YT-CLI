# 📱 Installation Guide for Termux (Android)

## Prerequisites

First, install required system packages in Termux:

```bash
# Update packages
pkg update && pkg upgrade

# Install build tools and dependencies
pkg install python rust cargo clang make libffi openssl

# Install Python development headers
pkg install python-dev
```

## Installation Steps

### Option 1: Install with pre-built wheels (Recommended)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install cryptography first (may have pre-built wheels)
pip install cryptography

# Then install all requirements
pip install -r requirements.txt
```

### Option 2: Install cryptography from Termux packages (Alternative)

If Option 1 fails, try installing cryptography from Termux's package manager:

```bash
# Install cryptography from Termux packages
pkg install py312-cryptography

# Then install other requirements (excluding cryptography)
pip install --upgrade pip setuptools wheel
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv yt-dlp mutagen
```

### Option 3: Build cryptography manually

If both options fail, build cryptography manually:

```bash
# Install Rust and Cargo
pkg install rust cargo

# Set environment variables
export CARGO_BUILD_TARGET=aarch64-linux-android
export CC=clang
export CXX=clang++

# Install cryptography
pip install cryptography --no-binary cryptography

# Then install other requirements
pip install -r requirements.txt
```

## Troubleshooting

### Error: "Rust not found"

```bash
# Install Rust
pkg install rust

# Verify installation
rustc --version
cargo --version
```

### Error: "Unsupported platform"

Try setting environment variables before installing:

```bash
export CARGO_BUILD_TARGET=aarch64-linux-android
export CC=clang
export CXX=clang++
pip install cryptography
```

### Error: "Failed to build cryptography"

1. **Install all build dependencies:**
   ```bash
   pkg install python rust cargo clang make libffi openssl python-dev
   ```

2. **Upgrade pip and build tools:**
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

3. **Try installing cryptography separately:**
   ```bash
   pip install cryptography --no-cache-dir
   ```

### Alternative: Use system Python cryptography

If building fails, you can try using Termux's system package:

```bash
# Install from Termux packages
pkg install py312-cryptography

# Then install other packages manually
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv yt-dlp mutagen
```

## Verify Installation

After installation, verify everything works:

```bash
python -c "import google.auth; print('✓ google-auth OK')"
python -c "import yt_dlp; print('✓ yt-dlp OK')"
python -c "import mutagen; print('✓ mutagen OK')"
```

## Notes for Termux

- **OAuth2 Authentication**: When running `python main.py --login`, the console-based OAuth2 flow will be used automatically (no browser needed).
- **Storage**: Make sure you have enough storage space for downloads.
- **Permissions**: Grant storage permissions if needed for downloads.

## Quick Start After Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Configure OAuth2 credentials
python setup.py

# Login (will use console-based OAuth2 in Termux)
python main.py --login

# Search videos
python main.py --search "python tutorial"
```

## Alternative Installation Script

Create a file `install-termux.sh`:

```bash
#!/data/data/com.termux/files/usr/bin/bash

echo "Installing system dependencies..."
pkg update && pkg upgrade -y
pkg install -y python rust cargo clang make libffi openssl python-dev

echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

echo "Installing cryptography..."
pip install cryptography

echo "Installing project dependencies..."
pip install -r requirements.txt

echo "✓ Installation complete!"
echo "Run: source venv/bin/activate && python setup.py"
```

Make it executable and run:
```bash
chmod +x install-termux.sh
./install-termux.sh
```
