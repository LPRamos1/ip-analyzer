# IP Analyzer
#### Video Demo: <Link>

## 📌 Overview
A command-line tool that extracts, validates, and enriches IPv4 addresses from log files using external geolocation data.
---

## 🚀 Features

- Extract IPv4 addresses from multiple file formats (.txt, .log, .csv, .json)
- Validate IP addresses using custom rules
- Fetch geolocation data using external API (batch requests)
- Handle rate limits with controlled request batching
- Display results in a formatted table
---

## 🛠️ Tech Stack

- Python 3.11
- Requests
- Regex
- Tabulate
---

## ⚙️ How it works

The tool reads a file, extracts potential IP addresses using regex, validates them, and sends them in batches to a geolocation API.

Input file → Extraction → Validation → API enrichment → Output report

---

## 📦 Setup

```bash
git clone https://github.com/LPRamos1/ip-analyzer.git
pip install -r requirements.txt


## ▶️ Run

```bash
python project.py logs/acess.log
```

## ✅ Tests

```bash
pytest .
```

🎯 Purpose

This project was built as part of CS50P to practice file processing, data validation, and working with external APIs in Python.
---

## 📚 What I learned

- File parsing and data extraction techniques
- Regular expressions for pattern matching
- Working with external APIs in Python
- Handling rate limits and batch processing
- Structuring a CLI application
