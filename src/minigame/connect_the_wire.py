import pygame as pg
import random
from .minigame_manager import MiniGame


class ConnectTheWireMiniGame(MiniGame):
    def __init__(self, size):
        super().__init__(size)

        self.left_nodes = []
        self.right_nodes = []
        self.wires = []  # conexões feitas
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 100, 255), (255, 255, 0)]

        # setup de posições
        margin = 50
        spacing = (self.height - 2 * margin) // len(self.colors)

        # Criar nós da esquerda
        for i, color in enumerate(self.colors):
            y = margin + i * spacing + spacing // 2
            self.left_nodes.append({"pos": (60, y), "color": color, "connected": False})

        # Embaralhar cores da direita
        shuffled = self.colors[:]
        random.shuffle(shuffled)

        for i, color in enumerate(shuffled):
            y = margin + i * spacing + spacing // 2
            self.right_nodes.append({"pos": (self.width - 60, y), "color": color, "connected": False})

        self.dragging = False
        self.current_wire = None
        self.mouse_pos = (0, 0)

    def handle_event(self, event, keys):
        super().handle_event(event, keys)

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pg.mouse.get_pos()
            rel_x = mx - (pg.display.get_surface().get_width() - self.width) // 2
            rel_y = my - (pg.display.get_surface().get_height() - self.height) // 2
            self.mouse_pos = (rel_x, rel_y)

            # Verifica se começou num ponto da esquerda
            for i, node in enumerate(self.left_nodes):
                if not node["connected"]:
                    if pg.Vector2(node["pos"]).distance_to(self.mouse_pos) < 15:
                        self.dragging = True
                        self.current_wire = {"index": i, "from": node["pos"], "to": self.mouse_pos}
                        break

        elif event.type == pg.MOUSEMOTION:
            if self.dragging and self.current_wire:
                mx, my = pg.mouse.get_pos()
                rel_x = mx - (pg.display.get_surface().get_width() - self.width) // 2
                rel_y = my - (pg.display.get_surface().get_height() - self.height) // 2
                self.mouse_pos = (rel_x, rel_y)
                self.current_wire["to"] = self.mouse_pos

        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.dragging and self.current_wire:
                target_color = self.colors[self.current_wire["index"]]
                for node in self.right_nodes:
                    if node["color"] == target_color and not node["connected"]:
                        if pg.Vector2(node["pos"]).distance_to(self.mouse_pos) < 15:
                            # Conexão correta
                            self.left_nodes[self.current_wire["index"]]["connected"] = True
                            node["connected"] = True
                            self.wires.append({
                                "color": target_color,
                                "from": self.current_wire["from"],
                                "to": node["pos"]
                            })
                            if len(self.wires) == len(self.colors):
                                self.finished = True
                            break
                self.dragging = False
                self.current_wire = None

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((30, 30, 30))

        # Desenhar linhas já conectadas
        for wire in self.wires:
            pg.draw.line(surface, wire["color"], wire["from"], wire["to"], 5)

        # Desenhar a linha sendo arrastada
        if self.dragging and self.current_wire:
            pg.draw.line(surface, self.colors[self.current_wire["index"]],
                         self.current_wire["from"], self.current_wire["to"], 3)

        # Desenhar nós (esquerda e direita)
        for node in self.left_nodes + self.right_nodes:
            color = node["color"]
            radius = 10
            pg.draw.circle(surface, color, node["pos"], radius)
            if node["connected"]:
                pg.draw.circle(surface, (255, 255, 255), node["pos"], radius + 2, 2)
