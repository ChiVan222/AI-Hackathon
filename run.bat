@echo off
call venv\Scripts\activate
pip install -r requirements.txt
python app/utils/setup_idea_db.py
uvicorn app.main:app --reload --log-level debug
