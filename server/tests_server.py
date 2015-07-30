import sys
import os

sys.path += os.path.join(os.path.dirname(__file__), '..')

from twisted.trial import unittest

from src.exceptions import InvalidMovementDirection, BlockedPosition, InvalidShootDirection
from src.mapa import Mapa
from src.protocol import create_player, move_player, shoot_action
from src.handlers import HandlerCriaturas


class ActionsTest(unittest.TestCase):

    def setUp(self):
        self.mapa = Mapa("mapa")
        self.hcriat = HandlerCriaturas()
        self.hcriat.jugadores = {}
        self.hcriat.mapa = self.mapa

    def test_login_blue(self):
        player, others, map = create_player(1, self.hcriat)
        self.assertEqual(player.get_team(), 1)

    def test_login_red(self):
        player, others, map = create_player(2, self.hcriat)
        self.assertEqual(player.get_team(), 2)

    def test_move_valid(self):
        player, others, map = create_player(1, self.hcriat)
        for d in ('n', 's', 'o', 'e'):
            before_x, before_y = player.get_coor()
            moved_player = move_player(player.get_uid(), d, self.hcriat)
            self.assertTrue(before_x != moved_player.x or before_y != moved_player.y)

    def test_move_invalid(self):
        player, others, map = create_player(1, self.hcriat)
        self.assertRaises(
            InvalidMovementDirection, move_player, player.get_uid(), 'bad_direction', self.hcriat)

    def test_blocking_position(self):
        player, others, map = create_player(1, self.hcriat)
        for d in ('o', 'o', 'o'):
            move_player(player.get_uid(), d, self.hcriat)
        self.assertRaises(BlockedPosition, move_player, player.get_uid(), 'o', self.hcriat)

    def test_multiple_players(self):
        player, others, map = create_player(1, self.hcriat)
        self.assertEqual(others, [])
        player, others, map = create_player(1, self.hcriat)
        self.assertEqual(len(others), 1)

    def test_shoot_directions(self):
        player, others, map = create_player(1, self.hcriat)
        for d in ('n', 's', 'o', 'e', 'no', 'ne', 'so', 'se'):
            player, shoot_handler = shoot_action(player.get_uid(), d, self.hcriat, None)
            self.assertIsNot(shoot_handler, None)

    def test_shoot_bad_direction(self):
        player, others, map = create_player(1, self.hcriat)
        self.assertRaises(
            InvalidShootDirection, shoot_action, player.get_uid(), 'bad_dir', self.hcriat, None)

    def test_shoot_update(self):
        player, others, map = create_player(1, self.hcriat)
        player, shoot_handler = shoot_action(player.get_uid(), 'n', self.hcriat, None)
        before_y = shoot_handler.bala.y
        shoot_handler.update()
        self.assertEqual(before_y - 1, shoot_handler.bala.y)

    def test_shoot_hit_wall(self):
        player, others, map = create_player(1, self.hcriat)
        player, shoot_handler = shoot_action(player.get_uid(), 'o', self.hcriat, None)
        for i in range(3):
            self.assertTrue(shoot_handler.update())
        self.assertFalse(shoot_handler.update())

    def test_shoot_friend(self):
        player1, others, map = create_player(1, self.hcriat)
        player2, others, map = create_player(1, self.hcriat)
        map.moverJugador(player2, player1.x+2, player1.y)
        player, shoot_handler = shoot_action(player1.get_uid(), 'e', self.hcriat, None)
        for i in range(3):
            self.assertTrue(shoot_handler.update())

    def test_shoot_enemy(self):
        player1, others, map = create_player(1, self.hcriat)
        player2, others, map = create_player(2, self.hcriat)
        map.moverJugador(player2, player1.x+2, player1.y)
        callback = lambda x, y: (x, y)
        player, shoot_handler = shoot_action(player1.get_uid(), 'e', self.hcriat, callback)
        healt_before = player2.vida
        self.assertTrue(shoot_handler.update())  # move 1 sqm
        self.assertFalse(shoot_handler.update())  # hit the enemy
        self.assertLess(player2.vida, healt_before)