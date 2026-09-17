from unittest import TestCase
from unittest.mock import patch

from shared.constants import Direction, Team

from src.actions import (
    create_player,
    increase_score,
    move_player,
    restart_round,
    revive_player,
    shoot_action,
    teleport_player,
)
from src.entidades import Jugador
from src.exceptions import (
    BlockedPosition,
    CantMove,
    CantShoot,
    InvalidMovementDirection,
    InvalidShootDirection,
    PlayerDoesNotExist,
    RespawnFull,
)
from src.handlers import CreaturesHandler
from src.mapa import Mapa
from src.score import Score


def callback(*args):  # dummy callback
    return args


class ActionsTest(TestCase):

    def setUp(self):
        self.pw_map = Mapa("test")
        self.score = Score()
        self.ch = CreaturesHandler()
        self.ch.jugadores = {}
        self.ch.pw_map = self.pw_map
        self.ch.score = self.score

    def test_login_blue(self):
        player, _, _, _ = create_player(Team.BLUE, self.ch)
        self.assertEqual(player.get_team(), 1)

    def test_login_red(self):
        player, _, _, _ = create_player(Team.RED, self.ch)
        self.assertEqual(player.get_team(), 2)

    def test_player_get_data(self):
        player, _, _, _ = create_player(Team.BLUE, self.ch)
        self.assertEqual(player.get_data(), [2, 1, 34, 2, 100, 100])

    def test_wrong_player_uid(self):
        self.assertRaises(PlayerDoesNotExist, self.ch.get_creature_by_uid, 157)

    def test_lost_connection_handler(self):
        player, _, _, _ = create_player(Team.BLUE, self.ch)
        uid = player.uid
        self.ch.del_creature_by_uid(uid)
        self.assertRaises(PlayerDoesNotExist, self.ch.get_creature_by_uid, uid)

    def test_teleport_player(self):
        player, _, _, _ = create_player(Team.BLUE, self.ch)
        teleport_player(player.uid, 1, 1, self.ch)
        self.assertEqual((player.x, player.y), (1, 1))

    @patch.object(Jugador, "MOVE_COOLDOWN", 0) # no move locks
    def test_move_valid(self):
        player, _, _, _ = create_player(Team.BLUE, self.ch)
        for d in (Direction.NORTH, Direction.SOUTH, Direction.WEST, Direction.EAST):
            before_x, before_y = player.get_coor()
            moved_player = move_player(player.get_uid(), d, self.ch)
            self.assertTrue(before_x != moved_player.x or before_y != moved_player.y)

    def test_move_invalid(self):
        player, _, _, _ = create_player(Team.BLUE, self.ch)
        self.assertRaises(
            InvalidMovementDirection,
            move_player,
            player.get_uid(),
            "bad_direction",
            self.ch,
        )

    def test_cant_move_exception(self):
        player, _, _, _ = create_player(Team.BLUE, self.ch)
        player.vivo = False
        self.assertRaises(CantMove, move_player, player.get_uid(), "n", self.ch)

    @patch.object(Jugador, "MOVE_COOLDOWN", 0) # no move locks
    def test_blocking_position(self):
        player, _, _, _ = create_player(Team.BLUE, self.ch)
        # move until the wall
        for d in (Direction.WEST, Direction.WEST, Direction.WEST):
            move_player(player.get_uid(), d, self.ch)
        # then try to walk over the wall -> not possible
        self.assertRaises(BlockedPosition, move_player, player.get_uid(), Direction.WEST, self.ch)

    def test_multiple_players_blue(self):
        _, others, _, _ = create_player(Team.BLUE, self.ch)
        self.assertEqual(others, [])
        _, others, _, _ = create_player(Team.BLUE, self.ch)
        self.assertEqual(len(others), 1)

    def test_multiple_players_red(self):
        _, others, _, _ = create_player(Team.RED, self.ch)
        self.assertEqual(others, [])
        _, others, _, _ = create_player(Team.RED, self.ch)
        self.assertEqual(len(others), 1)

    def test_full_team_base(self):
        for _ in range(9):
            create_player(Team.RED, self.ch)
        self.assertRaises(RespawnFull, create_player, Team.RED, self.ch)

    @patch.object(Jugador, "SHOOT_COOLDOWN", 0) # no move locks
    def test_shoot_directions(self):
        player, _, _, _ = create_player(Team.BLUE, self.ch)
        for d in (Direction.NORTH, Direction.SOUTH, Direction.WEST, Direction.EAST, Direction.NORTH_WEST, Direction.NORTH_EAST, Direction.SOUTH_WEST, Direction.SOUTH_EAST):
            bullet_handler = shoot_action(
                player.get_uid(), d, self.ch, callback, callback
            )
            self.assertIsNotNone(bullet_handler)

    def test_shoot_bad_direction(self):
        player, _, _, _ = create_player(Team.BLUE, self.ch)
        self.assertRaises(
            InvalidShootDirection,
            shoot_action,
            player.get_uid(),
            "bad_dir",
            self.ch,
            None,
            None,
        )

    def test_shoot_update(self):
        player, _, _, _ = create_player(Team.BLUE, self.ch)
        shoot_handler = shoot_action(player.get_uid(), Direction.NORTH, self.ch, callback, callback)
        before_y = shoot_handler.bala.y
        shoot_handler.loop()
        self.assertEqual(before_y - 1, shoot_handler.bala.y)

    def test_shoot_hit_wall(self):
        player, _, _, _ = create_player(Team.BLUE, self.ch)
        shoot_handler = shoot_action(player.get_uid(), Direction.WEST, self.ch, callback, callback)
        for _ in range(3):
            self.assertTrue(shoot_handler.update())
        self.assertFalse(shoot_handler.update())

    def test_shoot_friend(self):
        player1, _, _, pw_map = create_player(Team.BLUE, self.ch)
        player2, _, _, pw_map = create_player(Team.BLUE, self.ch)
        pw_map.move_player(player2, player1.x + 2, player1.y)
        shoot_handler = shoot_action(player1.get_uid(), Direction.EAST, self.ch, callback, callback)
        for _ in range(3):
            self.assertTrue(shoot_handler.update())

    def test_shoot_enemy(self):
        player1, _, _, pw_map = create_player(Team.BLUE, self.ch)
        player2, _, _, pw_map = create_player(Team.RED, self.ch)
        pw_map.move_player(player2, player1.x + 2, player1.y)
        shoot_handler = shoot_action(player1.get_uid(), Direction.EAST, self.ch, callback, callback)
        health_before = player2.vida
        self.assertTrue(shoot_handler.update())  # move 1 sqm
        self.assertFalse(shoot_handler.update())  # hit the enemy
        self.assertLess(player2.vida, health_before)

    def test_cant_shoot_exception(self):
        player1, _, _, _ = create_player(Team.BLUE, self.ch)
        player1.vivo = False
        self.assertRaises(
            CantShoot, shoot_action, player1.get_uid(), Direction.EAST, self.ch, callback, callback
        )

    def test_kill_and_revive_enemy(self):
        player1, _, _, pw_map = create_player(Team.BLUE, self.ch)
        player2, _, _, pw_map = create_player(Team.RED, self.ch)
        pw_map.move_player(player2, player1.x + 1, player1.y)
        shoot_handler = shoot_action(
            player1.get_uid(), Direction.EAST, self.ch, callback, callback
        )
        player2.vida = 1
        shoot_handler.loop()
        self.assertFalse(player2.vivo)
        revive_player(player2.uid, self.ch)
        self.assertTrue(player2.vivo)
        self.assertEqual(player2.vida, CreaturesHandler.VIDA_MAX)

    def test_score_from_blue(self):
        player1, _, _, pw_map = create_player(Team.BLUE, self.ch)
        player2, _, _, pw_map = create_player(Team.RED, self.ch)

        def die_callback(uid):
            return increase_score(uid, self.ch)

        pw_map.move_player(player2, player1.x + 1, player1.y)
        shoot_handler = shoot_action(
            player1.get_uid(), Direction.EAST, self.ch, callback, die_callback
        )
        player2.vida = 1
        self.assertEqual(self.score.blue_score, 0)
        shoot_handler.loop()
        self.assertEqual(self.score.blue_score, 1)

    def test_score_from_red(self):
        player1, _, _, pw_map = create_player(Team.RED, self.ch)
        player2, _, _, pw_map = create_player(Team.BLUE, self.ch)

        def die_callback(uid):
            return increase_score(uid, self.ch)

        pw_map.move_player(player2, player1.x + 1, player1.y)
        shoot_handler = shoot_action(
            player1.get_uid(), Direction.EAST, self.ch, callback, die_callback
        )
        player2.vida = 1
        self.assertEqual(self.score.red_score, 0)
        shoot_handler.loop()
        self.assertEqual(self.score.red_score, 1)

    def test_restart_round(self):
        player1, _, _, pw_map = create_player(Team.BLUE, self.ch)
        player2, _, _, pw_map = create_player(Team.RED, self.ch)

        # move both one place
        teleport_player(player1.uid, player1.x + 1, player1.y + 1, self.ch)
        teleport_player(player2.uid, player2.x + 1, player2.y + 1, self.ch)
        # change life
        player1.vida = 1
        player2.vida = 1
        # change score
        self.score.murio_azul()
        self.score.murio_rojo()
        # restart
        players, new_score = restart_round(self.ch)

        # base positions
        players = list(players)
        player_blue = players.pop(0) if players[0].team == Team.BLUE else players.pop()
        player_red = players.pop()
        # blue
        self.assertEqual(player_blue.x, pw_map.x_azul)
        self.assertEqual(player_blue.y, pw_map.y_azul)
        self.assertEqual(player_blue.vida, self.ch.VIDA_MAX)
        # red
        self.assertEqual(player_red.x, pw_map.x_rojo)
        self.assertEqual(player_red.y, pw_map.y_rojo)
        self.assertEqual(player_red.vida, self.ch.VIDA_MAX)
        # score
        self.assertEqual(new_score[0], 0)
        self.assertEqual(new_score[1], 0)
