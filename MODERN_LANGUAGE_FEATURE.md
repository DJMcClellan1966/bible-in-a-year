# Enhanced Bible with Modern Language

## Feature Overview

The app now includes an **Enhanced Reading Mode** with modern language explanations that make Bible passages more accessible and easier to understand.

---

## What It Does

When you explore a Bible passage in Discovery Mode, you'll see a **"✨ Modern Language"** button. Click it to get:

1. **Clear, Modern Paraphrase** - The passage rewritten in contemporary English
2. **Preserved Meaning** - Original theological accuracy maintained
3. **Accessible Language** - Archaic terms and cultural references explained simply
4. **Same Structure** - Original flow and structure preserved

---

## How It Works

### In Discovery Mode:

1. Enter any passage (e.g., "Genesis 1", "Romans 8")
2. Click "Discover Deeply"
3. View the original passage text
4. Click **"✨ Modern Language"** button
5. See modern language explanation appear below

### Example:

**Original (KJV/YLT):**
> "In the beginning God created the heaven and the earth. And the earth was without form, and void; and darkness was upon the face of the deep."

**Modern Language:**
> "At the very start of everything, God created the heavens and the earth. At that time, the earth had no shape or structure—it was completely empty and formless. Darkness covered the surface of the deep waters."

---

## API Endpoint

### `POST /api/bible/modern-language`

**Request:**
```json
{
  "passage": "Genesis 1",
  "original_text": "1: In the beginning..."  // Optional
}
```

**Response:**
```json
{
  "passage": "Genesis 1",
  "original": "1: In the beginning...",
  "modern": "At the very start of everything...",
  "timestamp": "2024-01-01T12:00:00"
}
```

---

## Adding Modern Bible Translations

You can also add entire modern Bible translations (like NIV, NLT, NET, CSB) to use as your primary text. See `ADDING_BIBLE_VERSIONS.md` for instructions.

### Recommended Free Modern Translations:

1. **NET Bible** (New English Translation) - https://netbible.org/download/
   - Free, open access
   - Excellent quality
   - Modern language

2. **World English Bible (WEB)** - https://worldenglish.bible/
   - Public domain
   - Modern language

3. **Lexham English Bible (LEB)** - https://lexhamenglishbible.com/
   - Free for personal use
   - Study-focused

---

## Benefits

✅ **More Accessible** - Easier to understand for modern readers  
✅ **Preserves Meaning** - Maintains theological accuracy  
✅ **Side-by-Side** - See original and modern together  
✅ **Toggle On/Off** - Use when needed  
✅ **AI-Powered** - Uses Ollama for intelligent paraphrasing  

---

## Technical Details

- Uses Ollama LLM for generation
- Requires Ollama to be running
- Generates on-demand (not pre-cached)
- Works with any passage
- Preserves original structure and flow

---

**Result:** A Bible that's accessible in modern language while preserving the depth and meaning of the original text.
