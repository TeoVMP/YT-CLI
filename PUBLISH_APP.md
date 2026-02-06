# How to Publish Your App for Public Use

## Problem
Currently, your app is in "Testing" mode, which means only users added as "Test Users" can use it. To allow **anyone** to use your app, you need to publish it.

## Solution: Publish Your OAuth App

### Step 1: Go to OAuth Consent Screen

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** > **OAuth consent screen**

### Step 2: Check Your App Status

You should see your app is currently in **"Testing"** mode.

### Step 3: Publish Your App

1. Click on **"PUBLISH APP"** button (usually at the top)
2. You'll see a warning about making your app public
3. Click **"CONFIRM"** to publish

### Step 4: Verification Requirements

#### For Non-Sensitive Scopes (Your Case ✅)

Since you're only using `youtube.force-ssl` scope, which is **NOT a sensitive scope**, you can publish immediately **without verification**.

**What this means:**
- ✅ Your app can be used by anyone
- ✅ No verification process needed
- ✅ No additional steps required
- ⚠️ You'll see a warning banner (this is normal for unverified apps)

#### For Sensitive Scopes (Not Your Case)

If you were using sensitive scopes (like Gmail, Drive, etc.), you would need:
- Google verification process
- Privacy policy URL
- Terms of service URL
- Security assessment

**But since you're only using `youtube.force-ssl`, you don't need this!**

### Step 5: User Experience After Publishing

Once published:

1. **Any Google user** can use your app
2. They'll see a warning: "Google hasn't verified this app"
3. They can click "Advanced" > "Go to [Your App Name] (unsafe)"
4. After that, they can authorize normally

### Step 6: Optional - Remove Warning (Verification)

If you want to remove the "unverified app" warning, you can:

1. Go through Google's verification process (optional)
2. Provide privacy policy and terms of service
3. Complete security assessment

**Note:** This is optional for non-sensitive scopes. The app works fine without it.

## Important Notes

### What Changes After Publishing

- ✅ **Before**: Only test users can use the app
- ✅ **After**: Anyone with a Google account can use the app
- ⚠️ **Warning**: Users will see "unverified app" message (normal for non-verified apps)

### Security Considerations

- Your app still only requests `youtube.force-ssl` scope
- No access to Gmail or other sensitive data
- Users can see exactly what permissions are requested
- They can revoke access anytime from their Google account settings

### Rate Limits

- **Unverified apps**: Limited to 100 users (but this limit is usually not enforced strictly)
- **Verified apps**: No user limit
- **API quotas**: Still apply (10,000 units/day per project)

## Troubleshooting

### "Publish App" Button Not Available

- Make sure you've completed all required fields in OAuth Consent Screen
- Check that you've added at least one scope (`youtube.force-ssl`)

### Users Still Can't Access

- Wait a few minutes after publishing (propagation delay)
- Make sure users are using the correct Client ID
- Check that the app is actually published (status should show "In production")

### Want to Go Back to Testing Mode

- You can unpublish the app anytime
- Go to OAuth Consent Screen > Click "Unpublish App"
- Only test users will be able to use it again

## Summary

**To allow anyone to use your app:**

1. Go to OAuth Consent Screen in Google Cloud Console
2. Click "PUBLISH APP"
3. Confirm the action
4. Done! ✅

**No verification needed** because `youtube.force-ssl` is a non-sensitive scope.
