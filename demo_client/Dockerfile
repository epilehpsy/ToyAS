FROM python:3.8.5-slim-buster

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--debug"]

