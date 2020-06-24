from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor, threads, defer

from protocol import MyProtocol
from DBmanager import Database


PORT = 8100

HEADER_SIZE = 4


class Echo(Protocol):
    def __init__(self, factory):
        super().__init__()
        # each connection knows the factory
        self.factory = factory

    def connectionMade(self):
        # init data buffer
        self.dataBuffer = bytes()

        print("new connection!")

    def connectionLost(self, reason):
        print("connection lost!")

    def dataReceived(self, data):
        """combine data to get packet"""
        print("got", data)
        self.dataBuffer += data

        # if buffer size less than packet length
        if len(self.dataBuffer) < HEADER_SIZE:
            return

        # read length of packet
        length_pck = int.from_bytes(self.dataBuffer[:HEADER_SIZE], byteorder='little')

        # if buffer size < header + packet length
        if len(self.dataBuffer) < HEADER_SIZE + length_pck:
            return

        # 截取封包
        pck = self.dataBuffer[HEADER_SIZE:HEADER_SIZE + length_pck]
        print('got packet')

        # 把封包交给处理函数
        self.pck_received(pck)

        # 删除已经读取的字节
        self.dataBuffer = self.dataBuffer[HEADER_SIZE + length_pck:]

        # print("got", data)
        # self.transport.write(data)

    def pck_received(self, pck):

        # get packet type and message object
        p = MyProtocol(pck)
        pck_type = p.get_str()
        print("got pck type:", pck_type)

        message_obj = p.get_obj()
        print("message obj: ", message_obj)

        # send message back
        # self.send(pck_type, message_obj)

        # responses based on different types
        if pck_type == 'register':

            # get ac and psw
            account = message_obj[0]
            password = message_obj[1]

            # register ok?
            is_ok = self.factory.db.register(account, password)
            if is_ok:
                print('success!')
                self.send('register_ok')
            else:
                print("account exists!")
                self.send('account_exists')

    # actions
    def send(self, protocol_name, content_obj='na'):
        """send packet to server"""

        # make packet
        p = MyProtocol()
        p.add_str(protocol_name)
        p.add_obj(content_obj)
        data = p.get_pck_has_head()

        # send packet
        self.transport.write(data)
        # d = threads.deferToThread(self.transport.getHandle().sendall, data)
        # d.addCallback(self.say_sent)

    def say_sent(self, na):
        print('sent')

class EchoFactory(Factory):
    def __init__(self):
        self.users = {}
        self.db = Database()

    def buildProtocol(self, addr):
        return Echo(self)


reactor.listenTCP(PORT, EchoFactory())
reactor.run()