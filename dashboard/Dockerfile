FROM python:latest

WORKDIR /app

COPY requirements.txt .
COPY streamlit_app.py .
COPY .streamlit /.streamlit

RUN pip install -r requirements.txt

CMD streamlit run streamlit_app.py