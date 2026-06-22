# 🏥 MedNear AI

> **Professional Medical AI Assistant Bot for Telegram**

A production-ready Telegram bot powered by AI that provides medical consultations, symptom analysis, medicine information, appointment scheduling, and health monitoring — all in Uzbek, Russian, and English.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.13-blue.svg)](https://docs.aiogram.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-blue.svg)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ Features

### 🤖 AI Capabilities
- **Medical Chat** — GPT-4 powered medical conversations
- **Symptom Checker** — AI-driven symptom analysis with severity assessment
- **Medicine Advisor** — comprehensive drug information & interactions
- **PDF Analyzer** — extract & analyze medical documents (lab results, prescriptions)
- **OCR** — Google Vision powered image text extraction
- **Voice Transcription** — Whisper integration for voice messages
- **Lab Result Explainer** — AI explains blood test results in plain language
- **Nutrition Advisor** — personalized diet recommendations
- **Mental Health Support** — empathetic AI assistant

### 📱 Core Features
- 💊 **Medicine Database** — search 10,000+ medicines with side effects, interactions
- ⏰ **Smart Reminders** — medicine, water, vitamin, exercise tracking
- 📅 **Appointments** — book & manage doctor appointments
- 🏥 **Hospital Finder** — locate nearby hospitals, clinics, pharmacies
- 📊 **Health Tracking** — blood pressure, sugar, weight, BMI, heart rate
- 💉 **Vaccination History** — track all vaccinations
- 🚨 **Emergency Contacts** — quick access to emergency services
- 📄 **Medical Records** — prescriptions, lab results, diagnoses
- 🌐 **Multi-language** — Uzbek, Russian, English
- 💎 **Premium Subscriptions** — Payme, Click, Uzum, Telegram Stars
- 👥 **Referral System** — earn rewards for inviting friends
- 🏆 **Achievements** — gamified health tracking

### 🛠 Technical Features
- ⚡ **Async Architecture** — full async/await with aiogram 3
- 🗄 **PostgreSQL** — robust relational database
- 🔄 **Redis Caching** — high-performance caching layer
- 🐳 **Docker Ready** — full containerization
- 📈 **Prometheus + Grafana** — monitoring & metrics
- 🔒 **JWT Auth** — secure token-based authentication
- 🛡 **Rate Limiting** — flood protection & throttling
- 📝 **Structured Logging** — Loguru with rotation
- 🔄 **Migrations** — Alembic database migrations
- ⏰ **Scheduled Tasks** — APScheduler for reminders & stats
- 🎯 **FSM** — finite state machine for multi-step flows
- 🌐 **i18n** — internationalization support

## 🏗 Architecture

```
mednear-ai/
├── app/
│   ├── config.py            # Pydantic Settings configuration
│   ├── database/
│   │   ├── base.py          # SQLAlchemy declarative base
│   │   ├── enums.py         # 25+ application enums
│   │   ├── session.py       # Async DB session manager
│   │   └── models/
│   │       ├── user.py      # User, Profile, LoginHistory
│   │       ├── medical.py   # Chat, Message, AIHistory, Medicine
│   │       ├── health.py    # HealthMetric, Hospital, Appointment
│   │       └── payment.py   # Premium, Payment, Admin, Feedback
│   ├── repositories/        # Data access layer (10 repos)
│   │   ├── base.py          # Generic CRUD base
│   │   ├── user.py          # UserRepository
│   │   └── medical.py       # Chat, Medicine, Hospital, Appointment
│   ├── services/            # Business logic layer
│   │   ├── cache.py         # Redis cache service
│   │   ├── notification.py  # Push notifications
│   │   ├── scheduler.py     # APScheduler jobs
│   │   └── user.py          # User business logic
│   ├── keyboards/           # UI keyboards
│   │   ├── __init__.py      # Inline keyboards
│   │   └── reply.py         # Reply keyboards
│   ├── middlewares/         # Aiogram middlewares
│   │   └── __init__.py      # Logging, Throttling, Tracking
│   └── utils/               # Utilities
│       ├── logger.py        # Loguru configuration
│       └── helpers.py       # 16+ helper functions
├── bot/
│   ├── main.py              # Bot entry point
│   └── handlers/            # Bot handlers
│       ├── start.py         # /start, /help, /menu
│       ├── ai_chat.py       # AI chat handler
│       ├── symptom.py       # Symptom checker
│       ├── medicine.py      # Medicine search
│       ├── reminder.py      # Reminders
│       ├── appointment.py   # Appointments
│       ├── hospital.py      # Hospital finder
│       ├── profile.py       # User profile
│       ├── settings.py      # Settings
│       ├── premium.py       # Premium subscriptions
│       ├── feedback.py      # Feedback
│       ├── media.py         # Photo, voice, PDF
│       ├── admin.py         # Admin panel
│       └── errors.py        # Error handlers
├── migrations/              # Alembic migrations
├── monitoring/              # Prometheus, Grafana configs
├── docker-compose.yml       # Production stack
├── docker-compose.dev.yml   # Development stack
├── Dockerfile               # Production image
├── requirements.txt         # Python dependencies
├── alembic.ini              # Migration config
└── .env.example             # Environment template
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (recommended)

### 1. Clone & Configure

```bash
git clone https://github.com/KRYZENSYS/mednear-ai.git
cd mednear-ai
cp .env.example .env
# Edit .env with your values
```

### 2. Run with Docker (Recommended)

```bash
docker-compose up -d
docker-compose logs -f bot
```

### 3. Run Locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the bot
python -m bot.main
```

### 4. Get Bot Token

1. Talk to [@BotFather](https://t.me/BotFather) on Telegram
2. Create new bot with `/newbot`
3. Copy the token to `.env` as `BOT_TOKEN`
4. Get your Telegram user ID and set `BOT_ADMIN_IDS`

## ⚙️ Configuration

All configuration is via environment variables. See [`.env.example`](.env.example) for full list.

### Required Variables

```bash
BOT_TOKEN=your_telegram_bot_token
DB_PASSWORD=secure_password
REDIS_PASSWORD=redis_password
OPENAI_API_KEY=sk-xxx
GOOGLE_GEMINI_API_KEY=xxx
JWT_SECRET_KEY=change-this-in-production
ENCRYPTION_KEY=generate-fernet-key
```

## 📊 Database Schema

The application uses **30+ tables** organized into 4 categories:

- **User Management** (5 tables): User, Profile, DeviceSession, LoginHistory
- **Medical Core** (8 tables): Chat, Message, AIHistory, Symptom, Disease, Medicine, Reminder
- **Health Tracking** (10 tables): HealthMetric, Hospital, Appointment, Prescription, Vaccination
- **System & Admin** (10 tables): PremiumPlan, Payment, Admin, Feedback, Notification, Statistics

## 🎯 Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot & show main menu |
| `/menu` | Show main menu |
| `/chat` | Start AI medical chat |
| `/symptom` | Check symptoms |
| `/medicine` | Search medicine info |
| `/reminder` | Manage reminders |
| `/appointment` | Manage appointments |
| `/hospital` | Find hospitals |
| `/profile` | View profile |
| `/settings` | Bot settings |
| `/premium` | Premium subscription |
| `/language` | Change language |
| `/feedback` | Send feedback |
| `/cancel` | Cancel current operation |

## 💎 Premium Plans

| Plan | Duration | Price (UZS) |
|------|----------|-------------|
| Monthly | 30 days | 25,000 |
| Quarterly | 90 days | 65,000 |
| Yearly | 365 days | 200,000 |
| Lifetime | Forever | 500,000 |
| Telegram Stars | Varies | ⭐ Stars |

Premium features:
- Unlimited AI requests
- Priority response
- Voice transcription
- PDF analysis
- Advanced health insights
- No ads

## 🌐 Internationalization

MedNear AI supports three languages:
- 🇺🇿 Uzbek (default)
- 🇷🇺 Russian
- 🇬🇧 English

Users can switch language via `/language` command.

## 🔒 Security

- All sensitive data encrypted with Fernet
- Passwords hashed with bcrypt
- JWT-based authentication
- Rate limiting & flood protection
- SQL injection protection via SQLAlchemy ORM
- XSS protection via input sanitization
- CSRF protection for webhooks

## 📈 Monitoring

- **Prometheus metrics** at `:9090/metrics`
- **Grafana dashboards** at `:3000`
- **Health check** at `:9090/health`
- **Structured logs** in `logs/bot.log`
- **Error logs** in `logs/errors.log`

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 📞 Support

- 📧 Email: support@mednear.ai
- 💬 Telegram: [@MedNearSupport](https://t.me/MedNearSupport)
- 🌐 Website: https://mednear.ai

## 👥 Team

Built with ❤️ by the **KRYZENSYS** team.

---

**⚠️ Medical Disclaimer**: This bot provides AI-generated health information for educational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers with any questions you may have regarding a medical condition.