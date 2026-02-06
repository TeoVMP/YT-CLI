# 🔐 Authentication Guide - Login and Account Management

## How Authentication Works

### First Time Login

When you run `python main.py --login` for the first time:

1. **Browser Opens Automatically**: The OAuth2 flow uses `run_local_server()` which automatically opens your default browser
2. **Google Login Page**: You'll see Google's login page
3. **Sign In**: Sign in with the Google account you want to use
4. **Authorization Screen**: Google shows what permissions are requested:
   - ✅ "This app wants to access YouTube"
   - ❌ NO access to Gmail/email
5. **Click "Allow"**: Authorize the application
6. **Automatic Redirect**: The browser redirects to `http://localhost:8080` automatically
7. **Token Saved**: The token is automatically saved to `token.json` on your computer

**You DON'T need to copy/paste any URLs manually** - everything happens automatically!

### If Browser Doesn't Open Automatically

If your browser doesn't open automatically, you'll see a message like:

```
Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth?...
```

In this case:
1. Copy the URL shown in the terminal
2. Paste it into your browser
3. Sign in and authorize
4. The token will be saved automatically

## Changing Accounts

### Method 1: Logout and Login Again (Recommended)

```bash
# Step 1: Logout from current account
python main.py --logout

# Step 2: Login with new account
python main.py --login
```

This will:
- Revoke the old token
- Delete `token.json`
- Open browser for you to sign in with a different account
- Save the new token

### Method 2: Delete Token Manually

```bash
# Delete the token file
del token.json  # Windows
# or
rm token.json   # Linux/Mac

# Then login again
python main.py --login
```

## How It Works Internally

### OAuth2 Flow

1. **Client Configuration**: Uses your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from `.env`
2. **Authorization URL**: Generates a URL with your app's credentials
3. **Local Server**: Starts a temporary server on `http://localhost:8080`
4. **Browser Redirect**: After authorization, Google redirects to `localhost:8080`
5. **Token Exchange**: The local server receives the authorization code
6. **Token Storage**: Saves the token (and refresh token) to `token.json`

### Token File (`token.json`)

Contains:
- Access token (short-lived, ~1 hour)
- Refresh token (long-lived, used to get new access tokens)
- Token expiration time
- Scopes granted

**Important**: This file is in `.gitignore` - never commit it to GitHub!

## Multiple Accounts

### Using Different Accounts

If you want to use different Google accounts:

1. **Logout from current account**:
   ```bash
   python main.py --logout
   ```

2. **Login with different account**:
   ```bash
   python main.py --login
   ```
   - Browser opens
   - Sign in with the NEW account
   - New token is saved

### Using Same Account on Different Computers

Each computer has its own `token.json`:
- Computer A: Has `token.json` with Account 1
- Computer B: Needs to login separately (will have its own `token.json`)

## Troubleshooting

### "Browser didn't open automatically"

**Solution**: Copy the URL from terminal and paste in browser manually.

### "Token expired"

**Solution**: The refresh token automatically gets a new access token. If refresh token is expired, run `--login` again.

### "Want to use a different account"

**Solution**: 
```bash
python main.py --logout
python main.py --login
```

### "Can't logout - token file not found"

**Solution**: You're already logged out! Just run `--login` to authenticate.

## Security Notes

- ✅ **Tokens are local**: Stored only on your computer
- ✅ **Scopes limited**: Only YouTube access, no Gmail
- ✅ **Revocable**: You can revoke access anytime from Google Account settings
- ✅ **Per-computer**: Each computer needs its own authentication
- ✅ **Refresh tokens**: Automatically refresh expired access tokens

## Quick Reference

```bash
# First time setup
python setup.py              # Configure OAuth2 credentials
python main.py --login       # Authenticate with Google

# Check status
python main.py --auth-status # See if you're logged in

# Change account
python main.py --logout      # Logout current account
python main.py --login       # Login with different account

# Use features (requires login)
python main.py --video-id VIDEO_ID --comment "Hello"
python main.py --stats VIDEO_ID
```
