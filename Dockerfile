FROM python:latest
WORKDIR /server
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apt-get update && apt-get install -y gcc
COPY requirements.txt .
RUN pip install -r requirements.txt 
RUN echo "admin:letmein" > /creds.txt
EXPOSE 5000
CMD ["flask", "run", "--debug"] 
