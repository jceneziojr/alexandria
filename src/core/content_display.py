import pygame as pg
from typing import Union, List
from .configs import WINDOW_WIDTH, WINDOW_HEIGHT, GFX
from .contents import CONTENT_MAP


class ContentDisplay:
    def __init__(self, frame_rect: pg.Rect, image: Union[pg.Surface, List[pg.Surface]], scale_option: Union[bool, float] = True, fps: int = 10):
        """
        frame_rect: posição/tamanho da moldura
        image: Surface única ou lista de Surfaces (animação)
        scale_option:
            - True  → escala proporcional para caber na moldura (com folga)
            - False → mantém tamanho original
            - float → escala proporcional pelo fator fornecido
        fps: usado apenas se for animação
        """
        self.frame_rect = frame_rect
        self.scale_option = scale_option
        self.active = True

        # Moldura
        self.frame_surface = pg.transform.smoothscale(
            GFX["others"]["background_display"],
            (self.frame_rect.width, self.frame_rect.height)
        ).convert_alpha()

        # Detectar se é estático ou animado
        if isinstance(image, list):
            self.is_animation = True
            self.frames = [self._apply_scale(img) for img in image]
            self.frame_index = 0
            self.time_acc = 0
            self.frame_duration = 1 / fps
        else:
            self.is_animation = False
            self.image = self._apply_scale(image)
            self.image_pos = self._center_pos(self.image)

    def _apply_scale(self, img: pg.Surface):
        if not img:
            return None
        if isinstance(self.scale_option, bool):
            if self.scale_option:  # True → ajustar para caber (95% da moldura)
                return self._scale_to_fit(img, self.frame_rect.width * 0.95, self.frame_rect.height * 0.95)
            else:
                return img
        elif isinstance(self.scale_option, (float, int)):
            return self._scale_by_factor(img, float(self.scale_option))
        return img

    def _scale_to_fit(self, surface, max_w, max_h):
        w, h = surface.get_size()
        scale = min(max_w / w, max_h / h)
        new_size = (int(w * scale), int(h * scale))
        return pg.transform.smoothscale(surface, new_size)

    def _scale_by_factor(self, surface, factor: float):
        w, h = surface.get_size()
        new_size = (int(w * factor), int(h * factor))
        return pg.transform.smoothscale(surface, new_size)

    def _center_pos(self, img):
        img_x = self.frame_rect.x + (self.frame_rect.width - img.get_width()) // 2
        img_y = self.frame_rect.y + (self.frame_rect.height - img.get_height()) // 2
        return img_x, img_y

    def update(self, dt):
        if self.is_animation:
            self.time_acc += dt
            if self.time_acc >= self.frame_duration:
                self.time_acc = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, surface):
        if not self.active:
            return

        surface.blit(self.frame_surface, self.frame_rect.topleft)

        if self.is_animation:
            img = self.frames[self.frame_index]
            surface.blit(img, self._center_pos(img))
        else:
            if self.image:
                surface.blit(self.image, self.image_pos)


class ContentDisplayManager:
    def __init__(self, player):
        self.active = False
        self.display: Union[ContentDisplay, None] = None
        self.player = player

        self.rect = pg.Rect(0, 0, int(WINDOW_WIDTH * 0.8), int(WINDOW_HEIGHT * 0.6))
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 25)

    def start_for_dialog(self, speaker, phase, dialog_line):
        if speaker in CONTENT_MAP:
            if phase in CONTENT_MAP[speaker]:
                if dialog_line in CONTENT_MAP[speaker][phase]:
                    entry = CONTENT_MAP[speaker][phase][dialog_line]
                    img = entry.get("image")
                    scale_option = entry.get("scale", True)
                    fps = entry.get("fps", 10)

                    self.display = ContentDisplay(self.rect, image=img, scale_option=scale_option, fps=fps)
                    self.active = True
                    return
        self.active = False
        self.display = None

    def end(self):
        self.active = False
        self.display = None

    def update(self, dt):
        if self.active and self.display:
            self.display.update(dt)

    def draw(self, surface):
        if self.active and self.display:
            self.display.draw(surface)
