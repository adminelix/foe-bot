import json
import logging

from domain.account import Account
from foe_bot.request import Request
from foe_bot.response_mapper import map_to_account


class FriendsTavernService:
    def __init__(self, acc: Account):
        self.__acc = acc
        self.__request_session = Request()
        self.__logger = logging.getLogger("FriendsTavernService")
        if not self.__acc.own_tavern:
            self.refresh_own_tavern()

    def refresh_own_tavern(self):
        request_body = self.__request_session.create_rest_body('FriendsTavernService', 'getOwnTavern', [])
        response, _ = self.__request_session.send(request_body)
        map_to_account(self.__acc, *response)

    def collect(self):
        own_tavern_state = self.__acc.other_tavern_states.get(self.__acc.city_user_data.player_id, None)
        if own_tavern_state and own_tavern_state.unlockedChairCount == own_tavern_state.sittingPlayerCount:
            request_body = self.__request_session.create_rest_body('FriendsTavernService', 'collectReward', [])
            response, success = self.__request_session.send(request_body)
            if success:
                map_to_account(self.__acc, *response)
                self.__logger.info("collected tavern rewards")
                self.refresh_own_tavern()

    def visit(self):
        states = self.__acc.other_tavern_states
        player_ids_to_visit = [state.ownerId for state in states.values() if
                               not state.state and state.sittingPlayerCount < state.unlockedChairCount]
        visited = 0
        for id in player_ids_to_visit:
            request_body = self.__request_session.create_rest_body('FriendsTavernService', 'getOtherTavern', [id])
            response, success = self.__request_session.send(request_body)
            map_to_account(self.__acc, *response)
            sat_down = 'satdown' in json.dumps(response).lower()
            if success and sat_down:
                visited += 1

        if visited > 0:
            self.__logger.info(f"visited {visited} friend taverns")

    def extend_tavern(self):
        # TODO implement
        pass

# getownTavern directly after collect to get tavern state


# [
#     {
#         "__class__": "ServerRequest",
#         "requestData": [],
#         "requestClass": "FriendsTavernService",
#         "requestMethod": "getOwnTavern",
#         "requestId": 15
#     }
# ]
#
# [
#     {
#         "responseData": {
#             "view": {
#                 "tableLevel": 6,
#                 "unlockedChairs": 16,
#                 "visitors": [
#                     {
#                         "player_id": 849102670,
#                         "name": "JuelzSantana",
#                         "avatar": "portrait_id_171",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 365646,
#                         "name": "Molchie",
#                         "avatar": "addon_portrait_id_wildlife_halona",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 849404403,
#                         "name": "Richard Eisenherz",
#                         "avatar": "portrait_id_149",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 1285707,
#                         "name": "pingiun",
#                         "avatar": "portrait_id_24",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 7690382,
#                         "name": "Agatha 737 die Mächtige",
#                         "avatar": "portrait_id_142",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 9973421,
#                         "name": "Balduin mit dem Beil",
#                         "avatar": "addon_portrait_id_halloween_creepy_clown",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 849741992,
#                         "name": "Zeno 602 der Krieger",
#                         "avatar": "portrait_id_1",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 849566842,
#                         "name": "Agrippa 870 der Zornige",
#                         "avatar": "addon_portrait_id_jeoff",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 7670781,
#                         "name": "Bobi Der Treue",
#                         "avatar": "portrait_id_99",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 4151112,
#                         "name": "Vogel91",
#                         "avatar": "portrait_id_107",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 9901905,
#                         "name": "Tamerlane",
#                         "avatar": "addon_portrait_id_halloween_fortune",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 8711516,
#                         "name": "Naiara die Loyale",
#                         "avatar": "addon_portrait_id_makeda",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 849085821,
#                         "name": "Darkside-DNA",
#                         "avatar": "addon_portrait_id_skully",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 849095034,
#                         "name": "Geronimus",
#                         "avatar": "addon_portrait_id_pirate_king",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 5797899,
#                         "name": "Eumel 13",
#                         "avatar": "addon_portrait_id_soccer_fan_margaret",
#                         "__class__": "BasePlayer"
#                     },
#                     {
#                         "player_id": 850036569,
#                         "name": "bau0",
#                         "avatar": "portrait_id_10",
#                         "__class__": "BasePlayer"
#                     }
#                 ],
#                 "selectedCustomizationIds": {
#                     "tablecloth": "tablecloth_5",
#                     "tray": "tray_5",
#                     "flooring": "flooring_5"
#                 },
#                 "tavernSilverBase": 62,
#                 "tavernSilverAdd": 2,
#                 "__class__": "TavernView"
#             },
#             "unlockedCustomizationIds": [
#                 "tablecloth_0",
#                 "tray_0",
#                 "flooring_0",
#                 "tablecloth_1",
#                 "tablecloth_2",
#                 "tablecloth_3",
#                 "tablecloth_4",
#                 "tray_1",
#                 "flooring_1",
#                 "tablecloth_5",
#                 "tray_2",
#                 "flooring_2",
#                 "tray_3",
#                 "flooring_3",
#                 "tray_4",
#                 "tray_5",
#                 "flooring_4",
#                 "flooring_5"
#             ],
#             "friendCount": 70,
#             "__class__": "OwnTavern"
#         },
#         "requestClass": "FriendsTavernService",
#         "requestMethod": "getOwnTavern",
#         "requestId": 15,
#         "__class__": "ServerResponse"
#     }
# ]
#
# [
#     {
#         "__class__": "ServerRequest",
#         "requestData": [],
#         "requestClass": "FriendsTavernService",
#         "requestMethod": "collectReward",
#         "requestId": 17
#     }
# ]
#
# [
#     {
#         "responseData": {
#             "__class__": "Success"
#         },
#         "requestClass": "FriendsTavernService",
#         "requestMethod": "collectReward",
#         "requestId": 17,
#         "__class__": "ServerResponse"
#     }
# ]
