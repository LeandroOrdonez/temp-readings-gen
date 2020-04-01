#!/usr/bin/env python3

import os
from time import sleep
from os.path import basename
import argparse
import re
from kafka_observer import KafkaObserver
from rx import create, of
import json
import signal
import time
from random import randint
import random as rnd
import geohash as gh
from math import sin

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.kill_now = True

parser = argparse.ArgumentParser(description='Random temperature data generator.', prog='temp-gen', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--bbox', default='51.32288838086245,4.091720581054688,51.1509246836981,4.752960205078125', help='N,W,S,E coordinates of the bounding box inside which observations are going to be generated')
parser.add_argument('--avgTemp', default='19.0', help='Reference temperature value. generated values would oscilate around this value.')
parser.add_argument('--seed', default='0.0', help='Random seed (for reproducibility)')
args = vars(parser.parse_args())

N,W,S,E = [float(coord) for coord in args['bbox'].split(',')]
AVG_TEMP = float(args['avgTemp'])
RND_SEED = float(args['seed'])

rnd.seed(RND_SEED)

def gen_temperature_readings(observer, scheduler):
    killer = GracefulKiller()
    while not killer.kill_now:
        time.sleep(randint(1,5))
        ts = int(time.time()*1000)
        lat = rnd.uniform(S,N)
        lon = rnd.uniform(W,E)
        geohash = gh.encode(lat,lon)
        sensor_id = f's{str(randint(0,20)).zfill(6)}'
        value = AVG_TEMP + (4 * sin(time.time()/14400.)) + rnd.uniform(0, 1)
        unit = 'c'
        temp_obj = {
            "timestamp": ts,
            "geohash": geohash,
            "sensorId": sensor_id,
            "temp_val": value,
            "temp_unit": unit
        }
        print(f"generate temp reading {temp_obj}...")
        observer.on_next(temp_obj)

    print("End of the program...")
    observer.on_completed()


if __name__ == '__main__':
    KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
    KAFKA_BROKER = os.getenv("KAFKA_BROKER").split(",")

    kafka_producer = KafkaObserver(KAFKA_BROKER, KAFKA_TOPIC)

    source = create(gen_temperature_readings)
    source.subscribe(kafka_producer)

    input("Press key to quit")
