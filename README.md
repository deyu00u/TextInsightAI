# TextInsight AI — Offline update
1. Stop your current Streamlit server with Ctrl+C in Command Prompt.
2. Back up the existing project if desired. Extract this ZIP and copy all its files into the existing TextInsightAI folder (the folder containing app.py and .venv). Replace matching files. Keep .venv and sample.pdf.
3. Double-click START_LOCAL_AI.bat. This installs the extra local AI library and starts Streamlit.
4. Paste English text or upload a PDF and click Analyze document. The initial AI request downloads the model into .model_cache. No API key is needed.
5. Delete the old Gemini API keys in Google AI Studio if no longer needed, especially any exposed key.

The first download requires internet. The local AI selects source sentences using neural embeddings; it is not a generative chatbot. See PROJECT_DOCUMENTATION.md. To share the project, exclude .venv, .model_cache and any .env containing old credentials.
