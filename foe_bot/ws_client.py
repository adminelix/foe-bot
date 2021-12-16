import asyncio
import json
import logging
import threading
import time
from asyncio import exceptions

import websockets

from domain.account import Account
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account


class WsClient:

    def __init__(self, acc: Account, url: str, token: str):
        self.__logger = logging.getLogger("ws_client")
        self.__logger.setLevel(logging.DEBUG)
        self.__acc: Account = acc
        self.__url: str = url
        self.__is_connected: bool = False
        self.__stop_thread: bool = False
        self.__req_queue: list[str] = []
        self.__token: str = token
        self.__req_session: Request = Request()
        self.__connected_since: int = 0
        self.__connection_time: int = 0
        self.__reconnects: int = -1
        self.__task = None
        self.__loop = None
        self.__thread = None

    def stop(self):
        self.__stop_thread = True
        time.sleep(0.2)
        self.__task.cancel()
        self.__loop.stop()

    @staticmethod
    def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def run(self):
        self.__loop = asyncio.new_event_loop()
        self.__thread = threading.Thread(target=self.start_background_loop, args=(self.__loop,), daemon=True)
        self.__thread.start()
        self.__task = asyncio.run_coroutine_threadsafe(self.socket(), self.__loop)

    async def socket(self):
        header = self.get_header()
        logger = logging.getLogger("websockets.client")
        logger.setLevel(logging.INFO)
        async for websocket in websockets.connect(self.__url, ping_interval=30, extra_headers=header,
                                                  logger=logger):
            try:
                body = self.__req_session.create_ws_body('SocketAuthenticationService', 'authWithToken', [self.__token])
                await websocket.send(body)

                raw = await websocket.recv()
                response = foe_json_loads(raw)[0]

                if 'authWithToken' == response['requestMethod'] and response['responseData']:
                    self.__is_connected = True
                    self.__logger.info("logged into websocket")
                    self.__reconnects += 1
                    self.__connected_since = int(time.time())
                    self.__register_chats()

                while not self.__stop_thread:
                    self.__connection_time = int(time.time()) - self.__connected_since

                    if len(self.__req_queue) != 0:
                        body = self.__req_queue.pop(0)
                        await websocket.send(body)

                    try:
                        # await would block thread until something is received, therefore with timeout
                        msg = await asyncio.wait_for(websocket.recv(), 0.1)
                        self.__logger.debug(f"received message: {msg}")
                        json_ = foe_json_loads(msg)
                        json_ = json_ if type(json_) == list else [json_]
                        map_to_account(self.__acc, *json_)
                    except exceptions.TimeoutError:
                        # catch timeout that the loop can jump to next iteration and jump out if thread should be closed
                        pass

                break

            except websockets.ConnectionClosed as ex:
                self.__logger.warning(f"websocket closed unexpectedly: {ex}")
                continue
            except Exception as ex:
                self.__logger.error(f"websocket error: {ex}")
            finally:
                self.__is_connected = False

    def get_cookies(self):
        cookies = self.__req_session._session.cookies.get_dict(
            domain='de14.forgeofempires.com') | self.__req_session._session.cookies.get_dict(
            domain='.forgeofempires.com')
        cookies_str = ', '.join(key + '=' + value for key, value in cookies.items())
        return cookies_str

    def get_header(self):
        headers = dict(
            filter(lambda val: val[0] == 'User-Agent' or val[0] == 'Accept-Encoding',
                   self.__req_session.headers.items()))
        headers['Accept-Language'] = 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7'
        headers['Pragma'] = 'no-cache'
        headers['Cache-Control'] = 'no-cache'
        headers['Cookie'] = self.get_cookies()
        return headers

    def __register_chats(self):
        self.__logger.debug("registering chats")
        self.__req_queue.append(self.__req_session.create_ws_body('ChatService', 'joinChat', ["chat_global"]))
        self.__req_queue.append(self.__req_session.create_ws_body('ChatService', 'joinChat', ["chat_neighbors"]))
        if self.__acc.city_user_data.clan_name:
            self.__req_queue.append(self.__req_session.create_ws_body('ChatService', 'joinChat', ["chat_clan"]))

    def send(self, msg: str) -> None:
        self.__req_queue.append(msg)

    @property
    def is_connected(self) -> bool:
        return self.__is_connected

    @property
    def reconnects(self) -> int:
        return self.__reconnects

    @property
    def connection_time(self) -> int:
        return self.__connection_time
