#!/usr/bin/env python3

import singer
import csv
import sys

from tap_csv import utils


REQUIRED_CONFIG_KEYS = ['files']
STATE = {}
CONFIG = {}

logger = singer.get_logger()

def write_schema_from_header(entity, header):
    schema =    {
                    "type": "object",
                    "properties": {}
                }
    header_map = []
    for column in header:
        schema["properties"][column] = {"type": "string" } #TODO: intelligent type detection
        header_map.append(column)

    singer.write_schema(entity, schema, []) #no key/required properties

    return header_map


def sync_file(fileInfo):
    logger.info("Syncing entity '" + fileInfo["entity"] + "' from file: '" + fileInfo["file"] + "'")

    with open(fileInfo["file"], "r") as f:
        needsHeader = True
        reader = csv.reader(f)
        for row in reader:
            if(needsHeader):
                header_map = write_schema_from_header(fileInfo["entity"], row)
                needsHeader = False
            else:
                record = {}
                for index, column in enumerate(row):
                    record[header_map[index]] = column
                singer.write_record(fileInfo["entity"], record)

    singer.write_state(STATE) #moot instruction, state always empty


def do_sync():
    logger.info("Starting sync")
    for fileInfo in CONFIG['files']:
        sync_file(fileInfo)
    logger.info("Sync completed")


def main():
    config, state = utils.parse_args(REQUIRED_CONFIG_KEYS)
    CONFIG.update(config)
    STATE.update(state)
    do_sync()


if __name__ == '__main__':
    main()
