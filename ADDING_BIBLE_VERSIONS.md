# Adding Modern Bible Versions

## Currently Supported Versions

You currently have these versions configured:
- **YLT** (Young's Literal Translation, 1862) - Very literal translation
- **ASV** (American Standard Version, 1901) - Formal equivalence
- **DBY** (Darby Bible, 1890) - Literal translation

All are older translations. Below are modern options.

---

## Modern Bible Versions You Can Add

### Popular Modern Translations (2000+):

#### 1. **ESV** (English Standard Version, 2001)
- **Type**: Essentially literal, word-for-word
- **Popularity**: Very popular in Reformed/Eastern Orthodox circles
- **Readability**: Moderate
- **Where to get**: Available from ESV.org (may need licensing for bulk)

#### 2. **NIV** (New International Version, 2011)
- **Type**: Thought-for-thought (dynamic equivalence)
- **Popularity**: Most widely used modern translation
- **Readability**: Very readable
- **Where to get**: Biblica.com (free for personal use)

#### 3. **NASB** (New American Standard Bible, 2020)
- **Type**: Very literal, word-for-word
- **Popularity**: Popular with study-focused readers
- **Readability**: Moderate (more literal)
- **Where to get**: Lockman Foundation

#### 4. **NLT** (New Living Translation, 2015)
- **Type**: Thought-for-thought, very readable
- **Popularity**: Very popular for daily reading
- **Readability**: Very easy to read
- **Where to get**: Tyndale House Publishers

#### 5. **NKJV** (New King James Version, 1982)
- **Type**: Formal equivalence, updates KJV language
- **Popularity**: Popular for traditional + readable balance
- **Readability**: Good (modernized KJV)
- **Where to get**: Thomas Nelson

#### 6. **CSB** (Christian Standard Bible, 2017)
- **Type**: Optimal equivalence (balanced)
- **Popularity**: Growing popularity
- **Readability**: Very readable
- **Where to get**: Holman Bible Publishers

#### 7. **NET** (New English Translation, 2019)
- **Type**: Balanced with extensive notes
- **Popularity**: Popular for study (free, open)
- **Readability**: Good
- **Where to get**: Bible.org (FREE, open access)

---

## Free/Open Source Modern Translations

### Available for Free Download:

1. **NET Bible** (New English Translation)
   - Website: https://netbible.org/download/
   - Format: HTML, XML, JSON available
   - License: Free for personal use

2. **World English Bible (WEB)**
   - Website: https://worldenglish.bible/
   - Format: HTML, text available
   - License: Public domain

3. **Lexham English Bible (LEB)**
   - Website: https://lexhamenglishbible.com/
   - Format: Various formats available
   - License: Free for personal use

4. **Updated King James Version (UKJV)**
   - Website: Various sources
   - Format: HTML available
   - License: Public domain derivative

---

## How to Add a New Version

### Step 1: Get the Bible Files

You need the Bible in HTML format (one file per chapter). Example structure:
```
version_folder/
  Genesis/
    Genesis_1.html
    Genesis_2.html
    ...
  Exodus/
    Exodus_1.html
    ...
```

### Step 2: Place Files in a Folder

Create a folder (e.g., `C:\Users\DJMcC\OneDrive\Desktop\bible_in_year\esv`) and put your HTML files there.

### Step 3: Update `data/bible_sources.json`

Add your new version:

```json
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
    },
    "ESV": {
      "title": "English Standard Version",
      "path": "C:\\Users\\DJMcC\\OneDrive\\Desktop\\bible_in_year\\esv",
      "format": "html"
    },
    "NET": {
      "title": "New English Translation",
      "path": "C:\\Users\\DJMcC\\OneDrive\\Desktop\\bible_in_year\\net",
      "format": "html"
    }
  }
}
```

### Step 4: Restart the Backend

The new version will appear in the version selector after restarting.

---

## Recommended Modern Versions to Add

### Best for Study:
1. **ESV** - Most popular study Bible
2. **NASB** - Most literal modern translation
3. **NET** - FREE with extensive study notes

### Best for Reading:
1. **NIV** - Most widely used, very readable
2. **NLT** - Easiest to read modern translation
3. **CSB** - Balanced and readable

### Best Free Options:
1. **NET Bible** - Free, open, excellent quality
2. **World English Bible** - Public domain, modern language
3. **Lexham English Bible** - Free, study-focused

---

## Format Requirements

The HTML files should have verses in a format that can be parsed. The current parser looks for patterns like:

```html
<span class="verse">1 In the beginning...</span>
```

Or:

```html
<span id="v1">1</span> In the beginning...
```

If your HTML format is different, you may need to adjust the parsing in `backend/bible_reader.py` in the `_extract_verses` method.

---

## Quick Start: Add NET Bible (Free)

1. Download from https://netbible.org/download/
2. Extract HTML files to: `C:\Users\DJMcC\OneDrive\Desktop\bible_in_year\net`
3. Edit `data/bible_sources.json` to add NET entry
4. Restart backend

The NET Bible is excellent quality and completely free!

---

## Checking If Your HTML Format Works

The app will try to parse your HTML files. If verses don't appear:

1. Check the HTML structure of one chapter file
2. Look for verse numbers and text patterns
3. You may need to adjust the regex in `_extract_verses` method

Common formats that work:
- Verse numbers as `<span>` tags
- Verse numbers as text with numbers (1, 2, 3...)
- Verses separated by line breaks or HTML elements

---

**Note**: Some modern Bible translations may have copyright restrictions. Always check licensing before distributing. NET Bible and World English Bible are free for personal use.
