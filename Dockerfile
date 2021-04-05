FROM python:3.8-alpine
WORKDIR /code
RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8082

#COPY . .
# These line for /stats_server.py
COPY ./src/stats_server.py .
RUN chmod +x ./stats_server.py
#CMD [ "python", "./stats_server.py" ]
