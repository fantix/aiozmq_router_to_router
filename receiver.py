__author__ = 'kevin'
import aiozmq
import logging
import zmq
import asyncio


class _GatewayProtocol(aiozmq.ZmqProtocol):
    def __init__(self, receiver):
        self.receiver = receiver

    def msg_received(self, data):
        self.receiver.logger.info("Gateway Router receive %r " % data)


class Receiver():
    def __init__(self):
        self.gateway_router = ''
        self.broker_router = ''
        self.loop = asyncio.get_event_loop()
        self.logger = logging.getLogger(self.__class__.__name__)

    @asyncio.coroutine
    def start(self):
        self.logger.info("Creating gateway Router...")
        self.gateway_router, _ = yield from aiozmq.create_zmq_connection(
            lambda: _GatewayProtocol(self), zmq.ROUTER)
        #gateway_connect = yield from self.gateway_router.bind("ipc://@/temp/gateway")
        self.gateway_router.setsockopt(zmq.IDENTITY, b"GATEWAY")
        gateway_connect = yield from self.gateway_router.bind("tcp://*:8888")
        self.logger.info("Gateway bind to %s " % gateway_connect)
        

    def serve_forever(self):
        asyncio.async(self.start())
        self.loop.run_forever()


def main():
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(process)-5d] %(asctime)-15s [%(name)s] '
               '%(levelname)s: %(message)s')
    logging.getLogger('asyncio').setLevel(logging.INFO)
    Receiver().serve_forever()


if __name__ == '__main__':
    main()
