import pygame
import pygame_emojis
import os

if "A6_PRINTER" in os.environ:
    print("Found a printer address!")
    import ppa6
    import PIL
    import PIL.Image
    printer_mac = os.environ["A6_PRINTER"]


class BadgeCreator:
    def __init__(
            self,
            font_size=63,
            badge_size=(4450, 2380),
            emoji_size=(640, 640),
            hello_bar_color=pygame.color.Color('firebrick'),
            hello_text_color=pygame.color.Color('white'),
            hello_bar_end=780,
            name_bar_color=pygame.color.Color('white'),
            name_text_color=pygame.color.Color('firebrick'),
            bottom_bar_color=pygame.color.Color('firebrick'),
            bottom_bar_start=2100,
    ):
        self.font_size = font_size
        self.badge_size = badge_size
        self.emoji_size = emoji_size
        self.hello_bar_color = hello_bar_color
        self.hello_text_color = hello_text_color
        self.hello_bar_end = hello_bar_end
        self.name_bar_color = name_bar_color
        self.name_text_color = name_text_color
        self.bottom_bar_color = bottom_bar_color
        self.bottom_bar_start = bottom_bar_start
        self.fallback_font = pygame.font.SysFont(pygame.font.get_default_font(), self.font_size)
        self.width, self.height = self.badge_size
        self.emoji_width, self.emoji_height = self.emoji_size
        self.printer = None

    def create(self, name, image_or_emoji, font_name=None, hello_text="Hello, my name is"):
        pygame.font.init()
        print(f"font: {font_name}")
        font = pygame.font.SysFont(font_name, self.font_size)

        hello_bar = (0, 0, self.width, self.hello_bar_end)
        name_bar = (0, self.hello_bar_end, self.width, self.bottom_bar_start)
        bottom_bar = (0, self.bottom_bar_start, self.width, self.height)
        emoji_bar = (
            self.width / 2 - self.emoji_width / 2,
            self.height - self.emoji_height,
            self.width / 2 + self.emoji_width / 2,
            self.height
        )

        badge_surface = pygame.surface.Surface(self.badge_size)

        # draw backgrounds
        badge_surface.fill(self.hello_bar_color, hello_bar)
        badge_surface.fill(self.name_bar_color, name_bar)
        badge_surface.fill(self.bottom_bar_color, bottom_bar)

        self.draw_centered_text(hello_text, self.hello_text_color, self.hello_bar_color, font, badge_surface, hello_bar)
        self.draw_centered_text(name, self.name_text_color, self.name_bar_color, font, badge_surface, name_bar)
        self.draw_centered_image(image_or_emoji, badge_surface, emoji_bar)

        return badge_surface

    def print(self, badge):
        if printer_mac:
            try:
                pygame.image.save(badge, "/tmp/badge.png")
                image = PIL.Image.open("/tmp/badge.png")
                rotated = image.rotate(90, expand=True)
                
                if not self.printer:
                    print("new printer found")
                    self.printer = ppa6.Printer(printer_mac)
                
                if not self.printer.isConnected():
                    print("connecting to printer")
                    self.printer.connect()
                
                self.printer.printImage(rotated)
                self.printer.printBreak(64)

                print(f"batery left: {self.printer.getDeviceBattery():03d}%")
            except bluetooth.btcommon.BluetoothError:
                print("Bluetooth error, please try again")


    def draw_centered_text(self, text, text_color, background_color, font, target, target_rect):
        target_width = (target_rect[2] - target_rect[0]) * 0.9
        target_height = (target_rect[3] - target_rect[1]) * 0.8
        target_offset_x = target_rect[0] + 0.05 * target_width
        target_offset_y = target_rect[1] + 0.1 * target_height

        try:
            text_surface = font.render(text, True, text_color, background_color)
        except pygame.error:
            text_surface = self.fallback_font.render(text, True, text_color, background_color)

        text_width, text_height = text_surface.get_size()

        text_base_surface = pygame.surface.Surface((text_width, text_height))
        text_base_surface.fill(background_color)
        text_base_surface.blit(text_surface, (0, 0))

        if text_width > text_height:
            factor = target_width / float(text_width)

            if text_height * factor > target_height:
                factor = target_height / float(text_height)
        else:
            factor = target_height / float(text_height)

            if text_width * factor > target_width:
                factor = target_width / float(text_width)

        scaled_size = (text_width * factor, text_height * factor)
        scaled_surface = pygame.surface.Surface(scaled_size)
        scaled_surface.blit(text_surface, (0, 0))
        pygame.transform.scale(text_base_surface, scaled_size, scaled_surface)

        dest = (target_offset_x + target_width / 2.0 - scaled_size[0] / 2.0,
                target_offset_y + target_height / 2.0 - scaled_size[1] / 2.0)
        target.blit(scaled_surface, dest=dest)

    def draw_centered_image(self, image, target, target_rect):
        target_width = target_rect[2] - target_rect[0]
        target_height = target_rect[3] - target_rect[1]

        if image.isascii():
            text_surface = pygame.image.load(image)
            text_surface = pygame.transform.scale(text_surface, (target_width, target_height))
            target.blit(text_surface, dest=target_rect)
        else:
            emoji = pygame_emojis.load_emoji(image, (target_width, target_height))
            emoji_base = pygame.surface.Surface(self.emoji_size, emoji.get_flags())
            emoji_base.fill((255, 255, 255, 255),
                            (target_rect[0], target_rect[1], target_rect[2], target_rect[3] / 2.0))

            pygame.draw.circle(emoji_base, (255, 255, 255, 255), (self.emoji_width / 2, self.emoji_height / 2),
                               self.emoji_height / 2)

            emoji_base.blit(emoji, (0, 0))
            target.blit(emoji_base, dest=target_rect)
