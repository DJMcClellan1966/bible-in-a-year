# Faster Models & Content Prebuilding Guide

## Current Setup
- **Default Model**: `llama2:7b` (slower but higher quality)
- **Caching**: Some content is cached (character bible, commentaries)
- **Pre-generation**: Limited (Genesis corpus, some commentaries)

---

## Option 1: Use Faster Models

### Recommended Fast Models (Ollama)

1. **llama3.2:1b** - Fastest, good for simple tasks
   - Speed: ⚡⚡⚡⚡⚡
   - Quality: ⭐⭐⭐
   - Best for: Quick responses, simple commentary

2. **phi3:mini** - Fast and efficient
   - Speed: ⚡⚡⚡⚡
   - Quality: ⭐⭐⭐⭐
   - Best for: Balanced speed/quality

3. **llama3.2:3b** - Good balance
   - Speed: ⚡⚡⚡
   - Quality: ⭐⭐⭐⭐
   - Best for: Most tasks

4. **qwen2.5:1.5b** - Very fast, decent quality
   - Speed: ⚡⚡⚡⚡⚡
   - Quality: ⭐⭐⭐
   - Best for: Quick generation

### How to Use Faster Models

**Option A: Set Environment Variable**
```bash
# Windows PowerShell
$env:OLLAMA_MODEL="llama3.2:1b"
python -m backend.main

# Or in .env file
OLLAMA_MODEL=llama3.2:1b
```

**Option B: Use Different Models for Different Tasks**
- Fast model for simple tasks
- Larger model for complex tasks

---

## Option 2: Prebuild Content (Recommended)

Pre-generate content so users get instant responses.

### What Can Be Prebuilt

1. **Character Bible Perspectives**
   - All major characters × popular passages
   - Full chapters for key characters

2. **Commentaries**
   - Augustine/Aquinas on all passages
   - Already partially done

3. **Daily Discoveries**
   - Generate for next 365 days

4. **Story Narratives**
   - All biblical stories pre-reconstructed

5. **Character Chapters**
   - Full books from character perspectives

---

## Implementation: Prebuild Script

I'll create a script to pre-generate all character bible content and other frequently accessed content.
