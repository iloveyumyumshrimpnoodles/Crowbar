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
Example of a simple Omegle bot 
that mirrors everything the user sends
"""

from crowbar.api import OmegleClient
from crowbar.events import Event

client = OmegleClient()

print("Connecting")
client.connect()

print("Waiting for events...\n")
while client.isconnected:
    event, msg = client.get_event(2)

    if event == Event.GOTMESSAGE and msg != None:
        print(f"Stranger said '{msg}'")
        client.send_message(msg)
        client.disconnect()

    if event == Event.CONNECTIONDIED or event == Event.STRANGERDISCONNECTED:
        print("Disconnecting...")
        break