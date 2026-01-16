# Bible in a Year with AI Spiritual Companions

A modern web application that combines traditional Bible reading plans with AI-powered spiritual guidance from Saints Augustine and Aquinas. Experience Scripture in a new way with personalized commentary, reflective journaling, and intelligent conversation about theology and faith.

## 🌟 Features

### Core Functionality
- **Daily Bible Readings**: Traditional "Bible in a Year" reading plans with modern enhancements
- **AI Spiritual Companions**: Interactive conversations with Saints Augustine and Aquinas
- **Personal Diary**: Reflective journaling with margin notes for deeper insights
- **Progress Tracking**: Visual progress indicators and milestone celebrations
- **Offline Support**: Full functionality without internet connection

### AI Features
- **Personalized Commentary**: Context-aware biblical interpretation
- **Theological Q&A**: Ask questions about Scripture, doctrine, and spiritual life
- **Reflective Guidance**: AI-powered insights for personal growth
- **Multi-Saint Wisdom**: Choose between Augustine, Aquinas, or combined perspectives

### User Experience
- **Responsive Design**: Works beautifully on desktop, tablet, and mobile
- **Accessibility**: Screen reader friendly with keyboard navigation
- **Dark/Light Themes**: Multiple theme options for comfortable reading
- **Customizable Fonts**: Adjustable text sizes for different preferences

## 🚀 Quick Start

### Prerequisites
- Python 3.11 with pip (recommended on Windows)
- Node.js 16+ with npm
- Ollama (for local AI models)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bible-in-a-year
   ```

2. **Set up the backend**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt

   # The backend will create a SQLite database automatically
   ```
   For full RAG and document ingestion on Python 3.11:
   ```bash
   pip install -r requirements-full.txt
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. **Set up Ollama (for AI features)**
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama2:7b  # Base model
   ollama pull llama2:13b # For combined wisdom (optional)
   ```

5. **Add Saint Augustine's writings**
   ```
   # Place your downloaded Augustine texts in:
   data/augustine/
   # Supported formats: .txt, .pdf, .docx
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   python -m backend.main
   # Or: uvicorn backend.main:app --reload
   ```
   The API will be available at `http://localhost:8000`

2. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```
   The app will be available at `http://localhost:5173`

3. **Open your browser** and navigate to `http://localhost:5173`

## 📖 How to Use

### Daily Reading
1. Navigate to the "Daily Reading" tab
2. Use the date picker to select any day
3. Read the assigned Bible passages
4. Click "Ask Augustine" or "Ask Aquinas" for commentary
5. Add personal reflections in the Diary tab

### AI Conversations
1. Go to the "AI Helpers" page
2. Select your preferred spiritual companion
3. Ask questions about Scripture, theology, or spiritual guidance
4. Receive personalized, contextually-aware responses

### Personal Diary
1. Each day's reading has a dedicated diary entry
2. Add personal reflections and thoughts
3. Create margin notes for specific verses or passages
4. AI insights can be stored alongside your reflections

### Progress Tracking
- View completion statistics
- See milestone achievements
- Track reading streaks and consistency

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Database**: SQLite with SQLAlchemy ORM
- **AI Integration**: Ollama client with local model support
- **RAG System**: Lightweight keyword index by default (optional full RAG in `requirements-full.txt`)
- **Bible Reader**: Modular reading plan management
- **API**: RESTful endpoints with automatic documentation

### Frontend (React/TypeScript)
- **Framework**: React 18 with TypeScript
- **Routing**: React Router for navigation
- **Styling**: Tailwind CSS with custom components
- **State Management**: React hooks and context
- **API Client**: Axios with offline queue support

### Data Flow
```
User Request → Frontend → API → RAG System → Ollama → AI Response → Frontend Display
```

## 📚 Data Sources & Credits

This application uses materials from:

- **Christian Classics Ethereal Library (CCEL)**: Public domain theological texts
- **Project Gutenberg**: Classic Christian literature
- **Internet Archive**: Historical religious documents
- **Bible Texts**: Public domain KJV and other translations

### Attribution Requirements
When using downloaded texts, please attribute to the original sources as required by their licenses.

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=sqlite:///./bible_app.db

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:7b

# Optional: Remote Ollama instance
OLLAMA_REMOTE_URL=https://your-remote-ollama-instance.com

# Development
DEBUG=True
```

### Reading Plans
Customize reading plans by editing `data/reading_plans.json`:

```json
{
  "name": "Custom Reading Plan",
  "readings": {
    "2024-01-01": {
      "passages": ["Genesis 1-3", "Psalm 1"],
      "theme": "Creation"
    }
  }
}
```

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- **Additional Saints**: Add more theological figures (Thomas Merton, C.S. Lewis, etc.)
- **Bible Translations**: Support for multiple translations
- **Reading Plans**: Alternative reading schedules
- **Languages**: Internationalization support
- **Mobile App**: React Native companion app

### Development Setup
```bash
# Fork and clone
git clone your-fork-url
cd bible-in-a-year

# Set up development environment
pip install -r requirements.txt
cd frontend && npm install

# Run tests
pytest backend/tests/
cd frontend && npm test

# Submit pull request
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

### Content Licensing
- **Application Code**: MIT License
- **AI Training Data**: Subject to original source licenses
- **Bible Texts**: Public domain (KJV) or licensed from providers
- **Theological Texts**: Various open licenses (CCEL, Gutenberg, etc.)

## 🙏 Acknowledgments

- **Saints Augustine and Aquinas**: For their timeless wisdom
- **Open Source Community**: For the tools that made this possible
- **Beta Users**: For feedback and encouragement
- **Christian Tradition**: For 2000 years of spiritual guidance

## 🐛 Troubleshooting

### Common Issues

**Ollama not responding**
```bash
# Check if Ollama is running
ollama list

# Restart Ollama service
ollama serve
```

**Database errors**
```bash
# Reset database
rm bible_app.db
python -c "from backend.database import init_db; init_db()"
```

**Frontend build issues**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Support
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: [your-email@example.com]

---

*"The Bible is like a letter God has sent to us; prayer is like our answer."*
— Saint Augustine