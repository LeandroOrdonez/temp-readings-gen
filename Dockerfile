FROM python:3.8.0-slim

ENV BBOX "51.32288838086245,4.091720581054688,51.1509246836981,4.752960205078125"
ENV AVG_TEMP 19.0
ENV KAFKA_TOPIC 'temperature-readings'
ENV KAFKA_BROKER "kafka_broker:9092"
ENV RND_SEED 0.0

WORKDIR /app

ADD . /app

#RUN pwd

RUN apt-get clean \
    && apt-get update 
    
RUN apt-get install -y htop build-essential python-dev python3-dev 

RUN pip install -r requirements.txt --src /usr/local/src

# Add wait-for-it
COPY wait-for-it.sh wait-for-it.sh 
RUN chmod +x wait-for-it.sh

ENTRYPOINT [ "sh", "-c" ]
CMD ["./wait-for-it.sh ${KAFKA_BROKER} --strict --timeout=30 -- python run.py --bbox \"${BBOX}\" --avgTemp \"${AVG_TEMP}\" --seed \"${RND_SEED}\""]
