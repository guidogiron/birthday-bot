# 🎉 Birthday Celebration Bot

A Python bot that fetches birthdays and anniversaries from [Planning Center](https://www.planningcenteronline.com/) and sends personalized celebration postcards via the WhatsApp Business Cloud API.

## Features

- **Automatic birthday/anniversary detection** from Planning Center People lists
- **Custom postcard generation** with dynamic text overlay on templates using Pillow
- **WhatsApp delivery** via approved Business Cloud API templates
- **Couple matching** — groups spouses by household for anniversary postcards
- **Spanish date formatting** — postcards display dates in Spanish
- **Docker support** — containerized for easy deployment on NAS/server

## Prerequisites

- Python 3.12+
- [Planning Center](https://api.planningcenteronline.com/) API credentials (App ID + Personal Access Token)
- [WhatsApp Business Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api) token and approved message templates
- Docker & Docker Compose (optional, for containerized deployment)

## Quick Start

### 1. Clone & Configure

```bash
git clone https://github.com/YOUR_USERNAME/birthday-bot.git
cd birthday-bot
cp .env.example .env
# Edit .env with your actual credentials
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run

```bash
python Birthday.py
```

### 4. Docker Deployment

```bash
docker compose up --build
```

## Environment Variables

See [.env.example](.env.example) for all required variables. **Never commit your `.env` file.**

| Variable | Description |
|:---------|:------------|
| `PC_APP_ID` | Planning Center OAuth App ID |
| `PC_SECRET` | Planning Center Personal Access Token |
| `WHATSAPP_API_TOKEN` | WhatsApp Business Cloud API token |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp sender phone number ID |
| `TARGET_PHONE_NUMBER` | Recipient phone number (digits only) |
| `GOOGLE_API_KEY` | Google GenAI API key (optional) |
| `SENDER_EMAIL` | Gmail address for fallback notifications |
| `SENDER_PASSWORD` | Gmail App Password |

## Project Structure

```
birthday/
├── Birthday.py              # Main application script
├── Dockerfile               # Container definition
├── docker-compose.yml       # Docker Compose config
├── requirements.txt         # Pinned Python dependencies
├── .env.example             # Environment variable template
├── .gitignore               # Git exclusions
├── .dockerignore            # Docker build exclusions
├── fonts/                   # Font files for postcard text
│   ├── Lora-Regular.ttf
│   ├── Lora-Bold.ttf
│   └── ...
└── postcard/
    ├── felicidades.png      # Postcard template image
    └── whatsapp_test_sender.py  # API test utility
```

## Security

- All secrets are loaded from environment variables via `.env` (never hardcoded)
- `.env` is excluded from git and Docker builds
- Docker container runs as non-root user
- API calls use explicit TLS verification and timeouts
- Error notifications are sanitized (no internal details sent externally)

## License

Private project — not for redistribution.
