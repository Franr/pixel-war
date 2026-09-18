import logging
from types import MappingProxyType

from rich.text import Text
from shared.constants import Team
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, RichLog

from src.game import GameHandler
from src.logger import logger


class MatrixWidget(Widget):
    """Renders a 2D matrix where each cell color depends on its value."""

    QUADRANTS = MappingProxyType({
        (True, True, True, True): "\u2588", # Full Block
        (True, False, False, False): "\u2598", # Quadrant Upper Left
        (False, True, False, False): "\u259D",  # Quadrant Upper Right
        (True, True, False, False): "\u2580", # Upper Half Block
        (False, False, True, False): "\u2596", # Quadrant Lower Left
        (False, False, False, True): "\u2597", # Quadrant Lower Right
        (False, False, True, True): "\u2584", # Lower Half Block
        (True, False, True, False): "\u258C", # Left Half Block
        (False, True, False, True): "\u2590", # Right Half Block
        (True, False, False, True): "\u259A", # Quadrant Upper Left and Lower Right
        (False, True, True, False): "\u259E" # EQuadrant Upper Right and Lower Left
    })

    BACKGROUND = "white"
    FOREGROUND = "blue"
    STYLE = f"{FOREGROUND} on {BACKGROUND}"
    STYLE_FLIPPED = f"{BACKGROUND} on {FOREGROUND}"

    def __init__(self, map: list[list[int]], **kwargs):
        super().__init__(**kwargs)
        self.map = map

    def quadrant_to_char(self, tr, tl, br, bl) -> tuple[str, str]:
        values = tr > 0, tl > 0, br > 0, bl > 0
        # if not present, then flip values and color
        try:
            return self.QUADRANTS[values], self.STYLE
        except KeyError:
            return self.QUADRANTS[tr < 1, tl < 1, br < 1, bl < 1], self.STYLE_FLIPPED

    def on_mount(self) -> None:
        # Schedule self.refresh() to run automatically every N seconds
        self.set_interval(1, self.refresh)

    def render(self) -> Text:
        output = Text()

        # each character is the compound of 4 cells, so we need to iterate half each axies
        for row_idx, row in enumerate(self.map):
            if row_idx % 2: continue

            for val_idx, val in enumerate(row):
                if val_idx % 2: continue

                # Appending two spaces per cell makes the cells roughly square in terminals
                quadrant, style = self.quadrant_to_char(
                    self.map[row_idx][val_idx],
                    self.map[row_idx][val_idx+1],
                    self.map[row_idx+1][val_idx],
                    self.map[row_idx+1][val_idx+1]
                )
                output.append(quadrant, style)

            # Add newline between matrix rows (except the last line)
            if row_idx < len(self.map) - 1:
                output.append("\n")

        return output


# Custom logging handler that redirects standard logging to a Textual widget
class TextualLogHandler(logging.Handler):
    def __init__(self, log_widget: RichLog):
        super().__init__()
        self.log_widget = log_widget

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        self.log_widget.write(msg)


class Tui(App):
    CSS = """
    MatrixWidget {
        width: auto;
        height: auto;
    }
    Screen {
        layout: grid;
        grid-size: 3 3;
        grid-rows: 1fr;
        grid-columns: 1fr;
    }
    .box {
        height: 100%;
        width: 1fr;
    }
    #log_view {
        row-span: 2;
        column-span: 3;
    }
    """

    TITLE = "Pixel-War Server"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield RichLog(id="log_view", highlight=True, classes="box")
        with Vertical(classes="box"):
            yield Button(id="restart_button", label="Restart Round")
            yield Button(id="remove_all", label="Remove all bots")
        with Vertical(classes="box"):
            yield Button(id="add_bot_blue", label="Add bot: blue")
            yield Button(id="add_bot_red", label="Add bot: red")
            yield Button(id="remove_bot_blue", label="Remove bot: blue")
            yield Button(id="remove_bot_red", label="Remove bot: red")
        yield MatrixWidget(self.gh.pw_map.array_map, classes="box")
        yield Footer()

    def on_mount(self) -> None:
        log_widget = self.query_one("#log_view", RichLog)
        # Attach custom handler to our logger
        handler = TextualLogHandler(log_widget)
        logger.addHandler(handler)

    @on(Button.Pressed, "#restart_button")
    def pressed_restart_button(self, event: Button.Pressed) -> None:
        """Pressed the restart button."""
        self.gh.restart_round()

    @on(Button.Pressed, "#add_bot_blue")
    def pressed_add_blue(self, event: Button.Pressed) -> None:
        """Pressed the restart button."""
        self.gh.add_bot(Team.BLUE)

    @on(Button.Pressed, "#add_bot_red")
    def pressed_add_red(self, event: Button.Pressed) -> None:
        """Pressed the restart button."""
        self.gh.add_bot(Team.RED)

    @on(Button.Pressed, "#remove_bot_blue")
    def pressed_remove_blue(self, event: Button.Pressed) -> None:
        """Pressed the restart button."""
        self.gh.remove_bot(Team.BLUE)

    @on(Button.Pressed, "#remove_bot_red")
    def pressed_remove_red(self, event: Button.Pressed) -> None:
        """Pressed the restart button."""
        self.gh.remove_bot(Team.RED)

    @on(Button.Pressed, "#remove_all")
    def pressed_remove_all(self, event: Button.Pressed) -> None:
        """Pressed the restart button."""
        self.gh.remove_all_bots()

    def __init__(self, gh: GameHandler, **kwargs):
        super().__init__(**kwargs)
        self.gh = gh
