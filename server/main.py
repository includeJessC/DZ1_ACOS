#!/usr/bin/env python3
import io
import json
import os
import pickle
import random
import socket
import string
import sys
import timeit

import dicttoxml
import fastavro
import msgpack
import xmltodict
import yaml


def generate_random_string(length):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for _ in range(length))
    print("Random string of length", length, "is:", rand_string)
    return rand_string


def random_data():
    return {
        "string": generate_random_string(10),
        "integer": random.randint(0, 100),
        "float": random.uniform(0, 1),
        "dict": {'lol': 1, 'get': 2},
        "array": [random.random() for _ in range(10)]
    }


def native_serialization(data):
    return pickle.dumps(data)


def native_deserialization(data):
    return pickle.loads(data)


def xml_serialization(data):
    return dicttoxml.dicttoxml(data)


def xml_deserialization(data):
    return xmltodict.parse(data)


def json_serialization(data):
    return json.dumps(data)


def json_deserialization(data):
    return json.loads(data)


def apache_serialization(data):
    wb = io.BytesIO()
    fastavro.schemaless_writer(wb, {
        "name": "exmpl",
        "type": 'record',
        "fields": [
            {"name": "string", "type": "string"},
            {"name": "integer", "type": "int"},
            {"name": "float", "type": "float"},
            {"name": "dict", "type": {"type": "map", "values": "int"}},
            {"name": "array", "type": {"type": "array", "items": "int"}},
        ]
    }, data)
    return wb.getvalue()


def apache_deserialization(data):
    wb = io.BytesIO()
    wb.write(data)
    wb.seek(0)
    return fastavro.schemaless_reader(wb, {
        "name": "exmpl",
        "type": 'record',
        "fields": [
            {"name": "string", "type": "string"},
            {"name": "integer", "type": "int"},
            {"name": "float", "type": "float"},
            {"name": "dict", "type": {"type": "map", "values": "int"}},
            {"name": "array", "type": {"type": "array", "items": "int"}},
        ]
    })


def yaml_serialization(data):
    return yaml.dump(data)


def yaml_deserialization(data):
    return yaml.load(data, yaml.FullLoader)


def msgpack_serialization(data):
    return msgpack.packb(data)


def msgpack_deserialization(data):
    return msgpack.unpackb(data)


def get_time(func, data):
    timer = timeit.Timer(lambda: func(data))
    return timer.timeit(number=1000)


BUFFER_SIZE = 1024

SERAIL = {
    "NATIVE": native_serialization,
    "XML": xml_serialization,
    "JSON": json_serialization,
    "APACHE": apache_serialization,
    "YAML": yaml_serialization,
    "MSGPACK": msgpack_serialization,
}

DESERAIL = {
    "NATIVE": native_deserialization,
    "XML": xml_deserialization,
    "JSON": json_deserialization,
    "APACHE": apache_deserialization,
    "YAML": yaml_deserialization,
    "MSGPACK": msgpack_deserialization,
}

if __name__ == "__main__":
    host = os.environ['HOST']
    port = int(os.environ['PORT'])
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', port))
        test_data = random_data()
        while True:
            bytesAddressPair = s.recvfrom(BUFFER_SIZE)
            data, address = bytesAddressPair
            serialized = SERAIL[host](test_data)
            result = {
                "format": host,
                "s_time": get_time(SERAIL[host], test_data),
                "d_time": get_time(DESERAIL[host], serialized),
                "serial_size": sys.getsizeof(serialized),
            }
            s.sendto(str.encode(json.dumps(result)), address)
