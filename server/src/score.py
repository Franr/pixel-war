class Score(object):

    def __init__(self):
        self.blue_score = 0
        self.red_score = 0

    def restart(self):
        self.blue_score = 0
        self.red_score = 0

    def murio_rojo(self):
        self.blue_score += 1

    def murio_azul(self):
        self.red_score += 1

    def get_data(self):
        return self.blue_score, self.red_score
