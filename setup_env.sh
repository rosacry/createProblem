#!/usr/bin/env bash

set -e  # Exit on error

# 1) Check if 'env' folder already exists:
if [ -d "env" ]; then
  echo "Virtual environment 'env' already exists. Activating it."
else
  echo "Creating a new virtual environment in 'env'..."
  python3 -m venv env
fi

# 2) Activate environment
echo "Activating virtual environment..."
source env/bin/activate

# 3) Install Python requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 4) (Optional) Any post-install steps, e.g. running the Node server or setting environment variables
# This is where you'd mention how to start the alfaarghya/alfa-leetcode-api if you want
echo "All set! You can now run 'python create_problem.py' or './create_problem.py' inside this environment."

