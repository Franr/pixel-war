class MapLogic(object):

    def __init__(self, array_map):
        self.dicMap = {}
        # calculating the map dimensions
        self.y = len(array_map)
        self.x = len(array_map[0])
        # generate the map structure
        self._pre_generate_surf()
        for i in range(len(array_map)):
            for e in range(len(array_map[i])):
                obj_id = int(array_map[i][e])
                sqm = 'b' if obj_id else 'n'
                self.dicMap[i, e] = (sqm, obj_id)
                self._render_sqm(e, i, sqm)
        self._post_generate_surf()

    def _pre_generate_surf(self):
        pass

    def _render_sqm(self, x, y, sqm_type):
        pass

    def _post_generate_surf(self):
        pass

    def is_blocking_position(self, x, y):
        return self.dicMap[y, x][0] == "b"

    def move_creature(self, creature, x, y):
        x_ant, y_ant = creature.get_coor()
        self.set_creature(creature, x, y)
        self.clean_position(x_ant, y_ant)

    def set_creature(self, creature, x, y):
        self.dicMap[y, x] = ("b", creature)

    def clean_position(self, x, y):
        self.dicMap[y, x] = ("n", 0)

    def get_creature(self, x, y):
        if self.dicMap[y, x][0] == "n":
            return None
        elif self.dicMap[y, x][0] == "b":
            if isinstance(self.dicMap[y, x][1], int):
                return None
            else:
                return self.dicMap[y, x][1]
