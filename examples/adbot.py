"""
Crowbar is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, 
either version 3 of the License, or (at your option) any later version.

Crowbar is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this code. 
If not, see <https://www.gnu.org/licenses/>. 
"""

"""
Simple advertising bot
"""

import time

from threading import Thread

from crowbar.api import OmegleClient
from crowbar.exceptions import *

print("Initializing client")
client = OmegleClient()

message = "FREE VBUCKS --> kekma[.]net"

def handler():

    while 1:

        print("\nOpening new chat")
        client.connect()

        print("Sending message")
        client.send_message(
            message
        )

        time.sleep(1)

        print("Disconnecting...")
        client.disconnect()

Thread(
    target=handler, 
    daemon=False
).start()