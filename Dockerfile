FROM python:latest
WORKDIR /server
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apt-get update && apt-get install -y gcc firefox-esr iputils-ping
COPY requirements.txt .
RUN pip install -r requirements.txt 
RUN echo "admin:letmein" > /credentials
EXPOSE 5000
CMD ["flask", "run", "--debug"] 
