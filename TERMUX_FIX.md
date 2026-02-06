# 🔧 Fix for cryptography Installation in Termux

## Problem
`cryptography` fails to build because it needs `ANDROID_API_LEVEL` environment variable.

## Solution: Set Android API Level

The easiest fix is to set the `ANDROID_API_LEVEL` environment variable before installing:

```bash
# Step 1: Set Android API level (try 34 first, then 33, 32 if needed)
export ANDROID_API_LEVEL=34

# Step 2: Install cryptography
pip install cryptography

# Step 3: Verify it's installed
python -c "import cryptography; print('✓ cryptography OK')"

# Step 4: Install other dependencies
pip install -r requirements-termux.txt
```

## If API Level 34 doesn't work

Try different API levels:

```bash
# Try 33
export ANDROID_API_LEVEL=33
pip install cryptography

# Or try 32
export ANDROID_API_LEVEL=32
pip install cryptography
```

## Make it permanent (optional)

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
export ANDROID_API_LEVEL=34
```

Then reload: `source ~/.bashrc`

## Alternative: If py312-cryptography doesn't work

Try installing the cryptography package that matches your Python version:

```bash
# Check your Python version
python --version

# For Python 3.12:
pkg install py312-cryptography

# For Python 3.11:
pkg install py311-cryptography

# For Python 3.10:
pkg install py310-cryptography
```

## If Termux package doesn't exist

If the Termux package doesn't work, try installing Rust properly first:

```bash
# Install Rust
pkg install rust

# Verify Rust is in PATH
rustc --version
cargo --version

# If cargo is not found, add to PATH
export PATH=$PATH:$HOME/.cargo/bin

# Set build target for Android
export CARGO_BUILD_TARGET=aarch64-linux-android
export CC=clang
export CXX=clang++

# Try installing cryptography again
pip install cryptography --no-binary cryptography
```

## Quick Fix (Recommended)

```bash
# Install from Termux packages (easiest)
pkg install py312-cryptography

# Then install rest of requirements
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv yt-dlp mutagen
```
