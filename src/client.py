import asyncio, websockets, json, time, requests, os
from typing import List, Optional, Dict
from src.crud import DatabaseManager
from src.lib import MPPMessage, Logger, Participant, CommandMessage, Debug
from src.utils import sqliteutils, regex
from src.lib.exceptions import *
from config import Config

config = Config()


class MPPClient:
    def __init__(self, token: str, name: str, color: str, channel: str, instance_name: str, prefix: str, debug: str, host: str = "mppclone.com", port: int = 443):
        self.token = token
        self.name = name
        self.color = color
        self.channel = channel
        self.instance = instance_name
        self.prefix = prefix
        self.debug = Debug.from_string(debug)
        self.host = host
        self.port = port

        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.db: Optional[DatabaseManager] = None
        self.inbound_queue = asyncio.Queue()
        self.outbound_queue = asyncio.Queue()
        self.logger = Logger(self.__class__.__name__, self.debug)

        self.participants: Dict[str, Participant] = {}
        self.is_running = True
        self.retry_count = 0

        self._client_tick_hz = 5
        self._delta_time = 1 / self.tps

    def __enter__(self):
        self.db = DatabaseManager(self.instance, self.debug)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.log(Debug.ERROR, f"Uncaught exception occurred: {exc_type}, {exc_val}")

        self.db.close()

        return False

    async def run(self):
        while self.is_running:
            try:
                await self.connect()
                pull_task = asyncio.create_task(self.pull_task())
                push_task = asyncio.create_task(self.push_task())
                connection_task = asyncio.create_task(self.handle_connection())
                server_handler_task = asyncio.create_task(self.handle_message())
                simulation_task = asyncio.create_task(self.simulation_loop())
                await asyncio.gather(push_task, pull_task, connection_task, server_handler_task, simulation_task)
            except websockets.ConnectionClosedError as e:
                delay = max(self.retry_count ** 2, config.max_retry_delay)
                self.logger.log(Debug.CONNECTION, f"WebSocket connection closed: code={e.code}, error={e}")
                self.logger.log(Debug.CONNECTION, f"Attempting to reconnect in {delay} seconds... (Attempt {self.retry_count})")
                await asyncio.sleep(delay)
                self.retry_count += 1
            except BotTermination as e:
                self.logger.log(Debug.ERROR, e.error)
                self.is_running = False
            finally:
                await self.disconnect()

    async def simulation_loop(self):
        while True:
            start_time = asyncio.get_running_loop().time()

            # Stuff

            elapsed_time = asyncio.get_running_loop().time() - start_time
            await asyncio.sleep(max(0.0, 1 / self.tps - elapsed_time))
            self.dt = max(1 / self.tps, elapsed_time)

    async def connect(self):
        self.websocket = await websockets.connect(f"wss://{self.host}:{self.port}")
        self.logger.log(Debug.CONNECTION, "Authenticating with token...")
        request = [MPPMessage(MPPMessage.ServerBound.CONNECT, token=self.token)]
        await self.send(request)
        self.logger.log(Debug.CONNECTION, f"Setting user '{self.name}' and joining channel '{self.channel}'...")
        request = [MPPMessage(MPPMessage.ServerBound.USERSET, set={"name": self.name, "color": self.color}), MPPMessage(MPPMessage.ServerBound.SETCHANNEL, _id=self.channel)]
        await self.send(request)
        self.logger.log(Debug.CONNECTION, "Connected to MPP!")
        self.retry_count = 0

    async def disconnect(self):
        if not self.websocket.closed:
            request = [MPPMessage(MPPMessage.ServerBound.DISCONNECT)]
            await self.send(request)
            await self.websocket.close()
        self.logger.log(Debug.CONNECTION, "Disconnected from MPP!")

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
                self.logger.log(Debug.INBOUND, f"Received ({message.type}) message: {str(message)}")

    async def push_task(self):
        while True:
            messages = await self.outbound_queue.get()
            await self.send(messages)
            for message in messages:
                self.logger.log(Debug.OUTBOUND, f"Sent ({message.type}) message: {str(message)}")

    async def handle_connection(self):
        while True:
            request = [MPPMessage(MPPMessage.ServerBound.PING, e=self.get_time())]
            await self.outbound_queue.put(request)
            await asyncio.sleep(20)

    async def handle_message(self):
        while True:
            messages: List[MPPMessage] = await self.inbound_queue.get()
            for message in messages:
                handler = getattr(self, f"handle_{message.type.m}_message")
                await handler(message)
                    
    async def handle_a_message(self, message: MPPMessage):
        """MESSAGE"""
        sender = self.participants.get(message.sender)
        msg = message.payload["a"].strip()
        if msg.startswith(self.prefix) and len(msg) > 1:
            try:
                command = CommandMessage.deserialize(msg)
                await self.handle_command(command, message, sender)
            except (ArgumentValueError, OptionValueError, ArgumentMissingError, OptionMutualExclusivityError) as e:
                response = [MPPMessage(MPPMessage.ServerBound.MESSAGE, message=e.error, reply_to=message.payload["id"])]
                await self.outbound_queue.put(response)
    
    async def handle_dm_message(self, message: MPPMessage):
        """DIRECTMESSAGE"""
        pass

    async def handle_b_message(self, message: MPPMessage):
        """VERIFY"""
        pass

    async def handle_bye_message(self, message: MPPMessage):
        """DISCONNECT"""
        participant = self.participants[message.sender]
        await self.handle_participant(participant)

    async def handle_c_message(self, message: MPPMessage):
        """CHATHISTORY"""
        pass

    async def handle_ch_message(self, message: MPPMessage):
        """CHANNELINFO"""
        for participant_info in message.payload.get("ppl"):
            participant = Participant.deserialize(participant_info)
            self.participants[participant.client_id] = participant
            await self.handle_participant(participant)

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
        participant = Participant.deserialize(message.payload)
        self.participants[participant.client_id] = participant
        await self.handle_participant(participant)

    async def handle_t_message(self, message: MPPMessage):
        """PONG"""
        pass

    async def handle_unknown_message(self, message: MPPMessage):
        """UNKNOWN"""
        pass

    async def handle_participant(self, participant: Participant):
        now = sqliteutils.datetime_to_string()
        if not self.db.user_exists(participant.client_id):
            role = "bot" if participant.tag is not None and participant.tag.text == "BOT" else "user"
            values = {
                "client_id": participant.client_id,
                "roles": role,
                "usernames": participant.name,
                "added_at": now,
                "last_seen": now
            }
            self.db.add_user(values)
        else:
            aliases = self.db.get_user_column(participant.client_id, "usernames")
            usernames = aliases + ("\0{}".format(participant.name) if participant.name not in aliases.split("\0") else "")
            values = {
                "last_seen": now
            }
            if usernames != aliases:
                values["usernames"] = usernames
            self.db.update_user(participant.client_id, values)

    async def handle_command(self, command: CommandMessage, message: MPPMessage, sender: Participant):
        handler = getattr(self, f"handle_{command.type.name}_command")
        try:
            await self.handle_command_authorization(command, message, sender)
            await handler(command, message, sender)
        except CommandAuthorizationError as e:
            response = [MPPMessage(MPPMessage.ServerBound.MESSAGE, message=e.error, reply_to=message.payload["id"])]
            await self.outbound_queue.put(response)

    async def handle_command_authorization(self, command: CommandMessage, message: MPPMessage, sender: Participant):
        user_roles = self.db.get_user_roles(sender.client_id)
        command_roles = command.type.roles
        if command_roles is None or all(role in user_roles for role in command_roles):
            return
        elif command_roles is not None and not all(role in user_roles for role in command_roles):
            command_role_names = [role.name for role in command.type.roles]
            raise CommandAuthorizationError(command.type.name, command_role_names)

    async def handle_help_command(self, command: CommandMessage, message: MPPMessage, sender: Participant):
        """HELP"""
        response = []
        for member in command.type.get_commands():
            options = ["[{}{}]".format("-" + opt["character"], " " + opt["name"] if opt["type"] is not bool else "") for opt in member.opts]
            arguments = ["{}".format("<" + arg["name"] + ">" if arg["required"] else "[" + arg["name"] + "]") for arg in member.args]
            usage = "{}{} {} {}".format(self.prefix, member.name, " ".join(options), " ".join(arguments)).rstrip()
            msg = f"`{usage}`: {member.description}"
            response.append(MPPMessage(MPPMessage.ServerBound.MESSAGE, message=msg))
        await self.outbound_queue.put(response)

    async def handle_echo_command(self, command: CommandMessage, message: MPPMessage, sender: Participant):
        """ECHO"""
        response = []
        msg = command.args['message']
        if command.opts["uppercase"]:
            msg = msg.upper()
        elif command.opts["lowercase"]:
            msg = msg.lower()
        response.append(MPPMessage(MPPMessage.ServerBound.MESSAGE, message=msg))
        await self.outbound_queue.put(response)

    async def handle_gaming_command(self, command: CommandMessage, message: MPPMessage, sender: Participant):
        """GAMING"""
        response = []
        msgs = []
        try:
            if command.opts["list"]:
                downloaded_midis = self.db.get_midi_filenames()
                midi_list_string = ", ".join(['`{}`'.format(midi) for midi in downloaded_midis])
                msgs.append(f"MIDIs: {midi_list_string}")
            else:
                query = command.args['midi']
                if regex.is_valid_url(query):
                    filename = command.opts["output"] if "output" in command.opts else query.split("/")[-1]
                    self.download_midi(query, filename=filename)
                    downloaded_midis = self.db.get_midi_filenames()
                    values = {
                        "filename": filename,
                        "uploader_id": self.db.get_user_column(sender.client_id, "id")
                    }
                    if filename in downloaded_midis:
                        values.update({"added_at": sqliteutils.datetime_to_string()})
                        self.db.update_midi(filename, values)
                    else:
                        self.db.add_midi(values)
                    msgs.append(f"Successfully downloaded MIDI: `{filename}`")
                    # Add gaming task to simulation loop scheduler
                else:
                    results = self.search_midis(query)
                    if results is not None:
                        if len(results) > 1:
                            found_midis_string = ", ".join(['`{}`'.format(midi) for midi in results])
                            msgs.append(f"Multiple results found: {found_midis_string}")
                            msgs.append(f"Please select one with `!gaming <file_name.mid>`")
                        else:
                            msgs.append(f"Result found: `{results[0]}`")
                            # Add gaming task to simulation loop scheduler
                    else:
                        msgs.append("No results found. Do `!gaming -l` to browse downloaded MIDIs")
            response.extend([MPPMessage(MPPMessage.ServerBound.MESSAGE, message=msg) for msg in msgs])
        except HTTPError as e:
            response.append(MPPMessage(MPPMessage.ServerBound.MESSAGE, message=e.error, reply_to=message.payload["id"]))
        await self.outbound_queue.put(response)

    async def handle_unknown_command(self, command: CommandMessage, message: MPPMessage, sender: Participant):
        """UNKNOWN"""
        pass

    def download_midi(self, url: str, filename: str = None):
        filename = url.split("/")[-1] if filename is None else filename
        response = requests.get(url)
        if response.status_code == 200:
            destination_path = os.path.abspath("instance/midis/" + filename)
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            with open(destination_path, 'wb') as file:
                file.write(response.content)
            self.logger.log(Debug.FILESYSTEM, f"Downloaded new MIDI file: '{destination_path}'")
        else:
            self.logger.log(Debug.ERROR, f"Failed to download new MIDI file: '{filename}'")
            raise HTTPError(url, response.status_code)

    def search_midis(self, query: str) -> Optional[list[str]]:
        searchable_files = self.db.get_midi_filenames()
        results = regex.search_engine(query, searchable_files)
        return [os.path.basename(result) for result in results] if results is not None else None

    @staticmethod
    def get_time():
        return round(time.time() * 1000)

    @property
    def tps(self) -> float:
        return self._client_tick_hz

    @tps.setter
    def tps(self, client_tick_hz: float):
        self._client_tick_hz = client_tick_hz

    @property
    def dt(self) -> float:
        return self._delta_time

    @dt.setter
    def dt(self, delta_time: float):
        self._delta_time = delta_time
