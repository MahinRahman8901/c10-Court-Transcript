FROM python:latest

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

EXPOSE 8200

COPY streamlit_app.py .
COPY .streamlit /.streamlit

CMD streamlit run streamlit_app.py --server.port 8200