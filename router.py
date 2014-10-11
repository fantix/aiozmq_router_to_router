import time

__author__ = 'kevin'
import asyncio
import aiozmq
import zmq
import logging


class _FrontProtocol(aiozmq.ZmqProtocol):
    def __init__(self, test_router):
        self.test_router = test_router

    def msg_received(self, data):
        self.test_router.logger.info("Front Router receive %r" % data)
        from_addr = data[0:1]
        message = data[2:]
        send_message = [b"GATEWAY", b""] + from_addr + message
        self.test_router.forward_router.write(send_message)
        self.test_router.logger.info("Forward Router send message %r " % send_message)


class _ForwardProtocol(aiozmq.ZmqProtocol):
    def __init__(self, test_router):
        self.test_router = test_router

    def msg_received(self, data):
        self.test_router.logger.info("Forward Router receive %r " % data)


class TestRouter():
    def __init__(self):
        self.front_router = ''
        self.forward_router = ''
        self.loop = asyncio.get_event_loop()
        self.logger = logging.getLogger(self.__class__.__name__)

    @asyncio.coroutine
    def start(self):
        self.logger.info("Creating Front Router...")
        self.front_router, _ = yield from aiozmq.create_zmq_connection(
            lambda: _FrontProtocol(self), zmq.ROUTER)
        front_endpoint = yield from self.front_router.bind("ipc://@/temp/front_router")
        self.front_router.setsockopt(zmq.IDENTITY, b"FRONT")
        self.logger.info("Front Router bind to %s" % front_endpoint)

        self.logger.info("Creating Forward Router...")
        self.forward_router, _ = yield from aiozmq.create_zmq_connection(
            lambda: _ForwardProtocol(self), zmq.ROUTER)
        self.forward_router.setsockopt(zmq.IDENTITY, b"FORWARD")
        # forward_connect = yield from self.forward_router.connect("ipc://@/temp/gateway")
        forward_connect = yield from self.forward_router.connect("tcp://127.0.0.1:8888")
        time.sleep(1)
        self.logger.info("Forward Router connect to %s" % forward_connect)

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
    TestRouter().serve_forever()


if __name__ == '__main__':
    main()
