from ..core.configs import levels


class GlobalController:
    def __init__(self):
        self.levels_handler = {}
        for i, map_name in enumerate(levels):
            self.levels_handler[map_name] = i + 1
        self.current_phase_number = 1

    def set_current_phase_number(self, level_name, override=None):
        if override == None:
            self.current_phase_number += 1
        else:
            self.current_phase_number = override
