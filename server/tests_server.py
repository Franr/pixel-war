from twisted.internet import reactor
from twisted.trial.unittest import TestCase
from twisted.test.proto_helpers import StringTransport

from main import Server
from src.actions import (
    create_player, move_player, shoot_action, revive_player, teleport_player, increase_score,
    restart_round)
from src.exceptions import (
    InvalidMovementDirection, BlockedPosition, InvalidShootDirection, CantShoot, CantMove,
    TeamBasePositionNotFound, PlayerDoesNotExist)
from src.constants import Team
from src.handlers import CreaturesHandler
from src.mapa import Mapa
from src.score import Score
from src.protocol import PWProtocolFactory


OK_RESPONSE = {'ok': 1}


def callback(*args):  # dummy callback
    return args


class NoDelayTransport(StringTransport):

    def setTcpNoDelay(self, bla):
        pass


class ActionsTest(TestCase):

    def setUp(self):
        self.pw_map = Mapa("test")
        self.score = Score()
        self.hcriat = CreaturesHandler()
        self.hcriat.jugadores = {}
        self.hcriat.pw_map = self.pw_map
        self.hcriat.score = self.score

    def tearDown(self):
        """Cancel all the pending calls to avoid problems"""
        pending = reactor.getDelayedCalls()
        for p in pending:
            if p.active():
                p.cancel()

    def test_main(self):
        server = Server()
        self.assertTrue(isinstance(server.pw_map, Mapa))
        self.assertTrue(isinstance(server.score, Score))
        self.assertTrue(isinstance(server.hcriat, CreaturesHandler))

    def test_login_blue(self):
        player, _, _, _ = create_player(Team.BLUE, self.hcriat)
        self.assertEqual(player.get_team(), 1)

    def test_login_red(self):
        player, _, _, _ = create_player(Team.RED, self.hcriat)
        self.assertEqual(player.get_team(), 2)

    def test_player_get_data(self):
        player, _, _, _ = create_player(Team.BLUE, self.hcriat)
        self.assertEqual(player.get_data(), [2, 1, 34, 2, 100, 100])

    def test_wrong_player_uid(self):
        self.assertRaises(PlayerDoesNotExist, self.hcriat.get_creature_by_uid, 157)

    def test_lost_connection_handler(self):
        player, _, _, _ = create_player(Team.BLUE, self.hcriat)
        uid = player.uid
        self.hcriat.del_creature_by_uid(uid)
        self.assertRaises(PlayerDoesNotExist, self.hcriat.get_creature_by_uid, uid)

    def test_teleport_player(self):
        player, _, _, _ = create_player(Team.BLUE, self.hcriat)
        teleport_player(player.uid, 1, 1, self.hcriat)
        self.assertEqual((player.x, player.y), (1, 1))

    def test_move_valid(self):
        player, _, _, _ = create_player(Team.BLUE, self.hcriat)
        for d in ('n', 's', 'o', 'e'):
            before_x, before_y = player.get_coor()
            moved_player = move_player(player.get_uid(), d, self.hcriat)
            self.assertTrue(before_x != moved_player.x or before_y != moved_player.y)
            player.bloqM.unblock()

    def test_move_invalid(self):
        player, _, _, _ = create_player(Team.BLUE, self.hcriat)
        self.assertRaises(
            InvalidMovementDirection, move_player, player.get_uid(), 'bad_direction', self.hcriat)

    def test_cant_move_exception(self):
        player, _, _, _ = create_player(Team.BLUE, self.hcriat)
        player.vivo = False
        self.assertRaises(
            CantMove, move_player, player.get_uid(), 'n', self.hcriat)

    def test_blocking_position(self):
        player, _, _, _ = create_player(Team.BLUE, self.hcriat)
        for d in ('o', 'o', 'o'):
            move_player(player.get_uid(), d, self.hcriat)
            player.bloqM.unblock()
        self.assertRaises(BlockedPosition, move_player, player.get_uid(), 'o', self.hcriat)

    def test_multiple_players_blue(self):
        _, others, _, _ = create_player(Team.BLUE, self.hcriat)
        self.assertEqual(others, [])
        _, others, _, _ = create_player(Team.BLUE, self.hcriat)
        self.assertEqual(len(others), 1)

    def test_multiple_players_red(self):
        _, others, _, _ = create_player(Team.RED, self.hcriat)
        self.assertEqual(others, [])
        _, others, _, _ = create_player(Team.RED, self.hcriat)
        self.assertEqual(len(others), 1)

    def test_full_team_base(self):
        for i in range(9):
            create_player(Team.RED, self.hcriat)
        self.assertRaises(TeamBasePositionNotFound, create_player, Team.RED, self.hcriat)

    def test_shoot_directions(self):
        player, _, _, _ = create_player(Team.BLUE, self.hcriat)
        for d in ('n', 's', 'o', 'e', 'no', 'ne', 'so', 'se'):
            player, shoot_handler = shoot_action(player.get_uid(), d, self.hcriat, None, None)
            self.assertIsNot(shoot_handler, None)
            player.bloqD.unblock()

    def test_shoot_bad_direction(self):
        player, _, _, _ = create_player(Team.BLUE, self.hcriat)
        self.assertRaises(
            InvalidShootDirection, shoot_action, player.get_uid(), 'bad_dir', self.hcriat, None,
            None)

    def test_shoot_update(self):
        player, _, _, _ = create_player(Team.BLUE, self.hcriat)
        player, shoot_handler = shoot_action(player.get_uid(), 'n', self.hcriat, None, None)
        before_y = shoot_handler.bala.y
        shoot_handler.loop()
        self.assertEqual(before_y - 1, shoot_handler.bala.y)

    def test_shoot_hit_wall(self):
        player, _, _, _ = create_player(Team.BLUE, self.hcriat)
        player, shoot_handler = shoot_action(player.get_uid(), 'o', self.hcriat, None, None)
        for i in range(3):
            self.assertTrue(shoot_handler.update())
        self.assertFalse(shoot_handler.update())

    def test_shoot_friend(self):
        player1, _, _, pw_map = create_player(Team.BLUE, self.hcriat)
        player2, _, _, pw_map = create_player(Team.BLUE, self.hcriat)
        pw_map.move_player(player2, player1.x+2, player1.y)
        player, shoot_handler = shoot_action(player1.get_uid(), 'e', self.hcriat, None, None)
        for i in range(3):
            self.assertTrue(shoot_handler.update())

    def test_shoot_enemy(self):
        player1, _, _, pw_map = create_player(Team.BLUE, self.hcriat)
        player2, _, _, pw_map = create_player(Team.RED, self.hcriat)
        pw_map.move_player(player2, player1.x+2, player1.y)
        player, shoot_handler = shoot_action(player1.get_uid(), 'e', self.hcriat, callback, None)
        healt_before = player2.vida
        self.assertTrue(shoot_handler.update())  # move 1 sqm
        self.assertFalse(shoot_handler.update())  # hit the enemy
        self.assertLess(player2.vida, healt_before)

    def test_cant_shoot_exception(self):
        player1, _, _, _ = create_player(Team.BLUE, self.hcriat)
        player1.vivo = False
        self.assertRaises(
            CantShoot, shoot_action, player1.get_uid(), 'e', self.hcriat, callback, None)

    def test_kill_and_revive_enemy(self):
        player1, _, _, pw_map = create_player(Team.BLUE, self.hcriat)
        player2, _, _, pw_map = create_player(Team.RED, self.hcriat)
        pw_map.move_player(player2, player1.x+1, player1.y)
        player, shoot_handler = shoot_action(
            player1.get_uid(), 'e', self.hcriat, callback, callback)
        player2.vida = 1
        shoot_handler.loop()
        self.assertFalse(player2.vivo)
        revive_player(player2.uid, self.hcriat)
        self.assertTrue(player2.vivo)
        self.assertEqual(player2.vida, CreaturesHandler.VIDA_MAX)

    def test_score_from_blue(self):
        player1, _, _, pw_map = create_player(Team.BLUE, self.hcriat)
        player2, _, _, pw_map = create_player(Team.RED, self.hcriat)

        def die_callback(uid):
            return increase_score(uid, self.hcriat)

        pw_map.move_player(player2, player1.x+1, player1.y)
        player, shoot_handler = shoot_action(
            player1.get_uid(), 'e', self.hcriat, callback, die_callback)
        player2.vida = 1
        self.assertEqual(self.score.blue_score, 0)
        shoot_handler.loop()
        self.assertEqual(self.score.blue_score, 1)

    def test_score_from_red(self):
        player1, _, _, pw_map = create_player(Team.RED, self.hcriat)
        player2, _, _, pw_map = create_player(Team.BLUE, self.hcriat)

        def die_callback(uid):
            return increase_score(uid, self.hcriat)

        pw_map.move_player(player2, player1.x+1, player1.y)
        player, shoot_handler = shoot_action(
            player1.get_uid(), 'e', self.hcriat, callback, die_callback)
        player2.vida = 1
        self.assertEqual(self.score.red_score, 0)
        shoot_handler.loop()
        self.assertEqual(self.score.red_score, 1)

    def test_restart_round(self):
        # wrong player trying to restart
        self.assertIsNone(restart_round(153, self.hcriat))

        # real case
        player1, _, _, pw_map = create_player(Team.BLUE, self.hcriat)
        player2, _, _, pw_map = create_player(Team.RED, self.hcriat)
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
        new_blue = players.pop(0) if players[0].team == Team.BLUE else players.pop()
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


class TestProtocol(TestCase):

    def setUp(self):
        self.pwp = PWProtocolFactory().buildProtocol('localhost')
        self.hcriat = CreaturesHandler()
        self.hcriat.score = Score()
        self.pwp.hcriat = self.hcriat
        self.pwp.hcriat.pw_map = Mapa("mapa")
        self.tr = NoDelayTransport()
        self.pwp.makeConnection(self.tr)
        self.player = self.pwp.hcriat.create_player(Team.BLUE, 1, 1)

    def tearDown(self):
        """Cancel all the pending calls to avoid problems"""
        pending = reactor.getDelayedCalls()
        for p in pending:
            if p.active():
                p.cancel()

    def test_receive_login(self):
        self.assertEqual(self.pwp.login(1), {'uid': 3})

    def test_receive_move(self):
        # moving a player who doesn't exists
        self.assertRaises(PlayerDoesNotExist, self.pwp.move, 1, 'n')
        # moving an existing player
        self.assertEqual(self.pwp.move(self.player.uid, 's'), OK_RESPONSE)
        # moving a player who can't move
        self.player.block_movement()
        # TODO: create a better response
        self.assertEqual(self.pwp.move(self.player.uid, 'n'), OK_RESPONSE)

    def test_receive_player_shoot(self):
        self.assertEqual(self.pwp.player_shoot(self.player.uid, 'n'), OK_RESPONSE)
        # testing a player who can't shot
        self.player.block_shot()
        # TODO: create a better response
        self.assertEqual(self.pwp.player_shoot(self.player.uid, 'n'), OK_RESPONSE)

    def test_restart_round(self):
        self.assertEqual(self.pwp.restart_round(self.player.uid), OK_RESPONSE)

    def test_hit(self):
        self.assertIsNone(self.pwp.hit(self.player.uid, 10))  # TODO: check what the client receive

    def test_die(self):
        self.assertIsNone(self.pwp.die(self.player.uid))  # TODO: check what the client receive

    def test_connection_lost(self):
        self.assertEqual(self.pwp.login(1), {'uid': 3})
        self.assertEqual(len(self.hcriat.jugadores), 2)
        self.pwp.connectionLost('test')
        self.assertEqual(len(self.hcriat.jugadores), 1)

    def test_add_bot(self):
        self.assertEqual(len(self.pwp.factory.bots[Team.BLUE]), 0)
        self.pwp.add_bot(Team.BLUE)
        self.assertEqual(len(self.pwp.factory.bots[Team.BLUE]), 1)

    def test_delete_bot(self):
        self.pwp.add_bot(Team.BLUE)
        self.pwp.delete_bot(Team.BLUE)
        self.assertEqual(len(self.pwp.factory.bots[Team.BLUE]), 0)

    def test_delete_non_existent_bot(self):
        self.pwp.delete_bot(Team.BLUE)
        self.assertEqual(len(self.pwp.factory.bots[Team.BLUE]), 0)
