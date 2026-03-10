import toga
import threading
import asyncio
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

class StatusDisplay():
    def __init__(self):
        self.status_box = self.setBox()
        self._clear_timer = None
        try:
            # Prefer the running loop if available (the UI loop).
            self._main_loop = asyncio.get_running_loop()
        except RuntimeError:
            try:
                # Fall back to the default event loop if present.
                self._main_loop = asyncio.get_event_loop()
            except Exception:
                self._main_loop = None

    def setBox(self):
        box = toga.Box(style=Pack(direction=COLUMN, alignment='center', justify_content='center', align_items='center'))
        self.label = toga.Label("Willkommen zu Tic Tac Toe!", style=Pack(margin=5, font_size=14, alignment='center'))
        box.add(self.label)
        return box
    
    def update_status(self, message: str, duration: float = 2.0):
        self.label.text = message
        # If a previous clear handle/timer exists, cancel it so messages don't race.
        if self._clear_timer is not None:
            try:
                self._clear_timer.cancel()
            except Exception:
                pass
            self._clear_timer = None

        if duration > 0:
            # Prefer scheduling on the main asyncio event loop so the UI update
            # runs on the correct thread. `call_later` returns a handle with
            # `cancel()`.
            if self._main_loop is not None:
                try:
                    self._clear_timer = self._main_loop.call_later(duration, self.clear_status)
                except Exception:
                    # If scheduling fails for some reason, fall back to a background timer.
                    def _safe_clear():
                        try:
                            self.clear_status()
                        except Exception:
                            pass
                    self._clear_timer = threading.Timer(duration, _safe_clear)
                    self._clear_timer.start()
            else:
                # No event loop known: fall back to a background timer (best-effort).
                def _safe_clear():
                    try:
                        self.clear_status()
                    except Exception:
                        pass
                self._clear_timer = threading.Timer(duration, _safe_clear)
                self._clear_timer.start()

    def clear_status(self):
            self.label.text = ""
            
    def game_has_ended(self, result: int):
        if result == 1:
            self.update_status("Spiel beendet: Spieler X hat gewonnen!", duration=0)
        elif result == -1:
            self.update_status("Spiel beendet: Spieler O hat gewonnen!", duration=0)
        elif result == 0:
            self.update_status("Spiel beendet: Unentschieden!", duration=0)
        else:
            self.update_status("Spiel beendet!", duration=0)
        