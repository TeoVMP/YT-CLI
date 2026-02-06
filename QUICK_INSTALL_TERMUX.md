# 🚀 Quick Install for Termux

## Step-by-Step Commands

Copy and paste these commands **one by one**:

```bash
# Step 1: Update Termux packages
pkg update && pkg upgrade

# Step 2: Install system dependencies
pkg install python rust clang make libffi openssl

# Step 3: Upgrade pip (IMPORTANT: use 'pip', not 'python')
pip install --upgrade pip setuptools wheel

# Step 4: Install cryptography
pip install cryptography

# Step 5: Install project dependencies
pip install -r requirements.txt
```

## Common Mistakes

❌ **Wrong:** `python install --upgrade pip`  
✅ **Correct:** `pip install --upgrade pip`

❌ **Wrong:** `python install cryptography`  
✅ **Correct:** `pip install cryptography`

## Verify Installation

```bash
python -c "import google.auth; print('✓ OK')"
python -c "import yt_dlp; print('✓ OK')"
```

## Next Steps

```bash
# Configure OAuth2
python setup.py

# Login
python main.py --login

# Test search
python main.py --search "python tutorial"
```
