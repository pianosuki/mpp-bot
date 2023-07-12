import asyncio, websockets, traceback, json, time
from typing import List, TypeVar
from src.message import MPPMessage

CLIENT_TICK_HZ = 5


class MPPClient:
    def __init__(self, token: str, name: str, color: str, channel: str, host: str = "mppclone.com", port: int = 443):
        self.token = token
        self.name = name
        self.color = color
        self.channel = channel
        self.host = host
        self.port = port

        self.websocket = None
        self.inbound_queue = asyncio.Queue()
        self.outbound_queue = asyncio.Queue()

        self.delta_time = 1 / CLIENT_TICK_HZ  # Time since last simulation loop

    async def run(self):
        try:
            await self.connect()
            pull_task = asyncio.create_task(self.pull_task())
            push_task = asyncio.create_task(self.push_task())
            connection_task = asyncio.create_task(self.handle_connection())
            server_handler_task = asyncio.create_task(self.handle_message())
            await asyncio.gather(push_task, pull_task, connection_task, server_handler_task)
        except Exception as e:
            print(f"ERROR: {e}")
            traceback.print_exc()
        finally:
            await self.disconnect()

    async def simulation_loop(self):
        while True:
            start_time = asyncio.get_running_loop().time()

            # Stuff

            elapsed_time = asyncio.get_running_loop().time() - start_time
            await asyncio.sleep(max(0, 1 / CLIENT_TICK_HZ - elapsed_time))
            self.delta_time = max(1 / CLIENT_TICK_HZ, elapsed_time)

    async def connect(self):
        self.websocket = await websockets.connect(f"wss://{self.host}:{self.port}")
        print("Authenticating with token...")
        request = [MPPMessage(MPPMessage.ServerBound.CONNECT, token=self.token)]
        await self.send(request)
        print(f"Setting up user '{self.name}' and joining channel '{self.channel}'...")
        request = [MPPMessage(MPPMessage.ServerBound.USERSET, set={"name": self.name, "color": self.color}), MPPMessage(MPPMessage.ServerBound.SETCHANNEL, _id=self.channel)]
        await self.send(request)
        print("Connected to MPP!")

    async def disconnect(self):
        request = [MPPMessage(MPPMessage.ServerBound.DISCONNECT)]
        await self.send(request)
        await self.websocket.close()
        print("Disconnected from MPP!")

    async def send(self, messages: List[MPPMessage]):
        await self.websocket.send(json.dumps([message.serialize() for message in messages]))

    async def recv(self) -> List[MPPMessage]:
        data = await self.websocket.recv()
        messages = MPPMessage.deserialize(data)
        return messages

    async def pull_task(self):
        while True:
            messages = await self.recv()
            await self.inbound_queue.put(messages)
            for message in messages:
                print(f"Received ({message.type}) message: {str(message)}")

    async def push_task(self):
        while True:
            messages = await self.outbound_queue.get()
            await self.send(messages)
            for message in messages:
                print(f"Sent ({message.type}) message: {str(message)}")

    async def handle_connection(self):
        while True:
            request = [MPPMessage(MPPMessage.ServerBound.PING, e=self.get_time())]
            await self.outbound_queue.put(request)
            await asyncio.sleep(20)

    async def handle_message(self):
        while True:
            messages = await self.inbound_queue.get()
            for message in messages:
                handler = getattr(self, f"handle_{message.type.m}_message")
                await handler(message)
                    
    async def handle_a_message(self, message: MPPMessage):
        """MESSAGE"""
        pass
    
    async def handle_dm_message(self, message: MPPMessage):
        """DIRECTMESSAGE"""
        pass

    async def handle_b_message(self, message: MPPMessage):
        """VERIFY"""
        pass

    async def handle_bye_message(self, message: MPPMessage):
        """DISCONNECT"""
        pass

    async def handle_c_message(self, message: MPPMessage):
        """CHATHISTORY"""
        pass

    async def handle_ch_message(self, message: MPPMessage):
        """CHANNELINFO"""
        pass

    async def handle_custom_message(self, message: MPPMessage):
        """CUSTOM"""
        pass

    async def handle_hi_message(self, message: MPPMessage):
        """CONNECT"""
        pass

    async def handle_ls_message(self, message: MPPMessage):
        """ROOMLIST"""
        pass

    async def handle_m_message(self, message: MPPMessage):
        """MOUSE"""
        pass

    async def handle_n_message(self, message: MPPMessage):
        """NOTES"""
        pass

    async def handle_notification_message(self, message: MPPMessage):
        """NOTIFICATION"""
        pass

    async def handle_nq_message(self, message: MPPMessage):
        """NOTEQUOTA"""
        pass

    async def handle_p_message(self, message: MPPMessage):
        """PARTICIPANTADDED"""
        pass

    async def handle_t_message(self, message: MPPMessage):
        """PONG"""
        pass

    async def handle_unknown_message(self, message: MPPMessage):
        """UNKNOWN"""
        pass

    @staticmethod
    def get_time():
        return round(time.time() * 1000)


CustomBotType = TypeVar("CustomBotType", bound=MPPClient)


class MyCustomBot(MPPClient):
    def __init__(self, token: str, name: str, color: str, channel: str, host: str = "mppclone.com", port: int = 443):
        super().__init__(token, name, color, channel, host, port)