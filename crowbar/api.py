"""
Crowbar is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, 
either version 3 of the License, or (at your option) any later version.

Crowbar is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this code. 
If not, see <https://www.gnu.org/licenses/>. 
"""

import requests
from random import uniform, choice
from urllib.parse import quote_plus

from .util import *
from .events import *
from .exceptions import *

class OmegleClient:
    """
    Instance of an Omegle Client

    Args:
        interests list[str]: List of topics/interests
        proxies dict[str, str]: Proxies to use for this client
        lang str: 2 char language code
        verify bool: Verify TLS certificates
        headers dict[str, str or bytes]: Headers to pass to Requests
    
    Returns:
        OmegleClient: Instance of a client
    """

    def __init__(
        self,
        interests: list[str] = [],
        proxies: dict[str, str] = {"http": "", "https": ""},
        lang: str = "en",
        verify: bool = True,
        headers: dict[str, str | bytes] = {
                "accept": (
                    "text/html,"
                    "application/xhtml+xml,"
                    "application/xml;q=0.9,"
                    "image/avif,"
                    "image/webp,"
                    "image/apng,"
                    "*/*;q=0.8,"
                    "application/signed-exchange;v=b3;q=0.9"
                ),

                "accept-encoding": "gzip, deflate",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
                "cache-control": "max-age=0",
                "connection": "keep-alive",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "sec-gpc": "1",
                "dnt": "1",
                "upgrade-insecure-requests": "1",
                "origin": "http://www.omegle.com",
                "referer": "http://www.omegle.com/",
                "user-agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/100.0.4896.79 "
                    "Safari/537.36"
                )
            },
            /
        ) -> None:

        if len(interests) > 0:
            self.interests = quote_plus(str(interests).replace(" ", ""))
            self.interests_raw = interests
        else:
            self.interests = self.interests = None

        self.lang = lang

        self.s = requests.Session()
        self.s.proxies = proxies
        self.s.headers = headers
        self.s.verify = verify

        self.randid = make_randid()
        self.clientid = ""

        self.isbanned = False
        self.isconnected = False

        self.omegle_online = 0
        self.antinudeservers = []
        self.antinudepercent = 0.0
        self.spyQueueTime = 0.0
        self.spyeeQueueTime = 0.0
        self.omegle_timestamp = 0.0
        self.omegle_servers = []

        self.status()
    
    def get_antinude_hash(self) -> str:
        """
        Sends a POST request to an anti-nude server

        Returns:
            str: Some hash digest
        """

        server = choice(self.antinudeservers)

        ret = self.s.post(f"https://{server}/check")
        return ret.text
    
    def status(self) -> None:
        """
        Retrieves the metadata, servers and some information from Omegle

        Raises:
            exceptions.BadApiResponse: Omegle returned a bad response
            exceptions.Banned: Your IP has been banned
        
        Returns:
            Nothing.
        """

        nocache = uniform(0, 1) # random nonce

        ret = self.s.get(
            f"https://omegle.com/status",
            params={
                "nocache": nocache,
                "randid": self.randid
            }
        )

        if ret.status_code != 200:
            raise BadApiResponse(f"Omegle returned bad response code: {ret.status_code}")

        body = ret.json()        
        self.omegle_online = body["count"]
        self.antinudeservers = body["antinudeservers"]
        self.antinudepercent = body["antinudepercent"]
        self.spyQueueTime = body["spyQueueTime"]
        self.spyeeQueueTime = body["spyeeQueueTime"]
        self.omegle_timestamp = body["timestamp"]
        self.omegle_servers = body["servers"]

        # pick a random server
        self.server = choice(
            self.omegle_servers
        )
    
    def connect(
        self, 
        unmonitored: bool = False
        ) -> str:
        """
        Connects and opens a new chat

        Args:
            unmonitored: If True, look for unmonitored chats

        Raises:
            exceptions.AlreadyConnected: You've already opened a connection
            exceptions.BadApiResponse: Omegle returned a bad response
            exceptions.ApiError: Omegle raises an error
        
        Returns:
            str: The client ID
        """

        if self.isconnected:
            raise AlreadyConnected("Please disconnect first before connecting again")
        
        params = {
            "caps": "recaptcha2,t3",
            "firstevents": 0, # 0 since we've already fetched status info
            "spid": "",
            "randid": self.randid,
            "cc": self.get_antinude_hash(),
            "group": "unmon" if unmonitored else "",
            "lang": self.lang
        }

        if self.interests != None:
            params["topics"] = self.interests

        ret = self.s.post(
            f"https://{self.server}.omegle.com/start",
            params=params
        )

        if ret.status_code != 200:
            raise BadApiResponse(f"Omegle returned bad response code: {ret.status_code}")

        body = ret.json()

        status = body["events"][0][0]
        if status == "connected":

            self.isconnected = True
            self.clientid = body["clientID"]

            return self.clientid
        
        raise ApiError(status)
    
    def disconnect(self) -> bool:
        """
        Disconnects from the current chat

        Raises:
            exceptions.NotConnected: No connection/chat has been opened yet
            exceptions.BadApiResponse: Omegle returned a bad response
        
        Returns:
            bool: True if the chat has been disconnected, False if not
        """

        if not self.isconnected:
            raise NotConnected("Please connect first before doing this")

        ret = self.s.post(
            f"https://{self.server}.omegle.com/disconnect",
            data={"id": self.clientid}
        )

        if ret.status_code != 200:
            raise BadApiResponse(f"Omegle returned bad response code: {ret.status_code}")
        
        self.isconnected = not ret.text == "win"
        return self.isconnected
    
    def typing(self) -> bool:
        """
        Sets the status to "typing..."

        Returns:
            bool: True if the status has been set, False if not
        """

        ret = self.s.post(
            f"https://{self.server}.omegle.com/typing",
            data={"id": self.clientid}
        )

        return ret.text == "win"
    
    def stoptyping(self) -> bool:
        """
        Clears the "typing..." status

        Returns:
            bool: True if the status has been cleared, False if not
        """

        ret = self.s.post(
            f"https://{self.server}.omegle.com/stoppedtyping",
            data={"id": self.clientid}
        )

        return ret.text == "win"
    
    def send_message(
        self, 
        msg: str, 
        typing: bool = True
        ) -> bool:
        """
        Sends a message

        Args:
            msg str: Message to send
            typing bool: Send a "typing..." status. Disabling this might result in a ban
        
        Raises:
            exceptions.NotConnected: No connection/chat has been opened yet
            exceptions.BadApiResponse: Omegle returned a bad response
        
        Returns:
            bool: True if the message has been sent, False if not
        """

        if not self.isconnected:
            raise NotConnected("Please connect first before doing this")

        if typing:
            self.typing()

        ret = self.s.post(
            f"https://{self.server}.omegle.com/send",
            data={
                "id": self.clientid,
                "msg": msg
            }
        )

        if typing:
            self.stoptyping()
        
        if ret.status_code != 200:
            raise BadApiResponse(f"Omegle returned bad response code: {ret.status_code}")
        
        return ret.text == "win"
    
    def get_event(
        self,
        timeout: int | float = 25.0
        ) -> tuple[int, str | None]:
        """
        Polls for a new event

        Args:
            timeout int or float: Seconds to wait before raising `requests.exceptions.Timeout`

        Raises:
            requests.exceptions.Timeout: Read time out
            exceptions.NotConnected: No connection/chat has been opened yet
            exceptions.BadApiResponse: Omegle returned a bad response
            exceptions.Banned: Your IP has been banned
        
        Returns:
            tuple[int, str or None]: Event code and message
        """

        if not self.isconnected:
            raise NotConnected("Please connect first before doing this")
        
        ret = self.s.post(
            f"https://{self.server}.omegle.com/events", 
            data={"id": self.clientid},
            timeout=timeout
        )

        if ret.status_code != 200:
            raise BadApiResponse(f"Omegle returned bad response code: {ret.status_code}")
        
        body = ret.json()
        if not body:
            self.isconnected = False

            return Event.CONNECTIONDIED, None

        body = body[0]
        match body[0].lower():
            case "waiting": return Event.SEARCHING, None
            case "connected": return Event.CONNECTED, None
            case "gotmessage": return Event.GOTMESSAGE, body[1]
            case "strangerdisconnected": 
                self.isconnected = False
                return Event.STRANGERDISCONNECTED, None

            case "typing": return Event.TYPING, None
            case "commonlikes": return Event.COMMONLIKES, body[1:]
            case "servermessage": return Event.SERVERMSG, body[1]
            case "error":
                self.isconnected = False
                return Event.ERROR, body[1]

            case "connectiondied":
                self.isconnected = False
                return Event.CONNECTIONDIED, None

            case "antinudebanned":
                self.isconnected = False
                self.isbanned = True
                raise Banned("Anti-nude banned")

            case _:
                return Event.SLEEP, None