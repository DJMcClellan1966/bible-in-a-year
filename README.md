# Bible Discovery - Deep Exploration App

Bible Discovery is a Windows‑friendly app for deep, meaningful Bible exploration when you have time. No pressure, no schedule - just pick any passage and explore with insights from Saints Augustine, Aquinas, and modern scholars.

## Philosophy

**For people who:**
- Struggle with daily reading plans
- Want deep meaning, not surface reading
- Need spiritual connection without pressure
- Value quality over quantity

**What makes this different:**
- ✅ No reading plan pressure - explore what interests you
- ✅ Deep commentary from church fathers and scholars
- ✅ Historical context and connections automatically included
- ✅ Thematic paths for guided exploration (no timeline)
- ✅ Available when you need spiritual connection

## Features
- **Discovery Mode** - Pick any passage, get deep exploration with multiple commentary perspectives
- **Historical Context** - Timeline events, cultural background, character information
- **Scriptural Connections** - Related passages, themes, and echoes automatically discovered
- **Thematic Paths** - Pre-curated studies (e.g., "The Journey of Faith", "Prophecy & Fulfillment")
- AI commentary from Augustine, Aquinas, and combined perspectives
- Character studies, narrative reconstruction, and timeline visualization
- Offline‑friendly local storage

## Requirements
- Python 3.11
- Ollama (optional, for AI commentary)

## Install
```bash
pip install -r requirements.txt
```

For full ingestion + RAG on Python 3.11:
```bash
pip install -r requirements-full.txt
```

## Run (Windows Desktop)
```bash
python desktop_app.py
```

## Run (API + Web)

### Local Access Only
```bash
python -m backend.main
```
Open `http://127.0.0.1:8000/static/index.html`

### Access from iPad/Network
```bash
python run_for_ipad.py
```
Then access from iPad: `http://YOUR_IP_ADDRESS:8000/static/index.html`

See `IPAD_ACCESS_GUIDE.md` for detailed instructions.

## Data Sources
Place your Saint Augustine files in:
```
data/augustine/
```

Place your Saint Thomas Aquinas files in:
```
data/aquinas/
```

## Bible Text
To display full passages, place a JSON file at:
```
data/bible_text.json
```
Format example:
```
{
  "version": "KJV",
  "books": {
    "Genesis": {
      "chapters": {
        "1": {
          "verses": {
            "1": "In the beginning God created the heaven and the earth."
          }
        }
      }
    }
  }
}
```

## Ollama
Set these env vars if needed:
```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:7b
OLLAMA_REMOTE_URL=https://your-remote-ollama-instance.com
```

The backend will try the local Ollama first and fall back to `OLLAMA_REMOTE_URL` if local Ollama is not available.

## Bible Versions (HTML folders)
To use your local Bible folders, edit:
```
data/bible_sources.json
```

**Currently configured**: YLT, ASV, DBY (all older translations)

**Want modern versions?** See `ADDING_BIBLE_VERSIONS.md` for instructions on adding:
- ESV, NIV, NASB, NLT, NKJV, CSB, NET (and more)
- Free options: NET Bible, World English Bible
Example:
```
{
  "default_version": "YLT",
  "sources": {
    "YLT": {
      "title": "Young's Literal Translation",
      "path": "C:\\Users\\DJMcC\\OneDrive\\Desktop\\bible_in_year\\englyt",
      "format": "html"
    },
    "ASV": {
      "title": "American Standard Version",
      "path": "C:\\Users\\DJMcC\\OneDrive\\Desktop\\bible_in_year\\asv",
      "format": "html"
    },
    "DBY": {
      "title": "Darby Bible",
      "path": "C:\\Users\\DJMcC\\OneDrive\\Desktop\\bible_in_year\\engDBY",
      "format": "html"
    }
  }
}
```
