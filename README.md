# Bible in a Year (Windows Universal App)

Bible in a Year is a Windows‑friendly app that combines a classic daily reading plan with AI spiritual companions based on Saints Augustine and Aquinas. It supports offline‑friendly journaling, margin notes, and Ollama‑powered commentary.

## Features
- Daily reading structure with a chronological-style plan (generated locally)
- AI commentary, Q&A, and personalized insights
- Diary with margin notes saved for rereading
- Progress tracking and themed devotionals
- Offline‑friendly local storage
- Credits for CCEL, Gutenberg, and Internet Archive

## Reading Plan
The app uses `data/reading_plans.json` if present. If the file is missing or incomplete, the backend will generate a complete 365‑day chronological-style plan on first run.

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
To use your local Bible folders (YLT, ASV, DBY), edit:
```
data/bible_sources.json
```
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
