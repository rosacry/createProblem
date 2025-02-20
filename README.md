# Competitive Programming Problem Setup Tool

This repository contains a Python script, [`create_problem.py`](./create_problem.py), that automates creating a folder and a starter code file for competitive programming problems from multiple sources:

1. **LeetCode** (via [`alfaarghya/alfa-leetcode-api`](https://github.com/alfaarghya/alfa-leetcode-api))  
2. **Codeforces** (via official API + HTML scraping for the full statement)  
3. **VJudge** (HTML scraping for problem statements)  
4. **Custom** (no external data, just create a folder and skeleton)

It supports **C++**, **C**, **Python**, and **Java** skeletons in either **Minimal** or **Extended** format.

---

## Features

1. **LeetCode**  
   - Automatically fetches the problem title, difficulty, and content via [`alfaarghya/alfa-leetcode-api`](https://github.com/alfaarghya/alfa-leetcode-api).  
   - **Important**: The `alfaarghya/alfa-leetcode-api` code is **Node.js/TypeScript** and does **not** install as a Python library. You must either run its Node server and query it via HTTP or replicate the logic in Python.  
   - If your LeetCode session cookie is invalid or not set up, the script prompts you gracefully, so it won’t crash.  

2. **Codeforces**  
   - Fetches metadata (title, tags) from the official Codeforces API.  
   - **Scrapes** the actual problem statement HTML from `https://codeforces.com/contest/<contestId>/problem/<index>` to include in your file comments.  

3. **VJudge**  
   - **Scrapes** the problem statement from `https://vjudge.net/problem/<OJ>-<ProblemID>` (e.g., `https://vjudge.net/problem/LightOJ-1000`).  
   - If any authentication is required, the script attempts to retrieve the public portion, or it will fallback gracefully.  

4. **Custom**  
   - No external calls; simply creates a folder with your chosen name.  

5. **Multiple Languages**  
   - **C++**, **C**, **Python**, **Java**  
   - Additional skeleton logic for “Minimal” (bare-bones `main()`) or “Extended” (class or function-based approach).  

6. **Automated Folder Creation**  
   - Creates a folder named according to the problem source and ID, e.g., `leetcode_p13`, `codeforces_p4A`, `vjudge_problem_lightoj1000`, or your custom name.  

7. **Configurable Skeleton**  
   - **Extended** skeleton can prompt for class/struct/function details.  
   - The script writes comments at the top of the file containing problem metadata or statement snippet.

---

## Installation

(Optional but Recommended) **Create and Activate a Python Virtual Environment**

   This helps avoid system-level Python issues (especially on Debian/Ubuntu with PEP 668).

   ```bash
   python3 -m venv env
   source env/bin/activate
   pip install -r requirements.txt

