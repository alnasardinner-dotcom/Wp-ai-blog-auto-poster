@echo off
title WordPress Rank Math AI Auto-Poster
cd /d "C:\Users\DFIT\.gemini\antigravity\scratch\wp-ai-blog-auto-poster"
echo ===================================================
echo   Starting WordPress AI Content Generator App...
echo ===================================================
echo.
python -m streamlit run app.py
echo.
echo ===================================================
echo   Application stopped or encountered an error.
echo ===================================================
pause
