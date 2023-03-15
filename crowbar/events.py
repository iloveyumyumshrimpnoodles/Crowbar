"""
Crowbar is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, 
either version 3 of the License, or (at your option) any later version.

Crowbar is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this code. 
If not, see <https://www.gnu.org/licenses/>. 
"""

class Event:
    SEARCHING = 0
    CONNECTED = 1
    GOTMESSAGE = 2
    STRANGERDISCONNECTED = 3
    TYPING = 4
    SLEEP = 5
    COMMONLIKES = 6
    SERVERMSG = 7
    ERROR = 8
    CONNECTIONDIED = 9
    ANTINUDEBANNED = 10