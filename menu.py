import pygame
import pygame_emojis
import subprocess
import math
import sys
import os

from badge import BadgeCreator


def words_in_emoji_table(words, emoji_key):
    for word in words:
        data = pygame_emojis.emoji.EMOJI_DATA
        emoji = data[emoji_key]
        if emoji['en'].lower().find(word) != -1:
            return True
        elif 'alias' in emoji:
            if len(list(filter(lambda alias: alias.lower().find(word) != -1, emoji['alias']))) > 0:
                return True


def create_emojis(words=None):
    if words is None:
        words = ['smile', 'cat']

    return list(
        filter(
            lambda x:
            words_in_emoji_table(words, x),
            pygame_emojis.emoji.EMOJI_DATA
        )
    )


def term_color(r, g, b):
    r = round(max(0.0, min(5.0, r * 6.0)))
    g = round(max(0.0, min(5.0, g * 6.0)))
    b = round(max(0.0, min(5.0, b * 6.0)))

    return int(16 + r + g * 6 + b * 6 * 6)


def hsv(index, length):
    # rainbow
    bucket_size = length / 6.0
    index_in_bucket = index / bucket_size - math.floor(index / bucket_size)

    # r1, g+, b0
    if index < bucket_size:
        r = 1.0
        g = index_in_bucket
        b = 0.0

    # r-, g1, b0
    elif index < 2 * bucket_size:
        r = 1.0 - index_in_bucket
        g = 1.0
        b = 0.0

    # r0, g1, b+
    elif index < 3 * bucket_size:
        r = 0.0
        g = 1.0
        b = index_in_bucket

    # r0, g-, b1
    elif index < 4 * bucket_size:
        r = 0.0
        g = 1.0 - index_in_bucket
        b = 1.0

    # r+, g0, b1
    elif index < 5 * bucket_size:
        r = index_in_bucket
        g = 0.0
        b = 1.0

    # r+, g0, b-
    else:  # index < 6 * bucket_size
        r = 1.0
        g = 0.0
        b = 1.0 - index_in_bucket

    return term_color(r, g, b)


def rainbowify(message, background=False):
    if background:
        layer_code = f"38;5;0;1m{color_escape_sequence}48"
    else:
        layer_code = "38"

    message = f"  {message}  "

    return "".join(
        list(
            map(
                lambda a:
                f"{color_escape_sequence}{layer_code};5;{hsv(a[0], len(message))}m{a[1]}",
                enumerate(message)
            )
        )
    ) + color_end_sequence


def render_font_previews(basename):
    pygame.font.init()
    creator = BadgeCreator()

    fonts = pygame.font.get_fonts()
    font_count = len(pygame.font.get_fonts())
    for index, selected_font in enumerate(fonts):
        print(f"{index} / {font_count}: {selected_font}")
        badge = creator.create(
            name=f"{selected_font} Fairy",
            image_or_emoji="😻",
            font_name=selected_font
        )

        pygame.image.save(badge, f"{basename}{selected_font}.png")


def prompt(message="", persona="badgey", newline=True, rainbow=False):
    if newline:
        end = "\n"
    else:
        end = ""

    if rainbow:
        user_prompt = f"{rainbowify(persona.upper())}: {rainbowify(message, True)}"
    else:
        user_prompt = f"{persona.upper()}: {message}"

    print(user_prompt, end=end)


color_escape_sequence = "\033["
color_end_sequence = f"{color_escape_sequence}m"


class Menu:
    def __init__(self):
        self.emoji_list = create_emojis()
        self.font_name = None
        self.event_name = None

        self.options = {
            'start': self.user_start,
            'exit': self.user_exit,
            'save': self.save_configuration,
            'load': self.load_configuration,
            'list fonts': self.user_list_fonts,
            'search fonts': self.user_search_fonts,
            'set event': self.user_set_event_name,
            'set font': self.user_set_font,
            'set emojis': self.user_set_emojis,
            'render previews': self.user_preview,
            'help': self.user_help,
            'debug': self.user_debug,
        }

    def menu(self):
        prompt()
        prompt("Hello, what do you want do?", rainbow=True)

        prompt("", "you", False)
        selection = input()

        end_this = False

        if selection in self.options:
            end_this = self.options[selection]()
            prompt("", "")
        else:
            self.user_help()
            prompt("", "")

        if not end_this:
            self.menu()

    def user_preview(self):
        basename = f"previews/{sys.platform}"
        os.makedirs(basename, exist_ok=True)
        render_font_previews(f"{basename}/badge")
        prompt(f"done previewing on {sys.platform}.")
        return False

    def user_list_fonts(self):
        pygame.font.init()
        fonts = pygame.font.get_fonts()
        fonts_per_page = 20
        for page in range(0, len(fonts), fonts_per_page):
            for font_index in range(page, min(len(fonts), page + fonts_per_page)):
                prompt(fonts[font_index], f"font {font_index}")

            prompt("More?")
            c = input()
            if c == "y":
                continue
            else:
                break

        return False

    def user_search_fonts(self):
        pygame.font.init()
        fonts = pygame.font.get_fonts()
        prompt("What are you looking for?")
        prompt("", "you", False)
        what = input()

        filtered = list(filter(lambda x: x.find(what) >= 0, fonts))

        for f in filtered:
            prompt(f"I found font '{f}'.")

        return False

    def user_set_font(self):
        prompt("What font do you want?")
        prompt("", "you", False)
        self.font_name = input()

    def user_set_event_name(self):
        prompt("What event is this?")
        prompt("", "you", False)
        self.event_name = input()

    def user_help(self):
        prompt("Welcome to the interactive badge creation utility.", rainbow=True)
        prompt("My name is badgey and I am here to help you type things")
        prompt("and getting things done.")
        prompt("I am not an ai, I'm just a prompt.")
        prompt("You have the following options of verbs I can understand")
        for option in self.options:
            prompt(option)
        return False

    def user_start(self):
        if not pygame.font.get_init():
            pygame.font.init()

        prompt("Starting the badge creation for the event ...", rainbow=True)
        creator = BadgeCreator()

        event_over = False
        while not event_over:
            prompt(f"Hey attendee of {self.event_name}, how should we call you?", rainbow=True)
            prompt("", "you", False)
            name = input()

            while len(name) < 4:
                prompt("Please use more then 4 letters.", rainbow=True)
                prompt("", "you", False)
                name = input()

            if name.lower() == "exit":
                event_over = True
                continue

            prompt(f"Thank you, {name}.")
            prompt(f"What is your favorite number from '0' to '{len(self.emoji_list)}'?")
            prompt("", "you", False)
            number = input()

            try:
                number = int(number)
            except ValueError:
                number = 42

            prompt(f"Creating your badge ...")
            try:
                emoji = self.emoji_list[number]
            except IndexError:
                emoji = self.emoji_list[0]

            badge = creator.create(name=name, image_or_emoji=emoji, font_name=self.font_name)
            badge_file_name = "attendee-badge.png"
            pygame.image.save(badge, badge_file_name)

            subprocess.call(('chafa', badge_file_name))

            creator.print(badge)

            prompt(f"Done, enjoy {self.event_name}.")

        return False

    def user_set_emojis(self):
        prompt(f"What emojis do you want to look for? (coma separated)")
        prompt("", "you", False)
        words = input().split(",")

        self.emoji_list = create_emojis(words)
        print(self.emoji_list)

        return False

    def user_exit(self):
        prompt("k, thx, bye.", rainbow=True)
        return True

    def user_debug(self):
        print("term colors")
        for r in range(6):
            for g in range(6):
                for b in range(6):
                    index = term_color(r / 6, g / 6, b / 6)
                    print(f"\033[38;5;{index}m{index:03d} ", end='')
            print()

        print("configuration")
        print(f"event = {self.event_name}")
        print(f"font = {self.font_name}")
        print(f"emojis = {','.join(self.emoji_list)}")

        return False

    def save_configuration(self):
        config = open(".configuration", "w")
        config.write(f"emojis={','.join(self.emoji_list)}")
        config.write('\n')
        config.write(f"font={self.font_name}")
        config.write('\n')
        config.write(f"event={self.event_name}")
        config.write('\n')
        config.close()

        return False

    def load_configuration(self):
        config = open(".configuration", "r")

        for line in config.readlines():
            key, value = line.split("=")
            value = value.replace('\n', '')
            if key == "emojis":
                self.emoji_list = value.split(",")
            elif key == "font":
                self.font_name = value
            elif key == "event":
                self.event_name = value
            else:
                print(f"Configuration key '{key}' not understood.")

        config.close()

        return False
