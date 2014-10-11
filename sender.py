import time
import zmq
import aiozmq
import asyncio
import logging


class _SenderProtocol(aiozmq.ZmqProtocol):
    def __init__(self, sender):
        self.sender = sender

    def msg_received(self, data):
        self.sender.logger.info("Sender receive %r" % data)


class Sender():
    def __init__(self):
        self.sender = ''
        self.loop = asyncio.get_event_loop()
        self.logger = logging.getLogger(self.__class__.__name__)

    @asyncio.coroutine
    def start(self):
        self.logger.info("Creating Sender REQ...")
        self.sender, _ = yield from aiozmq.create_zmq_connection(
            lambda: _SenderProtocol(self), zmq.REQ)
        self.sender.setsockopt(zmq.IDENTITY, b"SENDER")
        sender_connect = yield from self.sender.connect("ipc://@/temp/front_router")
        self.logger.info("Sender connect to %s" % sender_connect)
        time.sleep(1)

        send_message = [b'echo', b'req', b'hello']
        self.sender.write(send_message)
        self.logger.info("Sender sent message %r" % send_message)

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
    Sender().serve_forever()


if __name__ == '__main__':
    main()