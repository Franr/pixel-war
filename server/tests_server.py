from unittest import TestCase

from main import Server
from src.exceptions import (
    InvalidMovementDirection, BlockedPosition, InvalidShootDirection, CantShoot, CantMove,
    TeamBasePositionNotFound, PlayerDoesNotExist)
from src.mapa import Mapa
from src.score import Score
from src.protocol import (
    create_player, move_player, shoot_action, revive_player, teleport_player, increase_score,
    restart_round)
from src.handlers import HandlerCriaturas


class ActionsTest(TestCase):

    def setUp(self):
        self.pw_map = Mapa("mapa")
        self.score = Score()
        self.hcriat = HandlerCriaturas()
        self.hcriat.jugadores = {}
        self.hcriat.pw_map = self.pw_map
        self.hcriat.score = self.score

    def test_main(self):
        server = Server()
        self.assertTrue(isinstance(server.pw_map, Mapa))
        self.assertTrue(isinstance(server.score, Score))
        self.assertTrue(isinstance(server.hcriat, HandlerCriaturas))

    def test_login_blue(self):
        player, others, score, pw_map = create_player(1, self.hcriat)
        self.assertEqual(player.get_team(), 1)

    def test_login_red(self):
        player, others, score, pw_map = create_player(2, self.hcriat)
        self.assertEqual(player.get_team(), 2)

    def test_player_get_data(self):
        player, others, score, pw_map = create_player(1, self.hcriat)
        self.assertEqual(player.get_data(), [3, 1, 34, 23, 100, 100])

    def test_wrong_player_uid(self):
        self.assertRaises(PlayerDoesNotExist, self.hcriat.get_creature_by_uid, 157)

    def test_lost_connection_handler(self):
        player, others, score, pw_map = create_player(1, self.hcriat)
        uid = player.uid
        self.hcriat.del_creature_by_uid(uid)
        self.assertRaises(PlayerDoesNotExist, self.hcriat.get_creature_by_uid, uid)

    def test_teleport_player(self):
        player, others, score, pw_map = create_player(1, self.hcriat)
        teleport_player(player.uid, 1, 1, self.hcriat)
        self.assertEqual((player.x, player.y), (1, 1))

    def test_move_valid(self):
        player, others, score, pw_map = create_player(1, self.hcriat)
        for d in ('n', 's', 'o', 'e'):
            before_x, before_y = player.get_coor()
            moved_player = move_player(player.get_uid(), d, self.hcriat)
            self.assertTrue(before_x != moved_player.x or before_y != moved_player.y)
            player.bloqM.unblock()

    def test_move_invalid(self):
        player, others, score, pw_map = create_player(1, self.hcriat)
        self.assertRaises(
            InvalidMovementDirection, move_player, player.get_uid(), 'bad_direction', self.hcriat)

    def test_cant_move_exception(self):
        player, others, score, pw_map = create_player(1, self.hcriat)
        player.vivo = False
        self.assertRaises(
            CantMove, move_player, player.get_uid(), 'n', self.hcriat)

    def test_blocking_position(self):
        player, others, score, pw_map = create_player(1, self.hcriat)
        for d in ('o', 'o', 'o'):
            move_player(player.get_uid(), d, self.hcriat)
            player.bloqM.unblock()
        self.assertRaises(BlockedPosition, move_player, player.get_uid(), 'o', self.hcriat)

    def test_multiple_players_blue(self):
        player, others, score, pw_map = create_player(1, self.hcriat)
        self.assertEqual(others, [])
        player, others, score, pw_map = create_player(1, self.hcriat)
        self.assertEqual(len(others), 1)

    def test_multiple_players_red(self):
        player, others, score, pw_map = create_player(2, self.hcriat)
        self.assertEqual(others, [])
        player, others, score, pw_map = create_player(2, self.hcriat)
        self.assertEqual(len(others), 1)

    def test_full_team_base(self):
        for i in range(9):
            create_player(2, self.hcriat)
        self.assertRaises(TeamBasePositionNotFound, create_player, 2, self.hcriat)

    def test_shoot_directions(self):
        player, others, score, pw_map = create_player(1, self.hcriat)
        for d in ('n', 's', 'o', 'e', 'no', 'ne', 'so', 'se'):
            player, shoot_handler = shoot_action(player.get_uid(), d, self.hcriat, None, None)
            self.assertIsNot(shoot_handler, None)
            player.bloqD.unblock()

    def test_shoot_bad_direction(self):
        player, others, score, pw_map = create_player(1, self.hcriat)
        self.assertRaises(
            InvalidShootDirection, shoot_action, player.get_uid(), 'bad_dir', self.hcriat, None,
            None)

    def test_shoot_update(self):
        player, others, score, pw_map = create_player(1, self.hcriat)
        player, shoot_handler = shoot_action(player.get_uid(), 'n', self.hcriat, None, None)
        before_y = shoot_handler.bala.y
        shoot_handler.update()
        self.assertEqual(before_y - 1, shoot_handler.bala.y)

    def test_shoot_hit_wall(self):
        player, others, score, pw_map = create_player(1, self.hcriat)
        player, shoot_handler = shoot_action(player.get_uid(), 'o', self.hcriat, None, None)
        for i in range(3):
            self.assertTrue(shoot_handler.update())
        self.assertFalse(shoot_handler.update())

    def test_shoot_friend(self):
        player1, others, score, pw_map = create_player(1, self.hcriat)
        player2, others, score, pw_map = create_player(1, self.hcriat)
        pw_map.move_player(player2, player1.x+2, player1.y)
        player, shoot_handler = shoot_action(player1.get_uid(), 'e', self.hcriat, None, None)
        for i in range(3):
            self.assertTrue(shoot_handler.update())

    def test_shoot_enemy(self):
        player1, others, score, pw_map = create_player(1, self.hcriat)
        player2, others, score, pw_map = create_player(2, self.hcriat)
        pw_map.move_player(player2, player1.x+2, player1.y)
        callback = lambda x, y: (x, y)  # dummy callback
        player, shoot_handler = shoot_action(player1.get_uid(), 'e', self.hcriat, callback, None)
        healt_before = player2.vida
        self.assertTrue(shoot_handler.update())  # move 1 sqm
        self.assertFalse(shoot_handler.update())  # hit the enemy
        self.assertLess(player2.vida, healt_before)

    def test_cant_shoot_exception(self):
        player1, others, score, pw_map = create_player(1, self.hcriat)
        callback = lambda x, y: (x, y)  # dummy callback
        player1.vivo = False
        self.assertRaises(
            CantShoot, shoot_action, player1.get_uid(), 'e', self.hcriat, callback, None)

    def test_kill_and_revive_enemy(self):
        player1, others, score, pw_map = create_player(1, self.hcriat)
        player2, others, score, pw_map = create_player(2, self.hcriat)
        pw_map.move_player(player2, player1.x+1, player1.y)
        callback = lambda x, y: (x, y)  # dummy callback
        die_callback = lambda x: x  # dummy callback
        player, shoot_handler = shoot_action(
            player1.get_uid(), 'e', self.hcriat, callback, die_callback)
        player2.vida = 1
        shoot_handler.update()
        self.assertFalse(player2.vivo)
        revive_player(player2.uid, self.hcriat)
        self.assertTrue(player2.vivo)
        self.assertEqual(player2.vida, HandlerCriaturas.VIDA_MAX)

    def test_score_from_blue(self):
        player1, others, score, pw_map = create_player(1, self.hcriat)
        player2, others, score, pw_map = create_player(2, self.hcriat)
        pw_map.move_player(player2, player1.x+1, player1.y)
        callback = lambda x, y: (x, y)  # dummy callback
        die_callback = lambda uid: increase_score(uid, self.hcriat)
        player, shoot_handler = shoot_action(
            player1.get_uid(), 'e', self.hcriat, callback, die_callback)
        player2.vida = 1
        self.assertEqual(self.score.blue_score, 0)
        shoot_handler.update()
        self.assertEqual(self.score.blue_score, 1)

    def test_score_from_red(self):
        player1, others, score, pw_map = create_player(2, self.hcriat)
        player2, others, score, pw_map = create_player(1, self.hcriat)
        pw_map.move_player(player2, player1.x+1, player1.y)
        callback = lambda x, y: (x, y)  # dummy callback
        die_callback = lambda uid: increase_score(uid, self.hcriat)
        player, shoot_handler = shoot_action(
            player1.get_uid(), 'e', self.hcriat, callback, die_callback)
        player2.vida = 1
        self.assertEqual(self.score.red_score, 0)
        shoot_handler.update()
        self.assertEqual(self.score.red_score, 1)

    def test_restart_round(self):
        player1, others, score, pw_map = create_player(1, self.hcriat)
        player2, others, score, pw_map = create_player(2, self.hcriat)
        # move both once place
        teleport_player(player1.uid, player1.x+1, player1.y+1, self.hcriat)
        teleport_player(player2.uid, player2.x+1, player2.y+1, self.hcriat)
        # change life
        player1.vida = 1
        player2.vida = 1
        # change score
        self.score.murio_azul()
        self.score.murio_rojo()
        # restart
        players, new_score = restart_round(player1.uid, self.hcriat)
        # base positions
        new_blue = players.pop(0) if players[0].team == self.hcriat.BLUE else players.pop()
        new_red = players.pop()
        # blue
        self.assertEqual(new_blue.x, pw_map.x_azul)
        self.assertEqual(new_blue.y, pw_map.y_azul)
        self.assertEqual(new_blue.vida, self.hcriat.VIDA_MAX)
        # red
        self.assertEqual(new_red.x, pw_map.x_rojo)
        self.assertEqual(new_red.y, pw_map.y_rojo)
        self.assertEqual(new_red.vida, self.hcriat.VIDA_MAX)
        # score
        self.assertEqual(new_score[0], 0)
        self.assertEqual(new_score[1], 0)
