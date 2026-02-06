# GitHub Repository Description

## Repository Name
`YTLikesBot`

## Short Description (for GitHub)
```
Complete YouTube automation bot: comment, download videos/audio, analyze statistics, manage comments, and export metadata - all from the command line
```

## Full Description (for README or About section)

### Overview
**YTLikesBot** is a comprehensive Python-based command-line tool for interacting with YouTube through the official YouTube Data API v3. It provides a complete suite of features for content creators, community managers, and developers who need to automate YouTube interactions while maintaining security and following best practices.

### Key Features

#### 🎯 Comment Management
- **Post comments** on videos using your personal Google account
- **List your own comments** across videos or filter by specific video
- **Reply to comments** programmatically
- **Edit your comments** after posting
- **Delete your comments** with confirmation
- **View comment replies** and detailed information
- **Export comments** to text files (readable or grep-friendly format)

#### 📥 Download & Playback
- **Download videos** in MP4 format with configurable quality
- **Extract audio** as MP3 with embedded metadata
- **Download both** video and audio simultaneously
- **Automatic playback** with VLC Media Player integration
- **Fullscreen support** for video playback

#### 📊 Analytics & Export
- **Video statistics** including views, likes, comments, engagement rate
- **Top comments** sorted by likes/relevance
- **Metadata export** in JSON or human-readable text format
- **Comment export** with full details (author, date, likes, text)
- **Engagement rate calculation** for performance analysis

#### 🔒 Security & Protection
- **OAuth 2.0 authentication** with limited scopes
- **YouTube-only access** - NO Gmail/email access
- **Rate limiting** configurable per day/hour
- **Activity monitoring** with suspicious activity detection
- **Automatic moderation** with configurable rules
- **Secure token storage** locally on your machine

#### ⚙️ Advanced Features
- **Multi-account support** with load balancing and failover
- **Quota monitoring** to prevent API limit exhaustion
- **Activity logging** for audit trails
- **Interactive CLI mode** for user-friendly operation
- **UTF-8 encoding support** for international characters
- **Cross-platform** (Windows, Linux, macOS)

### Technical Stack
- **Language**: Python 3.x
- **APIs**: YouTube Data API v3 (Google APIs)
- **Authentication**: OAuth 2.0 with scope-limited access
- **Key Libraries**:
  - `google-api-python-client` - Official Google APIs client
  - `google-auth-oauthlib` - OAuth 2.0 handling
  - `yt-dlp` - Video/audio downloading
  - `mutagen` - MP3 metadata manipulation
  - `python-dotenv` - Environment variable management

### Architecture
Modular architecture with separation of concerns:
- **youtube_client.py** - YouTube API client with OAuth2
- **downloader.py** - Video/audio download module
- **comment_exporter.py** - Comment export functionality
- **metadata_exporter.py** - Metadata export (JSON/text)
- **moderator.py** - Automatic content moderation
- **account_protection.py** - Security and rate limiting
- **activity_monitor.py** - Activity logging and monitoring
- **vlc_player.py** - VLC Media Player integration
- **config.py** - Centralized configuration management

### Use Cases
- **Content creators**: Automate engagement and community management
- **Developers**: Integrate YouTube functionality into applications
- **Analysts**: Export and analyze video statistics and comments
- **Community managers**: Moderate and manage comments programmatically
- **Researchers**: Collect and analyze YouTube data

### Security Highlights
- ✅ **OAuth 2.0 with minimal scopes**: Only `youtube.force-ssl` scope requested
- ✅ **No email access**: Explicitly prevents Gmail/email API access
- ✅ **Rate limiting**: Configurable limits (default: 50/day, 10/hour)
- ✅ **Activity monitoring**: Detects suspicious patterns automatically
- ✅ **Secure storage**: Tokens stored locally, never transmitted

### Installation & Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure OAuth2 credentials: `python setup.py`
3. Authorize with your Google account (one-time)
4. Start using: `python main.py --help`

### Documentation
Comprehensive documentation included:
- Quick start guide
- Google Cloud Console setup instructions
- Security and privacy documentation
- Multi-account system guide
- Troubleshooting guides

### License
Open source project - use responsibly and respect YouTube's Terms of Service.

---

## Topics/Tags for GitHub
```
python
youtube-api
oauth2
automation
cli
youtube-bot
youtube-automation
content-management
api-integration
command-line-tool
python-script
youtube-downloader
comment-management
video-analytics
open-source
```

## Repository Settings Recommendations

### About Section
- **Website**: (optional - if you have a demo site)
- **Topics**: python, youtube-api, oauth2, automation, cli, youtube-bot
- **Description**: Complete YouTube automation bot: comment, download videos/audio, analyze statistics, manage comments, and export metadata - all from the command line

### Social Preview
The README.md already includes emojis and formatting that will look great on GitHub's social preview.

### Recommended Settings
- ✅ **Issues**: Enabled (for bug reports and feature requests)
- ✅ **Discussions**: Enabled (for community questions)
- ✅ **Wiki**: Optional (documentation is in markdown files)
- ✅ **Projects**: Optional (for project management)
- ✅ **Releases**: Enabled (for version tagging)
