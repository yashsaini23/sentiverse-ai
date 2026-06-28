🎬 SentiVerse – AI Entertainment Recommendation Engine

An AI-powered entertainment recommendation platform that understands user emotions and suggests personalized content using Natural Language Processing (NLP) and Sentiment Analysis.

📌 Overview

SentiVerse is an intelligent recommendation engine that recommends movies, TV shows, anime, comics, books, and other entertainment content based on a user's mood and emotions rather than simple genres or ratings.

Instead of searching manually, users can describe how they feel (e.g., "I'm feeling lonely", "I want something uplifting", "I need motivation"), and SentiVerse analyzes the sentiment using NLP before generating personalized recommendations.

✨ Features
🎭 Sentiment-based recommendations
🧠 Natural Language Processing (NLP)
🤖 AI-powered recommendation engine
🎬 Movies & TV Shows recommendations
🍿 Anime recommendations
📚 Comics & Books recommendations
🔍 Smart text analysis
⚡ FastAPI REST API backend
🐳 Docker support
📈 Scalable project architecture
🛠 Tech Stack
Languages
Python
Backend
FastAPI
REST API
Uvicorn
AI & Machine Learning
Natural Language Processing (NLP)
Scikit-learn
Pandas
NumPy
Development Tools
Docker
Git
GitHub
VS Code
🏗 Architecture
User Input
     │
     ▼
Sentiment Analysis (NLP)
     │
     ▼
Recommendation Engine
     │
     ▼
Content Filtering & Ranking
     │
     ▼
Personalized Recommendations
📂 Project Structure
sentiverse/
├── .github/workflows/         # CI/CD pipelines
├── backend/                   # FastAPI Python Server
│   ├── app/
│   │   ├── api/               # REST endpoints
│   │   ├── core/              # Configs, Security, JWT
│   │   ├── db/                # PostgreSQL & VectorDB clients
│   │   ├── ml/                # AI Models
│   │   │   ├── model_loader.py
│   │   │   ├── embeddings.py
│   │   │   └── emotion_classifier.py
│   │   ├── services/          # Business logic
│   │   │   └── recommendation.py
│   │   ├── schemas/           # Pydantic models
│   │   └── main.py            # FastAPI entry point
│   ├── tests/                 # Pytest directory
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                  # Next.js Application
│   ├── src/
│   │   ├── app/               # Pages (page.tsx, layout.tsx)
│   │   ├── components/        # UI (MoodInput, MediaCard)
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # API clients, utilities
│   │   └── store/             # Zustand state management
│   ├── public/                # Static assets
│   ├── tailwind.config.ts
│   ├── package.json
│   └── Dockerfile
├── data/                      # Initial datasets (ignored in git)
├── docker-compose.yml
└── README.md

🚀 Installation
git clone https://github.com/yourusername/SentiVerse.git

cd SentiVerse

pip install -r requirements.txt

uvicorn app.main:app --reload
📡 API
Method	Endpoint	Description
POST	/recommend	Generate recommendations from user sentiment
GET	/health	Health check
GET	/docs	Interactive Swagger documentation
📷 Screenshots

Add screenshots of:

Home Page
Recommendation Results
API Documentation (Swagger)
Dashboard (if available)
🎯 Future Enhancements
User authentication
Watchlist management
Personalized user profiles
Recommendation history
Hybrid recommendation models
LLM-powered conversational recommendations
Multi-language sentiment analysis
Mobile application
📄 License

This project is licensed under the MIT License.

👨‍💻 Author

Yash Saini

B.Tech Computer Science (AI & ML)

Python Developer | AI/ML Developer | Web Developer

GitHub: https://github.com/yourusername

LinkedIn: https://linkedin.com/in/yourprofile
