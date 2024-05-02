FROM python:latest

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

EXPOSE 8200

COPY streamlit_app.py .
COPY charts.py .
COPY case_profiles.py .
COPY layout.py .
COPY .streamlit /.streamlit

CMD streamlit run streamlit_app.py --server.port 8200