#!/usr/bin/env python3

import argparse
import base64
import json
import logging
import sys

from machina.core.api import BaseAPI

#-------------------------------------------------------------------------------
# CLI Functions
def submit(args):
    api = BaseAPI(rabbitmq_host=args.rabbitmq_host,
                  rabbitmq_port=int(args.rabbitmq_port),
                  rabbitmq_user=args.rabbitmq_user,
                  rabbitmq_password=args.rabbitmq_password,
                  rabbitmq_heartbeat=args.rabbitmq_heartbeat)
    channel = api.connection.channel()

    def submit_job(data, channel):
        channel.basic_publish(exchange='',
                              routing_key='Identifier',
                              body=data)
        channel.close()

    num_submission = len(args.submissions)
    for idx, s in enumerate(args.submissions):
        with open(s, 'rb') as f:
            data_encoded = base64.b64encode(f.read()).decode()
            data = {'data': data_encoded}
            data = json.dumps(data)
            submit_job(data, channel)
            logger.info("Submitted {}/{}".format(idx+1, num_submission))
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    #-------------------------------------------------------------------------------
    # Base parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true')
    subparser = parser.add_subparsers()

    #-------------------------------------------------------------------------------
    # submit
    submit_parser = subparser.add_parser('submit', help='submit a file')
    submit_parser.add_argument('submissions', nargs='+',
                    help='a list of APK files or package names to submit')
    submit_parser.add_argument('--rabbitmq-host', help='rabbitmq host', default='127.0.0.1')
    submit_parser.add_argument('--rabbitmq-port', help='rabbitmq port', default='5672')
    submit_parser.add_argument('--rabbitmq-user', help='rabbitmq user', default='rabbitmq')
    submit_parser.add_argument('--rabbitmq-password', help='rabbitmq password', default='rabbitmq')
    submit_parser.add_argument('--rabbitmq-heartbeat', help='rabbitmq heartbeat time', default='600')
    submit_parser.set_defaults(func=submit)
    #-------------------------------------------------------------------------------

    args = parser.parse_args()

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, format='[*] %(message)s')
    logger = logging.getLogger(__name__)

    #---------------------------------------
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
    #---------------------------------------
    sys.exit()
