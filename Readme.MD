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
                 {"client_id": "<your-user-id>", "roles": "user,admin", "usernames": "<your-username>"}
             ]
         }
     }
     ```

## Running the project

1. Run the main script: `python main.py`
   
## Customization

1. Define a class that inherits `src.client.MPPClient`:
   - ```python
     class MyCustomBot(MPPClient):
         def __init__(self, token: str, name: str, color: str, channel: str, host: str = "mppclone.com", port: int = 443, instance_name: str = "mpp_bot", prefix: str = "!"):
             super().__init__(token, name, color, channel, host, port, instance_name, prefix)
     ```
   - Add method overwrites to your new class as needed
     ```python
     ...
     async def handle_a_message(self, message: MPPMessage):
         """MESSAGE"""
         pass
     ...
     ```
2. Define a class that inherits `enum.Enum`:
   - ```python
     class MyCustomCommands(Enum):
         pass
     ```
   - Add commands to your new enum as needed
     ```python
     ...
     ECHO = (
         "Echos a message back to the user",
         None,
         [{"name": "message", "type": str, "required": True, "trailing": True}],
         [
             {"name": "uppercase", "type": bool, "character": "u", "mutually_exclusive_to": ["lowercase"]},
             {"name": "lowercase", "type": bool, "character": "l", "mutually_exclusive_to": ["uppercase"]}
         ]
     )
     ...
     ```
3. Edit `config/customization.py`:
   - In the `bot` property:
     - Import your custom bot class
     - Change the line `BOT_CLASS = MPPClient` to be assigned to your custom bot class 
   - In the `commands` property:
     - Import your custom commands enum class
     - Change the line `COMMANDS = Commands` to be assigned to your custom commands enum class
