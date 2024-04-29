FROM python:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY streamlit_app.py .
COPY .streamlit /.streamlit

CMD streamlit run streamlit_app.py