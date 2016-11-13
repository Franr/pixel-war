import pygame


class KeyboardHandler(object):

    def __init__(self, game):
        self.game = game
        self.enabled = False

    def activar(self):
        self.enabled = True

    def update(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_ESCAPE]:
            return False
        if not self.enabled:
            return True

        if pressed[pygame.K_UP]:
            self.game.conexion.cf.protocol.move('n')
        elif pressed[pygame.K_DOWN]:
            self.game.conexion.cf.protocol.move('s')
        elif pressed[pygame.K_LEFT]:
            self.game.conexion.cf.protocol.move('o')
        elif pressed[pygame.K_RIGHT]:
            self.game.conexion.cf.protocol.move('e')
        elif pressed[pygame.K_F1]:
            self.game.conexion.cf.protocol.restart_round()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pressed = event.key
                if pressed == pygame.K_F2:
                    self.game.conexion.cf.protocol.add_bot(1)
                elif pressed == pygame.K_F3:
                    self.game.conexion.cf.protocol.delete_bot(1)
                elif pressed == pygame.K_F4:
                    self.game.conexion.cf.protocol.add_bot(2)
                elif pressed == pygame.K_F5:
                    self.game.conexion.cf.protocol.delete_bot(2)

        return True
