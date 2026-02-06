# YouTube Bot - Comment and Download YouTube Videos

Complete bot to interact with YouTube: comment, download videos/audio, view statistics, and more.

## 🎯 Main Features

- ✅ **Comment on videos** using your personal Google account
- ✅ **Download MP4 videos** and **MP3 audio**
- ✅ **View video statistics**
- ✅ **Export comments** to text files
- ✅ **Play videos** automatically with VLC
- ✅ **Security system**: Only YouTube access (no Gmail)
- ✅ **Configurable rate limiting**

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure OAuth2 Credentials

**Each user uses their own Google account to comment.**

```bash
python setup.py
```

Or manually: copy `env.example` to `.env` and fill in your credentials.

### 3. Authorize with Your Personal Account

```bash
python main.py --stats VIDEO_ID
```

Your browser will open to authorize with your personal Google account.

## 📋 Available Commands

### Comment

```bash
# With full URL
python main.py --video-id "https://www.youtube.com/watch?v=VIDEO_ID" --comment "Your comment"

# With just the ID
python main.py --video-id VIDEO_ID --comment "Your comment"
```

### Download

```bash
# Download MP4 video
python main.py --download-video "https://www.youtube.com/watch?v=VIDEO_ID"

# Download MP3 audio
python main.py --download-audio "https://www.youtube.com/watch?v=VIDEO_ID"

# Download both
python main.py --download-both "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Play with VLC

```bash
# Play from URL
python main.py --play "https://www.youtube.com/watch?v=VIDEO_ID"

# Play local file
python main.py --play "path/to/video.mp4"

# Fullscreen
python main.py --play "URL" --play-fullscreen

# Download and play automatically
python main.py --download-and-play "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Statistics and Comments

```bash
# View statistics
python main.py --stats VIDEO_ID

# View top comments
python main.py --top-comments VIDEO_ID

# Export comments
python main.py --export-comments VIDEO_ID

# Export in grep format
python main.py --export-comments VIDEO_ID --grep-format
```

### Comment Management

```bash
# List your comments
python main.py --my-comments VIDEO_ID

# Delete a comment
python main.py --delete-comment COMMENT_ID

# Reply to a comment
python main.py --reply COMMENT_ID --reply-text "Your reply"

# Update a comment
python main.py --update-comment COMMENT_ID --new-text "New text"

# View comment replies
python main.py --comment-replies COMMENT_ID

# View comment info
python main.py --comment-info COMMENT_ID
```

### Download Metadata

```bash
# Download metadata (JSON)
python main.py --download-metadata VIDEO_ID

# Download metadata (text)
python main.py --download-metadata VIDEO_ID --metadata-format text
```

## 🔐 Security

- ✅ Only requests YouTube API access
- ✅ NO access to Gmail/email
- ✅ Tokens stored locally on your computer
- ✅ Each user authorizes with their own account

## ⚙️ Configuration

### `.env` File

```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
REDIRECT_URI=http://localhost:8080

# Rate limiting
MAX_COMMENTS_PER_DAY=50
MAX_COMMENTS_PER_HOUR=10
```

### Get OAuth2 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project
3. Enable "YouTube Data API v3"
4. Configure OAuth Consent Screen:
   - User Type: External
   - Scopes: ONLY `youtube.force-ssl`
   - **Publish your app** to allow anyone to use it (no verification needed for this scope)
5. Create OAuth2 credentials:
   - Application type: Desktop app
6. Copy Client ID and Client Secret

**Note:** To allow anyone to use your app without adding them as test users, click "PUBLISH APP" in OAuth Consent Screen. Since `youtube.force-ssl` is a non-sensitive scope, no verification is required.

## 🎮 Interactive Mode

```bash
python main.py
```

Interactive menu with all available options.

## 📝 Important Notes

- **Each user uses their own account**: You don't need collective accounts
- **First authorization**: Browser opens once
- **Limits**: 50 comments/day, 10/hour (configurable)
- **Tokens**: Stored in `token.json` (don't upload to GitHub)

## 🐛 Troubleshooting

### Error 403: access_denied
- Add your email as Test User in OAuth Consent Screen

### VLC doesn't open
- Install VLC from https://www.videolan.org/vlc/
- Verify it's in your PATH

### Credentials error
- Verify that `.env` has correct credentials
- Run `python setup.py` to reconfigure

## 📄 License

This project is open source. Use responsibly and respect YouTube's Terms of Service.
