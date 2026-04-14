# IP Analyzer
#### Video Demo: <Link>

## 📌 Overview
The **IP Analyzer** The IP Analyzer is a command-line tool that processes raw log files to extract, validate, and geolocate IPv4 addresses, producing structured and readable network reports.

## 🛠️ Architecture Overview

The project is structured into three main layers:
- Input validation and file handling
- IP extraction and normalization
- API integration and result reporting

## 🚀 Key Features

- Multi-format file support (.txt, .log, .csv, .json)
- IPv4 extraction using regex + custom validation
- Batch geolocation via external API (up to 50 IPs per request)
- Type-safe and modular Python design
- Formatted terminal output using tabulate

## ⚡ Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/LPRamos1/ip-analyzer.git
pip install -r requirements.txt
```

## ▶️ Run

```bash
python project.py logs/acess.log
```

## ✅ Tests

```bash
pytest .
```

## 📂 File Structure
- **project.py:** The main engine. Contains the orchestrator function (`ip_info`), extraction logic, and API communication layer.
- **test_project.py:** A comprehensive test suite utilizing `pytest`, with advanced techniques like **monkeypatching** and **mocking** to simulate file systems and API responses.
- **requirements.txt:** Lists the external dependencies (`requests`, `tabulate`) necessary for the project.

## 🧠 Design Decisions

- JSON files are normalized into strings to ensure consistent parsing across different structures.
- API requests are batched to reduce external calls and improve performance.
- Rate limiting is applied to comply with API constraints and avoid request failures.

## 🎯 Motivation
This project was built as part of CS50P to apply Python fundamentals in a real-world data processing problem involving file parsing, validation, and API integration.