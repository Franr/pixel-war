from unittest.case import TestCase
from unittest.mock import MagicMock, patch

from shared.commands import (
    CreateObject,
    CreateObjects,
    MoveObject,
    PlayerHit,
    PlayerRevive,
    PlayerShoot,
    SendMap,
    UpdateScore,
)
from shared.constants import Direction, Team

from src.actions import create_player
from src.exceptions import PlayerDoesNotExist
from src.game import GameHandler


class GameHandlerTest(TestCase):
    DUMMY_PLAYER_ID = 1

    def setUp(self):
        self.server = MagicMock()
        self.client = MagicMock()
        self.gh = GameHandler(self.server)

    def test_receive_login(self):
        new_player_uid = self.gh.login(self.client, Team.BLUE, "correlation-token")

        # receive map
        self.assertIsInstance(self.client.send_message.call_args_list[0][0][0], SendMap)
        # receive new player
        self.assertIsInstance(self.server.broadcast.call_args_list[0][0][0], CreateObject)
        # receive all other players
        self.assertIsInstance(self.client.send_message.call_args_list[1][0][0], CreateObjects)
        # client receive score
        self.assertIsInstance(self.client.send_message.call_args_list[2][0][0], UpdateScore)

        # player registered
        self.assertIn(new_player_uid['uid'], self.gh.peers.values())

    def test_receive_move(self):
        # moving a player who doesn't exists
        self.assertFalse(self.gh.move(self.client, self.DUMMY_PLAYER_ID, Direction.NORTH))

        player, _, _, _ = create_player(Team.BLUE, self.gh.ch)
        
        # player who can't move
        with player._movement_lock.guard():
            self.assertFalse(self.gh.move(self.client, player.uid, Direction.SOUTH))

        # moving an existing player
        with patch.object(player._movement_lock, "cooldown", 0):
            self.assertTrue(self.gh.move(self.client, player.uid, Direction.NORTH))
            self.assertIsInstance(self.server.broadcast.call_args_list[0][0][0], MoveObject)

    def test_receive_player_shoot(self):
        # shoots from a player who doesn't exists
        self.assertFalse(self.gh.shoot(self.client, self.DUMMY_PLAYER_ID, Direction.NORTH))

        player, _, _, _ = create_player(Team.BLUE, self.gh.ch)

        # happy path
        self.assertTrue(self.gh.shoot(self.client, player.uid, Direction.NORTH))
        self.assertIsInstance(self.server.broadcast.call_args_list[0][0][0], PlayerShoot)

        # player who can't shot
        with player._shoot_lock.guard():
            self.assertFalse(self.gh.shoot(self.client, player.uid, Direction.NORTH))

    def test_hit_callback(self):
        self.assertTrue(self.gh._hit_callback(self.DUMMY_PLAYER_ID, damage=1))
        self.assertIsInstance(self.server.broadcast.call_args_list[0][0][0], PlayerHit)

    def test_die_callback(self):        
        player, _, _, _ = create_player(Team.BLUE, self.gh.ch)

        self.assertTrue(self.gh._die_callback(player.uid))
        self.assertIsInstance(self.server.broadcast.call_args_list[0][0][0], PlayerRevive)
        self.assertIsInstance(self.server.broadcast.call_args_list[1][0][0], UpdateScore)

    # def test_restart_round(self):
        # self.assertEqual(self.pwp.restart_round(self.player.uid), OK_RESPONSE)

    # def test_connection_lost(self):
        # self.assertEqual(self.pwp.login(1), {'uid': 3})
        # self.assertEqual(len(self.ch.jugadores), 2)
        # self.pwp.connectionLost('test')
        # self.assertEqual(len(self.ch.jugadores), 1)
