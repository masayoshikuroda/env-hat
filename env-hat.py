#!/usr/bin/env python3
# coding=utf-8
import sys
import struct
from datetime import datetime
from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_DGRAM
from socket import SOL_SOCKET, SO_BROADCAST
import asyncio
from bleak import BleakClient

GATT_CHARACTERISTIC_UUID_TEMP = '00002a6e-0000-1000-8000-00805f9b34fb'
GATT_CHARACTERISTIC_UUID_HUMI = '00002a6f-0000-1000-8000-00805f9b34fb'
GATT_CHARACTERISTIC_UUID_PRES = '00002a6d-0000-1000-8000-00805f9b34fb'

argparser =  ArgumentParser(description='Connect Env hat via bluetooth and broadcast measured values via UDP.')
argparser.add_argument('-d', '--dest', type=str,   dest='dest', default='255.255.255.255', help='destination mac address to broadcast')
argparser.add_argument('-p', '--port', type=int,   dest='port', default=7001,              help='destination port number to broadcast')
argparser.add_argument('-s', '--sec',  type=float, dest='sec',  default=1.0,               help='measurement interval') 
argparser.add_argument('-v', '--verbose',          dest='verbose', action='store_true',    help='dump result to stdout')
argparser.add_argument('id',           type=str,                                           help='device mac addres to connect')
args = argparser.parse_args()

id = args.id
dest = args.dest
port = args.port
sec = args.sec
verbose = args.verbose

s = socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

def on_value(temp, humi, pres):
    dt = datetime.now().strftime('%Y–%m–%d %H:%M:%S')
    if verbose:
       print("{0} {1:.1f}[degC] {2:.1f}[%] {3:.1f}[Pa]".format(dt, temp, humi, pres))
    msg = '{"temperature":' + str(temp) + ',"humidity":' + str(humi) + ',"pressure":' + str(pres) + '}'
    s.sendto(msg.encode(), (dest, port))   

async def run(loop):
    client = BleakClient(id)
    await client.connect()
    print("connected!")

    while True:
        temp = struct.unpack('f', await client.read_gatt_char(GATT_CHARACTERISTIC_UUID_TEMP))[0]
        humi = struct.unpack('f', await client.read_gatt_char(GATT_CHARACTERISTIC_UUID_HUMI))[0]
        pres = struct.unpack('f', await client.read_gatt_char(GATT_CHARACTERISTIC_UUID_PRES))[0]
        on_value(temp, humi, pres)
        await asyncio.sleep(sec, loop=loop)

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
