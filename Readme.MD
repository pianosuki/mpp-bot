# Multiplayer Piano Bot Python Library

https://multiplayerpiano.com

## Prerequisites

- Python 3.11

## Installation

1. Clone the repository: `git clone https://github.com/pianosuki/mpp-bot.git`
2. Navigate to the project directory: `cd mpp-bot`
3. Create a virtual environment: `python3 -m venv venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Install the dependencies: `pip install -r requirements.txt`

## Configuration

1. Request a bot token from here: [MPP Bot Guide](https://docs.google.com/document/d/1OrxwdLD1l1TE8iau6ToETVmnLuLXyGBhA0VfAY1Lf14)
2. Create the file `.env` and set the following variables:
   - `TOKEN=<your-mpp-bot-token>`
   - `NAME=<your-bot-name>`
   - `COLOR=<#hex-color-code>`
   - `CHANNEL=<channel-name-to-join>`
   - `INSTANCE=<database-instance-name>`
   - `PREFIX=<command-prefix>`
3. Edit the file `config/schema.json` and change the `"defaults"` object as needed:
   - ```json
     {
         "defaults": {
             "users": [
                 {"client_id": "<your-user-id>", "roles": "user,admin,whitelist,owner", "usernames": "<your-username>"}
             ]
         }
     }
     ```

## Running the project

1. Run the main script: `python main.py`
   
## Customization

1. **Roles** - Define a class that inherits `enum.Enum`:
   - ```python
     class MyCustomRoles(Enum):
         pass
     ```
   - Add roles to your new enum as needed:
     ```python
     ...
     USER = "A normal user"
     ...
     ```
2. **Commands** - Define a class that inherits `enum.Enum`:
   - ```python
     class MyCustomCommands(Enum):
         pass
     ```
   - Add commands to your new enum as needed:
     ```python
     ...
     ECHO = (
         "Echos a message back to the user",
         ["user"],
         [{"name": "message", "type": str, "required": True, "trailing": True}],
         [
             {"name": "uppercase", "type": bool, "character": "u", "mutually_exclusive_to": ["lowercase"]},
             {"name": "lowercase", "type": bool, "character": "l", "mutually_exclusive_to": ["uppercase"]}
         ]
     )
     ...
     ```
3. **Bot** - Define a class that inherits `src.client.MPPClient`:
   - ```python
     class MyCustomBot(MPPClient):
         def __init__(self, token: str, name: str, color: str, channel: str, instance_name: str, prefix: str, host: str = "mppclone.com", port: int = 443):
             super().__init__(token, name, color, channel, instance_name, prefix, host, port)
     ```
   - Add method overwrites to your new class as needed: `def handle_"lowercase_name"_message` ([MPP message protocol](https://github.com/LapisHusky/mppclone/blob/main/docs/protocol.md))
     ```python
     ...
     async def handle_a_message(self, message: MPPMessage):
         """MESSAGE"""
         print(message.payload["a"])
     ...
     ```
   - Add methods for each of your commands: `def handle_"lowercase_name"_command`
     ```python
     ...
     async def handle_echo_command(self, command: CommandMessage, message: MPPMessage):
         """ECHO"""
         msg = f"{command.args['message']}"
         if command.opts["uppercase"]:
             msg = msg.upper()
         elif command.opts["lowercase"]:
             msg = msg.lower()
         response = [MPPMessage(MPPMessage.ServerBound.MESSAGE, message=msg)]
         await self.outbound_queue.put(response)
     ...
     ```
4. **Config** - Edit `config/customization.py`:
   - In the `bot` property:
     - Import your custom bot class
     - Change the line `BOT_CLASS = MPPClient` to be assigned to your custom bot class 
   - In the `commands` property:
     - Import your custom commands enum class
     - Change the line `COMMANDS = Commands` to be assigned to your custom commands enum class
   - In the `roles` property:
     - Import your custom roles enum class
     - Change the line `ROLES = Roles` to be assigned to your custom roles enum class

## Contributions

All contributions are welcome and appreciated!
