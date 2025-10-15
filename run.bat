@echo off
call venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --log-level debug
