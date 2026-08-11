set -a
. .env
set +a
uvicorn main:fastapi_app --port=8008 --reload &
streamlit run app.py