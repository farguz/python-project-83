# Page Analyzer by farguz  
[![hexlet-check](https://github.com/farguz/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/farguz/python-project-83/actions/workflows/hexlet-check.yml)  
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=farguz_python-project-83&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=farguz_python-project-83)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=farguz_python-project-83&metric=bugs)](https://sonarcloud.io/summary/new_code?id=farguz_python-project-83)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=farguz_python-project-83&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=farguz_python-project-83)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=farguz_python-project-83&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=farguz_python-project-83)  
  
### Deployed version here -> [click (render.com)](https://page-analyzer-2cup.onrender.com/)

**Page Analyzer** is a full-stack web application designed to analyze specified web pages for SEO suitability. It crawls a given URL, checks for its availability, and extracts critical metadata such as HTML tags (`<h1>`, `<title>`, and `<meta description>`).

## Features

* URL Management: Add and store a list of websites for monitoring.
* URL Validation: Ensures URLs are valid and prevents duplicate entries through normalization.
* SEO Analysis: Automated fetching of HTTP status codes and SEO-related HTML tags using `BeautifulSoup`.
* Historical Data: Track multiple checks over time for every registered website.
* Responsive UI: Clean interface built with Bootstrap 5.

## Tech Stack

* **Language:** Python 3.10+
* **Framework:** Flask (with Flask-WTF)
* **Database:** PostgreSQL (with psycopg_pool)
* **Parsing** BeautifulSoup4 (with lxml)
* **Frontend:** Django Templates + Bootstrap 5
* **Package Manager:** uv
* **Extra:** gunicorn, ruff, python-dotenv

## Installation & Setup

This project uses `uv` for fast package management. It also includes a `Makefile` to make commands easier.

**0. Alternative**  

You can use deployed version [here (render.com)](https://page-analyzer-2cup.onrender.com/).

**1. Clone the repository**
```bash
git clone git@github.com:farguz/python-project-83.git
cd python-project-83
```
**2. Set environment**
```bash
cp .env.example .env
# manually set SECRET_KEY, DATABASE_URL variables
```
**3. Install dependencies:**
```bash
make build
```
**4. Run the application in dev or production mode:**  
```bash
make dev
```
or
```bash
make start
```