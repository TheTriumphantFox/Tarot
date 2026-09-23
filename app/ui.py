from __future__ import annotations

import math
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import messagebox, ttk

from .interpretation import format_spread_reading, format_spread_speech
from .models import ControlState, ReadingResult
from .session import SignalSession
from .speech import SpeechService
from .spreads import SPREADS, SPREADS_BY_LABEL, SpreadDefinition


BG = "#0b0e12"
PANEL = "#11161c"
PANEL_ALT = "#0e1318"
BRASS = "#b99355"
BRASS_DIM = "#67543a"
IVORY = "#e8dfc7"
MUTED = "#8d918e"
AMBER = "#d9a441"
GREEN = "#7b9b78"
RED = "#9b5f58"
TRACK = "#252c31"

INTRO_TEXT = (
    "HOW TO USE THE INSTRUMENT\n\n"
    "1. Choose how long to listen with the Measurement Window dial.\n"
    "2. Before the first reading, turn any dial or throw a lever to awaken the signal.\n"
    "3. Choose a draw pattern and select Draw Cards.\n"
    "4. Concentrate on your question. You may continue tuning the live controls while "
    "the instrument listens.\n\n"
    "THE ENTROPY ENGINE\n\n"
    "Throughout the measurement window, the instrument gathers a rapid series of "
    "changing signals from your settings, the path and timing of your movements, and "
    "fresh uncertainty supplied by Windows. Each moment is sealed separately, then all "
    "of them are fused into one final signal that determines the cards.\n\n"
    "After a reading, draw again with the same settings or retune the instrument first."
)


class Dial(ttk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        *,
        label: str,
        minimum: int,
        maximum: int,
        value: int,
        scale: float,
        command: Callable[[int, str], None],
        choices: tuple[int, ...] | None = None,
        value_suffix: str = "",
    ) -> None:
        super().__init__(parent, style="Panel.TFrame")
        self.minimum = minimum
        self.maximum = maximum
        self.choices = choices
        if choices is not None:
            if len(choices) < 2 or tuple(sorted(set(choices))) != choices:
                raise ValueError("Dial choices must be unique and increasing.")
            if value not in choices:
                raise ValueError("The initial dial value must be one of its choices.")
            self.minimum = choices[0]
            self.maximum = choices[-1]
        self.value = value
        self._value_suffix = value_suffix
        self._scale = scale
        self._command = command
        self._enabled = True
        self._last_drag_value = value

        ttk.Label(self, text=label, style="ControlTitle.TLabel").pack(pady=(0, 3))
        size = self._px(122)
        self.canvas = tk.Canvas(
            self,
            width=size,
            height=size,
            background=PANEL,
            highlightthickness=self._px(1),
            highlightbackground=BRASS_DIM,
            highlightcolor=AMBER,
            takefocus=True,
            cursor="hand2",
        )
        self.canvas.pack()
        self.value_label = ttk.Label(self, style="Readout.TLabel", anchor="center")
        self.value_label.pack(fill="x", pady=(4, 0))

        self.canvas.bind("<Button-1>", self._pointer_event)
        self.canvas.bind("<B1-Motion>", self._pointer_event)
        self.canvas.bind("<MouseWheel>", self._wheel_event)
        self.canvas.bind("<Left>", lambda event: self._step(-1))
        self.canvas.bind("<Down>", lambda event: self._step(-1))
        self.canvas.bind("<Right>", lambda event: self._step(1))
        self.canvas.bind("<Up>", lambda event: self._step(1))
        self.canvas.bind("<Home>", lambda event: self.set_value(self.minimum, notify=True))
        self.canvas.bind("<End>", lambda event: self.set_value(self.maximum, notify=True))
        self._draw()

    def _px(self, value: float) -> int:
        return max(1, round(value * self._scale))

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self.canvas.configure(cursor="hand2" if enabled else "arrow")
        self._draw()

    def set_value(self, value: int, *, notify: bool = False) -> None:
        value = int(value)
        if self.choices is not None:
            value = min(self.choices, key=lambda choice: abs(choice - value))
        else:
            value = max(self.minimum, min(self.maximum, value))
        if value == self.value:
            return
        old = self.value
        self.value = value
        self._draw()
        if notify:
            self._command(value, "up" if value > old else "down")

    def _step(self, amount: int) -> str:
        if self._enabled:
            if self.choices is None:
                next_value = self.value + amount
            else:
                index = self.choices.index(self.value)
                next_index = max(0, min(len(self.choices) - 1, index + amount))
                next_value = self.choices[next_index]
            self.set_value(next_value, notify=True)
        return "break"

    def _wheel_event(self, event: tk.Event) -> str:
        if self._enabled:
            step = 1 if event.delta > 0 else -1
            self._step(step)
        return "break"

    def _pointer_event(self, event: tk.Event) -> str:
        if not self._enabled:
            return "break"
        self.canvas.focus_set()
        size = int(self.canvas.cget("width"))
        center = size / 2
        degrees = math.degrees(math.atan2(center - event.y, event.x - center))
        if degrees < 0:
            degrees += 360
        unwrapped = degrees if degrees <= 225 else degrees - 360
        progress = (225 - unwrapped) / 270
        progress = max(0.0, min(1.0, progress))
        if self.choices is None:
            value = round(self.minimum + progress * (self.maximum - self.minimum))
        else:
            index = round(progress * (len(self.choices) - 1))
            value = self.choices[index]
        self.set_value(value, notify=True)
        self._last_drag_value = value
        return "break"

    def _draw(self) -> None:
        self.canvas.delete("all")
        size = int(self.canvas.cget("width"))
        center = size / 2
        outer = self._px(12)
        radius = center - outer
        active = BRASS if self._enabled else BRASS_DIM
        self.canvas.create_arc(
            outer,
            outer,
            size - outer,
            size - outer,
            start=-45,
            extent=270,
            style="arc",
            width=self._px(3),
            outline=active,
        )
        for index in range(11):
            progress = index / 10
            degrees = 225 - progress * 270
            radians = math.radians(degrees)
            inner_r = radius - self._px(8 if index % 5 else 13)
            outer_r = radius
            x1 = center + inner_r * math.cos(radians)
            y1 = center - inner_r * math.sin(radians)
            x2 = center + outer_r * math.cos(radians)
            y2 = center - outer_r * math.sin(radians)
            self.canvas.create_line(x1, y1, x2, y2, fill=active, width=self._px(1))

        knob_r = radius - self._px(19)
        self.canvas.create_oval(
            center - knob_r,
            center - knob_r,
            center + knob_r,
            center + knob_r,
            fill="#171d22" if self._enabled else "#13171a",
            outline=active,
            width=self._px(2),
        )
        if self.choices is None:
            progress = (self.value - self.minimum) / (self.maximum - self.minimum)
        else:
            progress = self.choices.index(self.value) / (len(self.choices) - 1)
        degrees = 225 - progress * 270
        radians = math.radians(degrees)
        pointer_r = knob_r - self._px(9)
        x = center + pointer_r * math.cos(radians)
        y = center - pointer_r * math.sin(radians)
        self.canvas.create_line(
            center,
            center,
            x,
            y,
            fill=AMBER if self._enabled else BRASS_DIM,
            width=self._px(4),
            capstyle=tk.ROUND,
        )
        self.canvas.create_oval(
            center - self._px(4),
            center - self._px(4),
            center + self._px(4),
            center + self._px(4),
            fill=active,
            outline="",
        )
        self.value_label.configure(text=f"{self.value}{self._value_suffix}")


class Lever(ttk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        *,
        label: str,
        states: tuple[str, str],
        value: int,
        scale: float,
        command: Callable[[str, str], None],
    ) -> None:
        super().__init__(parent, style="Panel.TFrame")
        self.states = states
        self.value = value
        self._scale = scale
        self._command = command
        self._enabled = True

        ttk.Label(self, text=label, style="ControlTitle.TLabel").pack(pady=(0, 3))
        self.canvas = tk.Canvas(
            self,
            width=self._px(112),
            height=self._px(64),
            background=PANEL,
            highlightthickness=self._px(1),
            highlightbackground=BRASS_DIM,
            highlightcolor=AMBER,
            takefocus=True,
            cursor="hand2",
        )
        self.canvas.pack()
        self.state_label = ttk.Label(self, style="Readout.TLabel", anchor="center")
        self.state_label.pack(fill="x", pady=(4, 0))
        self.canvas.bind("<Button-1>", self._toggle)
        self.canvas.bind("<space>", self._toggle)
        self.canvas.bind("<Return>", self._toggle)
        self.canvas.bind("<Left>", lambda event: self.set_value(0, notify=True))
        self.canvas.bind("<Right>", lambda event: self.set_value(1, notify=True))
        self._draw()

    def _px(self, value: float) -> int:
        return max(1, round(value * self._scale))

    @property
    def state(self) -> str:
        return self.states[self.value].lower()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self.canvas.configure(cursor="hand2" if enabled else "arrow")
        self._draw()

    def set_value(self, value: int, *, notify: bool = False) -> str:
        value = 0 if value <= 0 else 1
        if value == self.value:
            return "break"
        old = self.value
        self.value = value
        self._draw()
        if notify:
            self._command(self.state, "right" if value > old else "left")
        return "break"

    def _toggle(self, _event: tk.Event | None = None) -> str:
        if self._enabled:
            self.canvas.focus_set()
            self.set_value(1 - self.value, notify=True)
        return "break"

    def _draw(self) -> None:
        self.canvas.delete("all")
        width = int(self.canvas.cget("width"))
        height = int(self.canvas.cget("height"))
        y = height / 2
        pad = self._px(22)
        active = BRASS if self._enabled else BRASS_DIM
        self.canvas.create_line(
            pad,
            y,
            width - pad,
            y,
            fill=TRACK,
            width=self._px(8),
            capstyle=tk.ROUND,
        )
        x = pad if self.value == 0 else width - pad
        self.canvas.create_line(
            width / 2,
            y,
            x,
            y,
            fill=active,
            width=self._px(4),
            capstyle=tk.ROUND,
        )
        self.canvas.create_oval(
            x - self._px(12),
            y - self._px(12),
            x + self._px(12),
            y + self._px(12),
            fill=AMBER if self._enabled else BRASS_DIM,
            outline=IVORY if self._enabled else TRACK,
            width=self._px(1),
        )
        self.state_label.configure(text=self.states[self.value])


class SignalMeter(tk.Canvas):
    def __init__(self, parent: tk.Misc, *, scale: float) -> None:
        self._scale = scale
        super().__init__(
            parent,
            width=self._px(420),
            height=self._px(56),
            background=PANEL_ALT,
            highlightthickness=self._px(1),
            highlightbackground=BRASS_DIM,
        )
        self._phase = 0.0
        self._energy = 0.08
        self._target = 0.08
        self._animate()

    def _px(self, value: float) -> int:
        return max(1, round(value * self._scale))

    def pulse(self, strength: float = 0.75) -> None:
        self._target = max(self._target, max(0.0, min(1.0, strength)))

    def lock(self) -> None:
        self._target = 1.0

    def settle(self) -> None:
        self._target = 0.04

    def _animate(self) -> None:
        if not self.winfo_exists():
            return
        self._phase += 0.22
        self._energy += (self._target - self._energy) * 0.18
        self._target = max(0.08, self._target * 0.94)
        self.delete("all")
        # Use the canvas's rendered size rather than its initial requested size.
        # The meter stretches with the result panel, so drawing against cget()
        # left the right side of wider signal boxes empty.
        width = max(1, self.winfo_width())
        height = max(1, self.winfo_height())
        center = height / 2
        points: list[float] = []
        segments = 72
        for index in range(segments + 1):
            x = index * width / segments
            wave = (
                math.sin(index * 0.63 + self._phase) * 0.56
                + math.sin(index * 1.71 - self._phase * 1.3) * 0.27
                + math.sin(index * 0.17 + self._phase * 0.4) * 0.17
            )
            y = center - wave * self._energy * height * 0.42
            points.extend((x, y))
        self.create_line(
            0,
            center,
            width,
            center,
            fill=TRACK,
            width=self._px(1),
        )
        self.create_line(
            *points,
            fill=GREEN if self._energy < 0.82 else AMBER,
            width=self._px(2),
            smooth=True,
        )
        self.after(65, self._animate)


class TarotApp:
    def __init__(
        self,
        root: tk.Tk,
        cards: tuple,
        speech_script_path: Path,
        art_directory: Path,
    ) -> None:
        self.root = root
        self.cards = cards
        self._art_directory = art_directory
        self._card_images: list[tk.PhotoImage] = []
        self._speech = SpeechService(speech_script_path)
        self._audio_enabled = tk.BooleanVar(value=False)
        dpi = root.winfo_fpixels("1i")
        self.scale = max(1.0, dpi / 96.0)
        self.root.tk.call("tk", "scaling", dpi / 72.0)
        self._session = SignalSession(cards)
        self._reveal_jobs: list[str] = []
        self._deal_holders: list[tk.Frame] = []
        self._deal_labels: list[tk.Label] = []
        self._deal_orientation_labels: list[tk.Label] = []
        self._deal_face_images: list[tk.PhotoImage] = []
        self._deal_back_image: tk.PhotoImage | None = None
        self._busy = False
        self._measuring = False
        self._measurement_card_count = 1
        self._measurement_spread = SPREADS[0]
        self._measurement_duration = 3
        self._measurement_samples: list[bytes] = []
        self._last_sample_count = 0
        self._result: tuple[ReadingResult, ...] | None = None
        self._result_spread = SPREADS[0]

        self._configure_window()
        self._configure_styles()
        self._build_ui()
        self._show_card_back()
        self._refresh_session_labels()
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _configure_window(self) -> None:
        self.root.title("Signal Tarot — Complete Deck")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = min(round(1080 * self.scale), screen_width - round(50 * self.scale))
        height = min(round(680 * self.scale), screen_height - round(70 * self.scale))
        self.root.geometry(f"{width}x{height}")
        min_width = min(round(940 * self.scale), width)
        min_height = min(round(600 * self.scale), height)
        self.root.minsize(min_width, min_height)
        self.root.configure(background=BG)

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Root.TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("Result.TFrame", background=PANEL_ALT)
        style.configure(
            "Title.TLabel",
            background=BG,
            foreground=IVORY,
            font=("Georgia", 21, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=BG,
            foreground=MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "ControlTitle.TLabel",
            background=PANEL,
            foreground=IVORY,
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Readout.TLabel",
            background=PANEL,
            foreground=AMBER,
            font=("Consolas", 10, "bold"),
        )
        style.configure(
            "Status.TLabel",
            background=PANEL_ALT,
            foreground=GREEN,
            font=("Consolas", 11, "bold"),
        )
        style.configure(
            "CardName.TLabel",
            background=PANEL_ALT,
            foreground=IVORY,
            font=("Georgia", 24, "bold"),
        )
        style.configure(
            "Orientation.TLabel",
            background=PANEL_ALT,
            foreground=AMBER,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "Keywords.TLabel",
            background=PANEL_ALT,
            foreground=BRASS,
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Meaning.TLabel",
            background=PANEL_ALT,
            foreground=IVORY,
            font=("Segoe UI", 12),
        )
        style.configure(
            "Meta.TLabel",
            background=PANEL_ALT,
            foreground=MUTED,
            font=("Consolas", 9),
        )
        style.configure(
            "Signal.TButton",
            background="#6f542b",
            foreground="#fff7e3",
            bordercolor=BRASS,
            lightcolor="#8b6c38",
            darkcolor="#4c391d",
            padding=(18, 11),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Signal.TButton",
            background=[("active", "#8b6c38"), ("disabled", "#292a28")],
            foreground=[("disabled", "#676966")],
        )
        style.configure(
            "Quiet.TButton",
            background=PANEL,
            foreground=MUTED,
            bordercolor=BRASS_DIM,
            padding=(13, 9),
            font=("Segoe UI", 9),
        )
        style.configure(
            "Spread.TCombobox",
            fieldbackground=PANEL,
            background="#6f542b",
            foreground=IVORY,
            arrowcolor=IVORY,
            bordercolor=BRASS_DIM,
            lightcolor=BRASS_DIM,
            darkcolor=BRASS_DIM,
            padding=(9, 8),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Spread.TCombobox",
            fieldbackground=[("readonly", PANEL), ("disabled", "#202326")],
            foreground=[("readonly", IVORY), ("disabled", "#676966")],
            selectbackground=[("readonly", PANEL)],
            selectforeground=[("readonly", IVORY)],
        )
        style.configure(
            "Audio.TCheckbutton",
            background=PANEL_ALT,
            foreground=MUTED,
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Audio.TCheckbutton",
            background=[("active", PANEL_ALT)],
            foreground=[("selected", AMBER), ("disabled", "#555956")],
        )

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, style="Root.TFrame", padding=round(20 * self.scale))
        outer.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(1, weight=1)

        header = ttk.Frame(outer, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, round(14 * self.scale)))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="SIGNAL TAROT", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="OFFLINE 78-CARD MULTI-SEED INSTRUMENT  ·  OPTIONAL LOCAL VOICE  ·  NO NETWORK",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))
        self.sigil_label = ttk.Label(header, style="Subtitle.TLabel")
        self.sigil_label.grid(row=0, column=1, rowspan=2, sticky="e")

        controls_panel = ttk.Frame(
            outer,
            style="Panel.TFrame",
            padding=round(16 * self.scale),
        )
        controls_panel.grid(row=1, column=0, sticky="nsw", padx=(0, round(14 * self.scale)))

        self.frequency = Dial(
            controls_panel,
            label="FREQUENCY",
            minimum=0,
            maximum=999,
            value=437,
            scale=self.scale,
            command=lambda value, direction: self._control_changed("frequency", value, direction),
        )
        self.frequency.grid(row=0, column=0, padx=round(7 * self.scale), pady=(0, round(14 * self.scale)))
        self.resonance = Dial(
            controls_panel,
            label="RESONANCE",
            minimum=0,
            maximum=100,
            value=50,
            scale=self.scale,
            command=lambda value, direction: self._control_changed("resonance", value, direction),
        )
        self.resonance.grid(row=0, column=1, padx=round(7 * self.scale), pady=(0, round(14 * self.scale)))
        self.drift = Dial(
            controls_panel,
            label="DRIFT",
            minimum=-100,
            maximum=100,
            value=0,
            scale=self.scale,
            command=lambda value, direction: self._control_changed("drift", value, direction),
        )
        self.drift.grid(row=1, column=0, padx=round(7 * self.scale), pady=(0, round(18 * self.scale)))
        self.duration = Dial(
            controls_panel,
            label="MEASUREMENT WINDOW",
            minimum=1,
            maximum=10,
            value=3,
            scale=self.scale,
            command=lambda value, direction: self._control_changed(
                "measurement_window", value, direction
            ),
            choices=(1, 3, 5, 7, 10),
            value_suffix=" SEC",
        )
        self.duration.grid(
            row=1,
            column=1,
            padx=round(7 * self.scale),
            pady=(0, round(18 * self.scale)),
        )

        self.direction = Lever(
            controls_panel,
            label="DIRECTION",
            states=("FORWARD", "RETURN"),
            value=0,
            scale=self.scale,
            command=lambda value, direction: self._control_changed("direction", value, direction),
        )
        self.direction.grid(row=2, column=0, padx=round(7 * self.scale))
        self.filter_mode = Lever(
            controls_panel,
            label="FILTER",
            states=("LOW", "HIGH"),
            value=0,
            scale=self.scale,
            command=lambda value, direction: self._control_changed("filter", value, direction),
        )
        self.filter_mode.grid(row=2, column=1, padx=round(7 * self.scale))

        result_panel = ttk.Frame(
            outer,
            style="Result.TFrame",
            padding=round(24 * self.scale),
        )
        self.result_panel = result_panel
        result_panel.grid(row=1, column=1, sticky="nsew")
        result_panel.columnconfigure(0, weight=1)
        result_panel.rowconfigure(6, weight=1)

        self.status_label = ttk.Label(result_panel, text="THE SIGNAL IS QUIET", style="Status.TLabel")
        self.status_label.grid(row=0, column=0, sticky="w")
        self.meter = SignalMeter(result_panel, scale=self.scale)
        self.meter.grid(row=1, column=0, sticky="ew", pady=(round(10 * self.scale), round(24 * self.scale)))

        self.art_frame = tk.Frame(result_panel, background=PANEL_ALT)
        self.art_frame.grid(row=2, column=0, sticky="ew", pady=(0, round(12 * self.scale)))

        self.card_name_label = ttk.Label(result_panel, text="—", style="CardName.TLabel")
        self.card_name_label.grid(row=3, column=0, sticky="w")
        self.orientation_label = ttk.Label(result_panel, text="TUNE THE INSTRUMENT TO BEGIN", style="Orientation.TLabel")
        self.orientation_label.grid(row=4, column=0, sticky="w", pady=(round(5 * self.scale), 0))
        self.keywords_label = ttk.Label(result_panel, text="", style="Keywords.TLabel")
        self.keywords_label.grid(row=5, column=0, sticky="w", pady=(round(16 * self.scale), 0))
        reading_frame = tk.Frame(result_panel, background=PANEL_ALT)
        reading_frame.grid(row=6, column=0, sticky="nsew", pady=(round(10 * self.scale), 0))
        reading_frame.rowconfigure(0, weight=1)
        reading_frame.columnconfigure(0, weight=1)
        self.meaning_text = tk.Text(
            reading_frame,
            background=PANEL_ALT,
            foreground=IVORY,
            insertbackground=IVORY,
            selectbackground=BRASS_DIM,
            selectforeground=IVORY,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            wrap="word",
            font=("Segoe UI", 12),
            padx=0,
            pady=0,
            cursor="arrow",
        )
        self.meaning_text.grid(row=0, column=0, sticky="nsew")
        reading_scroll = ttk.Scrollbar(
            reading_frame,
            orient="vertical",
            command=self.meaning_text.yview,
        )
        reading_scroll.grid(row=0, column=1, sticky="ns", padx=(round(8 * self.scale), 0))
        self.meaning_text.configure(yscrollcommand=reading_scroll.set)
        self._set_reading_text(INTRO_TEXT)

        bottom = ttk.Frame(result_panel, style="Result.TFrame")
        bottom.grid(row=7, column=0, sticky="ew", pady=(round(18 * self.scale), 0))
        bottom.columnconfigure(0, weight=3)
        bottom.columnconfigure(1, weight=1)
        self.deck_label = ttk.Label(bottom, style="Meta.TLabel")
        self.deck_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, round(8 * self.scale)))
        self.audio_toggle = ttk.Checkbutton(
            bottom,
            text="VOICE OFF / ON" if self._speech.available else "VOICE UNAVAILABLE",
            variable=self._audio_enabled,
            command=self._audio_toggled,
            style="Audio.TCheckbutton",
            state="normal" if self._speech.available else "disabled",
        )
        self.audio_toggle.grid(row=0, column=2, sticky="e", pady=(0, round(8 * self.scale)))
        self.spread_choice = tk.StringVar(value=SPREADS[0].selector_label)
        self.spread_selector = ttk.Combobox(
            bottom,
            textvariable=self.spread_choice,
            values=tuple(spread.selector_label for spread in SPREADS),
            state="readonly",
            style="Spread.TCombobox",
            width=42,
        )
        self.spread_selector.grid(row=1, column=0, sticky="ew")
        self.spread_selector.bind("<<ComboboxSelected>>", self._spread_selected)
        self.draw_button = ttk.Button(
            bottom,
            text="DRAW 1 CARD",
            style="Signal.TButton",
            command=self._begin_draw,
            state="disabled",
        )
        self.draw_button.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(round(8 * self.scale), 0),
        )
        self.reset_button = ttk.Button(
            bottom,
            text="RESET DECK",
            style="Quiet.TButton",
            command=self._reset,
        )
        self.reset_button.grid(row=1, column=2, padx=(round(8 * self.scale), 0))

        self.measurement_overlay = tk.Frame(result_panel, background=PANEL_ALT)
        measurement_prompt = tk.Label(
            self.measurement_overlay,
            text="Concentrate on Your Question",
            background=PANEL_ALT,
            foreground=IVORY,
            font=("Georgia", 24, "bold"),
            anchor="center",
            justify="center",
        )
        measurement_prompt.pack(expand=True, fill="both", padx=30, pady=30)

    def _current_state(self) -> ControlState:
        return ControlState(
            frequency=self.frequency.value,
            resonance=self.resonance.value,
            drift=self.drift.value,
            direction=self.direction.state,
            filter_mode=self.filter_mode.state,
        )

    def _control_changed(self, name: str, value: int | str, direction: str) -> None:
        if self._busy and not self._measuring:
            return
        self._session.record_event(name, value, direction, self._current_state())
        strength = min(0.9, 0.35 + self._session.interaction_count * 0.035)
        self.meter.pulse(strength)
        if not self._measuring:
            self.status_label.configure(text="TUNING — SIGNAL SHIFT DETECTED", foreground=GREEN)
        self._update_draw_buttons()
        self._refresh_session_labels()

    def _begin_draw(self) -> None:
        self._begin_reading(self._selected_spread())

    def _selected_spread(self) -> SpreadDefinition:
        return SPREADS_BY_LABEL.get(self.spread_choice.get(), SPREADS[0])

    def _spread_selected(self, _event: tk.Event | None = None) -> None:
        count = len(self._selected_spread().positions)
        noun = "CARD" if count == 1 else "CARDS"
        self.draw_button.configure(text=f"DRAW {count} {noun}")
        self._update_draw_buttons()

    def _begin_reading(self, spread: SpreadDefinition) -> None:
        count = len(spread.positions)
        if self._busy or not self._session.can_draw_count(count):
            return
        self._speech.stop()
        self._busy = True
        self._measuring = True
        self._measurement_card_count = count
        self._measurement_spread = spread
        self._measurement_duration = self.duration.value
        self._measurement_samples = []
        self.duration.set_enabled(False)
        self.draw_button.configure(state="disabled")
        self.spread_selector.configure(state="disabled")
        self.reset_button.configure(state="disabled")
        self.card_name_label.configure(text="—")
        self.orientation_label.configure(text="CONTROLS ARE LIVE — MOVE THEM THROUGH THE SIGNAL")
        self.keywords_label.configure(text="")
        self._set_reading_text("")
        self.meter.lock()
        self._show_measurement_overlay()

        try:
            self._measurement_samples.append(
                self._session.capture_seed_sample(self._current_state(), 0)
            )
        except RuntimeError as exc:
            self._abort_measurement(str(exc))
            return
        self._reveal_jobs = [
            self.root.after(SignalSession.SAMPLE_INTERVAL_MS, self._measurement_tick)
        ]

    def _measurement_tick(self) -> None:
        if not self._measuring:
            return
        sample_index = len(self._measurement_samples)
        self._measurement_samples.append(
            self._session.capture_seed_sample(self._current_state(), sample_index)
        )
        expected_samples = (
            self._measurement_duration * SignalSession.SAMPLES_PER_SECOND + 1
        )
        if len(self._measurement_samples) >= expected_samples:
            self._finish_measurement()
            return
        self._reveal_jobs.append(
            self.root.after(SignalSession.SAMPLE_INTERVAL_MS, self._measurement_tick)
        )

    def _finish_measurement(self) -> None:
        self._measuring = False
        self._hide_measurement_overlay()
        self._set_controls_enabled(False)
        try:
            results = self._session.draw_many_from_samples(
                self._current_state(),
                self._measurement_card_count,
                self._measurement_duration,
                tuple(self._measurement_samples),
            )
        except (RuntimeError, ValueError) as exc:
            self._abort_measurement(str(exc))
            return

        self._last_sample_count = len(self._measurement_samples)
        self._result = results
        self._result_spread = self._measurement_spread
        self.status_label.configure(
            text=f"FUSING {self._last_sample_count:02d} SAMPLE SEEDS…",
            foreground=AMBER,
        )
        self.orientation_label.configure(text="CARRIER SEARCH IN PROGRESS")
        self._reveal_jobs.extend(
            (
                self.root.after(450, self._carrier_found),
                self.root.after(
                    800,
                    lambda: self._start_card_sequence(results, self._measurement_spread),
                ),
            )
        )

    def _abort_measurement(self, message: str) -> None:
        self._measuring = False
        self._hide_measurement_overlay()
        self._busy = False
        self._measurement_samples.clear()
        self._set_controls_enabled(True)
        self.reset_button.configure(state="normal")
        self._update_draw_buttons()
        self.status_label.configure(text="MEASUREMENT INTERRUPTED", foreground=RED)
        messagebox.showinfo("Signal Tarot", message, parent=self.root)

    def _show_measurement_overlay(self) -> None:
        self.measurement_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.measurement_overlay.lift()

    def _hide_measurement_overlay(self) -> None:
        self.measurement_overlay.place_forget()

    def _clear_card_art(self) -> None:
        for child in self.art_frame.winfo_children():
            child.destroy()
        self._card_images.clear()
        self._deal_holders.clear()
        self._deal_labels.clear()
        self._deal_orientation_labels.clear()
        self._deal_face_images.clear()
        self._deal_back_image = None

    def _resize_card_image(
        self,
        image: tk.PhotoImage,
        spread: SpreadDefinition,
    ) -> tk.PhotoImage:
        if spread.image_divisor == 0:
            return image.zoom(2, 2).subsample(3, 3)
        return image.subsample(spread.image_divisor, spread.image_divisor)

    def _load_card_image(
        self,
        result: ReadingResult,
        *,
        spread: SpreadDefinition,
    ) -> tk.PhotoImage:
        suffix = "-reversed" if result.reversed else ""
        path = self._art_directory / f"{result.card.id}{suffix}.png"
        image = tk.PhotoImage(file=str(path))
        image = self._resize_card_image(image, spread)
        self._card_images.append(image)
        return image

    def _create_spread_layout(
        self,
        spread: SpreadDefinition,
        card_height: int,
    ) -> tk.Frame:
        layout = tk.Frame(self.art_frame, background=PANEL_ALT)
        coordinates, height = self._spread_geometry(spread, card_height)
        if coordinates is not None:
            layout.configure(height=height)
            layout.pack(fill="x")
            layout.pack_propagate(False)
        else:
            layout.pack(fill="x")
        return layout

    def _spread_geometry(
        self,
        spread: SpreadDefinition,
        card_height: int,
    ) -> tuple[tuple[tuple[float, int], ...] | None, int]:
        """Return normalized x/pixel y coordinates for non-linear layouts."""
        slot = card_height + round(32 * self.scale)
        count = len(spread.positions)

        if spread.layout == "row":
            return None, 0
        if spread.layout == "cross":
            coordinates = (
                (0.50, slot),
                (0.50, slot * 2),
                (0.23, slot),
                (0.77, slot),
                (0.50, 0),
            )
            return coordinates, slot * 3
        if spread.layout == "horseshoe":
            x_positions = (0.06, 0.20, 0.35, 0.50, 0.65, 0.80, 0.94)
            y_positions = tuple(
                round(value * self.scale) for value in (68, 34, 0, 0, 0, 34, 68)
            )
            return tuple(zip(x_positions, y_positions, strict=True)), slot + y_positions[-1]
        if spread.layout == "grid":
            columns = 3
            coordinates = tuple(
                ((column + 0.5) / columns, row * slot)
                for row in range(math.ceil(count / columns))
                for column in range(columns)
            )[:count]
            return coordinates, math.ceil(count / columns) * slot
        if spread.layout == "mirror":
            coordinates = tuple(
                (0.27 if index % 2 == 0 else 0.73, (index // 2) * slot)
                for index in range(count)
            )
            return coordinates, 3 * slot
        if spread.layout == "pyramid":
            coordinates = (
                (0.20, slot * 2),
                (0.50, slot * 2),
                (0.80, slot * 2),
                (0.35, slot),
                (0.65, slot),
                (0.50, 0),
            )
            return coordinates, 3 * slot
        if spread.layout == "branches":
            coordinates = (
                (0.50, 0),
                (0.22, slot),
                (0.22, slot * 2),
                (0.22, slot * 3),
                (0.78, slot),
                (0.78, slot * 2),
                (0.78, slot * 3),
            )
            return coordinates, 4 * slot
        if spread.layout == "chakra":
            x_positions = (0.06, 0.20, 0.35, 0.50, 0.65, 0.80, 0.94)
            y_positions = tuple(
                round(value * self.scale) for value in (42, 27, 13, 0, 13, 27, 42)
            )
            return tuple(zip(x_positions, y_positions, strict=True)), slot + y_positions[0]
        if spread.layout == "compass":
            center_y = slot
            coordinates = (
                (0.50, center_y),
                (0.50, 0),
                (0.75, round(slot * 0.30)),
                (0.84, center_y),
                (0.75, round(slot * 1.70)),
                (0.50, slot * 2),
                (0.25, round(slot * 1.70)),
                (0.16, center_y),
                (0.25, round(slot * 0.30)),
            )
            return coordinates, 3 * slot
        if spread.layout == "celtic_cross":
            coordinates = (
                (0.30, slot),
                (0.43, slot),
                (0.30, slot * 2),
                (0.12, slot),
                (0.30, 0),
                (0.58, slot),
                (0.86, round(slot * 2.25)),
                (0.86, round(slot * 1.50)),
                (0.86, round(slot * 0.75)),
                (0.86, 0),
            )
            return coordinates, round(slot * 3.25)
        if spread.layout == "tree":
            coordinates = (
                (0.50, 0),
                (0.20, slot),
                (0.50, slot),
                (0.80, slot),
                (0.20, slot * 2),
                (0.50, slot * 2),
                (0.80, slot * 2),
                (0.20, slot * 3),
                (0.50, slot * 3),
                (0.80, slot * 3),
            )
            return coordinates, slot * 4
        if spread.layout == "wheel":
            center_y = slot * 1.10
            radius_y = slot * 0.95
            coordinates = tuple(
                (
                    0.50 + 0.42 * math.cos(math.radians(-90 + index * 30)),
                    round(center_y + radius_y * math.sin(math.radians(-90 + index * 30))),
                )
                for index in range(12)
            )
            return coordinates, round(slot * 3.15)
        raise ValueError(f"Unsupported spread layout: {spread.layout}")

    def _place_spread_column(
        self,
        column: tk.Frame,
        index: int,
        spread: SpreadDefinition,
        card_height: int,
    ) -> None:
        coordinates, _ = self._spread_geometry(spread, card_height)
        if coordinates is not None:
            relx, y = coordinates[index]
            column.place(relx=relx, y=y, anchor="n")
            return
        column.pack(
            side="left" if len(spread.positions) > 1 else "top",
            expand=len(spread.positions) > 1,
            padx=round((5 if len(spread.positions) <= 3 else 2) * self.scale),
        )

    def _show_card_back(self) -> None:
        self._clear_card_art()
        path = self._art_directory / "card-back.png"
        try:
            image = tk.PhotoImage(file=str(path)).subsample(2, 2)
        except tk.TclError:
            ttk.Label(
                self.art_frame,
                text="THE DECK WAITS",
                style="Orientation.TLabel",
            ).pack()
            return
        self._card_images.append(image)
        tk.Label(
            self.art_frame,
            image=image,
            background=PANEL_ALT,
            borderwidth=0,
        ).pack()

    def _show_card_art(
        self,
        results: tuple[ReadingResult, ...],
        spread: SpreadDefinition,
    ) -> None:
        self._clear_card_art()
        compact = len(results) > 1
        card_height = 200 if spread.image_divisor == 0 else math.ceil(
            300 / spread.image_divisor
        )
        layout = self._create_spread_layout(spread, card_height)
        for index, result in enumerate(results):
            column = tk.Frame(layout, background=PANEL_ALT)
            if compact:
                tk.Label(
                    column,
                    text=spread.positions[index],
                    background=PANEL_ALT,
                    foreground=BRASS,
                    font=("Segoe UI", 8 if len(results) <= 5 else 7, "bold"),
                    wraplength=round((90 if len(results) <= 3 else 65) * self.scale),
                    justify="center",
                    height=2 if spread.layout != "row" or len(results) > 3 else 1,
                ).pack(pady=(0, round(4 * self.scale)))
            try:
                image = self._load_card_image(result, spread=spread)
            except tk.TclError:
                tk.Label(
                    column,
                    text="ARTWORK UNAVAILABLE",
                    background=PANEL_ALT,
                    foreground=RED,
                    font=("Consolas", 8, "bold"),
                ).pack(padx=12, pady=24)
            else:
                tk.Label(
                    column,
                    image=image,
                    background=PANEL_ALT,
                    borderwidth=0,
                ).pack()
            if compact and spread.layout == "row":
                tk.Label(
                    column,
                    text="REVERSED" if result.reversed else "UPRIGHT",
                    background=PANEL_ALT,
                    foreground=AMBER,
                    font=("Segoe UI", 8, "bold"),
                ).pack(pady=(round(4 * self.scale), 0))
            self._place_spread_column(column, index, spread, card_height)

    def _start_card_sequence(
        self,
        results: tuple[ReadingResult, ...],
        spread: SpreadDefinition,
    ) -> None:
        """Deal the selected cards face down, then reveal them in order."""
        self.meter.settle()
        self.status_label.configure(text="DEALING FROM THE DECK…", foreground=AMBER)
        self.orientation_label.configure(text="CARDS DESCENDING FACE DOWN")
        if not self._prepare_card_sequence(results, spread):
            self._reveal_identity(results, spread)
            self._reveal_jobs.append(
                self.root.after(350, lambda: self._reveal_meaning(results, spread))
            )
            return
        self.root.update_idletasks()
        self._deal_card(results, spread, 0)

    def _prepare_card_sequence(
        self,
        results: tuple[ReadingResult, ...],
        spread: SpreadDefinition,
    ) -> bool:
        self._clear_card_art()
        compact = len(results) > 1
        try:
            back = tk.PhotoImage(file=str(self._art_directory / "card-back.png"))
            back = self._resize_card_image(back, spread)
            self._card_images.append(back)
            self._deal_back_image = back
            layout = self._create_spread_layout(spread, back.height())

            for index, result in enumerate(results):
                column = tk.Frame(layout, background=PANEL_ALT)
                if compact:
                    tk.Label(
                        column,
                        text=spread.positions[index],
                        background=PANEL_ALT,
                        foreground=BRASS,
                        font=("Segoe UI", 8 if len(results) <= 5 else 7, "bold"),
                        wraplength=round((90 if len(results) <= 3 else 65) * self.scale),
                        justify="center",
                        height=2 if spread.layout != "row" or len(results) > 3 else 1,
                    ).pack(pady=(0, round(4 * self.scale)))

                holder = tk.Frame(
                    column,
                    width=back.width(),
                    height=back.height(),
                    background=PANEL_ALT,
                )
                holder.pack_propagate(False)
                holder.pack()
                card_label = tk.Label(
                    holder,
                    image=back,
                    background=PANEL_ALT,
                    borderwidth=0,
                    highlightthickness=0,
                )
                card_label.place_forget()

                face = self._load_card_image(result, spread=spread)
                orientation_label = tk.Label(
                    column,
                    text="" if compact else " ",
                    background=PANEL_ALT,
                    foreground=AMBER,
                    font=("Segoe UI", 8, "bold"),
                )
                if compact and spread.layout == "row":
                    orientation_label.pack(pady=(round(4 * self.scale), 0))

                self._deal_holders.append(holder)
                self._deal_labels.append(card_label)
                self._deal_face_images.append(face)
                self._deal_orientation_labels.append(orientation_label)
                self._place_spread_column(
                    column,
                    index,
                    spread,
                    back.height(),
                )
        except tk.TclError:
            self._clear_card_art()
            return False
        return True

    def _deal_card(
        self,
        results: tuple[ReadingResult, ...],
        spread: SpreadDefinition,
        index: int,
    ) -> None:
        if index >= len(results):
            self.status_label.configure(
                text="ALL CARDS RECEIVED — REVEALING IN SEQUENCE",
                foreground=AMBER,
            )
            self._reveal_jobs.append(
                self.root.after(320, lambda: self._flip_card(results, spread, 0))
            )
            return

        back = self._deal_back_image
        holder = self._deal_holders[index]
        if back is None or not holder.winfo_exists():
            self._reveal_identity(results, spread)
            self._reveal_meaning(results, spread)
            return

        self.status_label.configure(
            text=f"DEALING CARD {index + 1} OF {len(results)}…",
            foreground=AMBER,
        )
        self.root.update_idletasks()
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        destination_x = holder.winfo_rootx() - root_x
        destination_y = holder.winfo_rooty() - root_y
        start_x = (self.root.winfo_width() - back.width()) / 2
        start_y = -back.height() - round(10 * self.scale)
        flying = tk.Label(
            self.root,
            image=back,
            background=PANEL_ALT,
            borderwidth=0,
            highlightthickness=0,
        )
        flying.place(x=round(start_x), y=round(start_y))
        flying.lift()

        frames = 18

        def move(frame: int) -> None:
            if not flying.winfo_exists():
                return
            progress = min(1.0, frame / frames)
            eased = 1.0 - (1.0 - progress) ** 3
            arc = math.sin(progress * math.pi) * round(18 * self.scale)
            x = start_x + (destination_x - start_x) * eased + arc * (1 if index % 2 else -1)
            y = start_y + (destination_y - start_y) * eased
            flying.place(x=round(x), y=round(y))
            if frame < frames:
                self._reveal_jobs.append(self.root.after(24, lambda: move(frame + 1)))
                return
            flying.destroy()
            label = self._deal_labels[index]
            label.configure(image=back)
            label.place(relx=0.5, rely=0.5, anchor="center", width=back.width(), height=back.height())
            self._reveal_jobs.append(
                self.root.after(
                    130,
                    lambda: self._deal_card(results, spread, index + 1),
                )
            )

        move(0)

    def _flip_card(
        self,
        results: tuple[ReadingResult, ...],
        spread: SpreadDefinition,
        index: int,
    ) -> None:
        if index >= len(results):
            if len(results) == 1:
                result = results[0]
                self.card_name_label.configure(text=result.card.name.upper())
                self.orientation_label.configure(
                    text="REVERSED" if result.reversed else "UPRIGHT"
                )
            else:
                self.card_name_label.configure(text=spread.name.upper())
                self.orientation_label.configure(
                    text=(
                        "  ·  ".join(spread.positions)
                        if len(results) <= 3
                        else f"{len(results)} POSITIONS — {spread.positions[0]} TO {spread.positions[-1]}"
                    )
                )
            self.status_label.configure(text="SIGNAL RESOLVED", foreground=GREEN)
            self._reveal_jobs.append(
                self.root.after(350, lambda: self._reveal_meaning(results, spread))
            )
            return

        result = results[index]
        label = self._deal_labels[index]
        holder = self._deal_holders[index]
        face = self._deal_face_images[index]
        full_width = holder.winfo_width()
        full_height = holder.winfo_height()
        half_frames = 7
        self.status_label.configure(
            text=f"REVEALING CARD {index + 1} OF {len(results)}…",
            foreground=AMBER,
        )

        def collapse(frame: int) -> None:
            progress = min(1.0, frame / half_frames)
            width = max(2, round(full_width * (1.0 - progress)))
            label.place_configure(width=width, height=full_height)
            if frame < half_frames:
                self._reveal_jobs.append(
                    self.root.after(24, lambda: collapse(frame + 1))
                )
                return
            label.configure(image=face)
            expand(0)

        def expand(frame: int) -> None:
            progress = min(1.0, frame / half_frames)
            eased = math.sin(progress * math.pi / 2)
            width = max(2, round(full_width * eased))
            label.place_configure(width=width, height=full_height)
            if frame < half_frames:
                self._reveal_jobs.append(
                    self.root.after(24, lambda: expand(frame + 1))
                )
                return
            label.place_configure(width=full_width, height=full_height)
            if len(results) == 1:
                self.card_name_label.configure(text=result.card.name.upper())
                self.orientation_label.configure(
                    text="REVERSED" if result.reversed else "UPRIGHT"
                )
            else:
                self.card_name_label.configure(
                    text=f"{spread.positions[index]} — {result.card.name.upper()}"
                )
                self.orientation_label.configure(
                    text="REVERSED" if result.reversed else "UPRIGHT"
                )
                self._deal_orientation_labels[index].configure(
                    text="REVERSED" if result.reversed else "UPRIGHT"
                )
            self._reveal_jobs.append(
                self.root.after(
                    360,
                    lambda: self._flip_card(results, spread, index + 1),
                )
            )

        collapse(0)

    def _carrier_found(self) -> None:
        self.status_label.configure(text="CARRIER FOUND — RESOLVING", foreground=AMBER)

    def _reveal_identity(
        self,
        results: tuple[ReadingResult, ...],
        spread: SpreadDefinition,
    ) -> None:
        self.meter.settle()
        self.status_label.configure(text="SIGNAL RESOLVED", foreground=GREEN)
        self._show_card_art(results, spread)
        if len(results) == 1:
            result = results[0]
            self.card_name_label.configure(text=result.card.name.upper())
            self.orientation_label.configure(text="REVERSED" if result.reversed else "UPRIGHT")
        else:
            self.card_name_label.configure(text=spread.name.upper())
            self.orientation_label.configure(
                text=(
                    "  ·  ".join(spread.positions)
                    if len(results) <= 3
                    else f"{len(results)} POSITIONS — {spread.positions[0]} TO {spread.positions[-1]}"
                )
            )

    def _reveal_meaning(
        self,
        results: tuple[ReadingResult, ...],
        spread: SpreadDefinition,
    ) -> None:
        if len(results) == 1:
            result = results[0]
            self.keywords_label.configure(
                text="  ·  ".join(keyword.upper() for keyword in result.meaning.keywords)
            )
            self._set_reading_text(result.meaning.text)
        else:
            self.keywords_label.configure(
                text=f"{spread.name.upper()}  ·  {len(results)} CARDS REVEALED"
            )
            self._set_reading_text(format_spread_reading(results, spread.positions))
        if self._audio_enabled.get():
            self._speak_results(results, spread)
        self._busy = False
        self._set_controls_enabled(True)
        self.reset_button.configure(state="normal")
        if self._session.remaining_count == 0:
            self.status_label.configure(text="THE DECK IS EXHAUSTED", foreground=RED)
            self.orientation_label.configure(text="RESET TO CONTINUE")
        else:
            self.status_label.configure(
                text=(
                    f"SIGNAL HELD — {self._last_sample_count:02d} SEEDS FUSED  ·  "
                    "DRAW AGAIN OR RETUNE"
                ),
                foreground=GREEN,
            )
        self._update_draw_buttons()
        self._refresh_session_labels()

    def _set_reading_text(self, text: str) -> None:
        self.meaning_text.configure(state="normal")
        self.meaning_text.delete("1.0", "end")
        self.meaning_text.insert("1.0", text)
        self.meaning_text.configure(state="disabled")
        self.meaning_text.yview_moveto(0.0)

    def _update_draw_buttons(self) -> None:
        if self._busy:
            draw_state = "disabled"
            selector_state = "disabled"
        else:
            count = len(self._selected_spread().positions)
            draw_state = "normal" if self._session.can_draw_count(count) else "disabled"
            selector_state = "readonly"
        self.draw_button.configure(state=draw_state)
        self.spread_selector.configure(state=selector_state)

    def _audio_toggled(self) -> None:
        if not self._audio_enabled.get():
            self._speech.stop()
            return
        if self._result is not None and not self._busy:
            self._speak_results(self._result, self._result_spread)

    def _speak_results(
        self,
        results: tuple[ReadingResult, ...],
        spread: SpreadDefinition,
    ) -> None:
        if len(results) == 1:
            result = results[0]
            orientation = "reversed" if result.reversed else "upright"
            narration = (
                f"{result.card.name}. {orientation}. "
                f"{', '.join(result.meaning.keywords)}. {result.meaning.text}"
            )
        else:
            narration = format_spread_speech(results, spread.positions)
        if not self._speech.speak(narration):
            self._audio_enabled.set(False)

    def _set_controls_enabled(self, enabled: bool) -> None:
        self.frequency.set_enabled(enabled)
        self.resonance.set_enabled(enabled)
        self.drift.set_enabled(enabled)
        self.direction.set_enabled(enabled)
        self.filter_mode.set_enabled(enabled)
        self.duration.set_enabled(enabled)

    def _reset(self) -> None:
        self._speech.stop()
        self._hide_measurement_overlay()
        for job in self._reveal_jobs:
            try:
                self.root.after_cancel(job)
            except tk.TclError:
                pass
        self._reveal_jobs.clear()
        self._session = SignalSession(self.cards)
        self._result = None
        self._busy = False
        self._measuring = False
        self._measurement_samples.clear()
        self._last_sample_count = 0
        self._show_card_back()
        self.frequency.set_value(437)
        self.resonance.set_value(50)
        self.drift.set_value(0)
        self.duration.set_value(3)
        self.direction.set_value(0)
        self.filter_mode.set_value(0)
        self._set_controls_enabled(True)
        self.meter.settle()
        self.status_label.configure(text="THE SIGNAL IS QUIET", foreground=GREEN)
        self.card_name_label.configure(text="—")
        self.orientation_label.configure(text="TUNE THE INSTRUMENT TO BEGIN")
        self.keywords_label.configure(text="")
        self._set_reading_text(INTRO_TEXT)
        self._update_draw_buttons()
        self.reset_button.configure(state="normal")
        self._refresh_session_labels()

    def _close(self) -> None:
        self._speech.stop()
        self.root.destroy()

    def _refresh_session_labels(self) -> None:
        self.sigil_label.configure(text=f"SESSION SIGIL  {self._session.sigil}")
        self.deck_label.configure(
            text=(
                f"DRAW {self._session.draw_number + 1:02d}  ·  "
                f"{self._session.remaining_count:02d} CARDS REMAIN  ·  "
                f"{self._session.interaction_count:02d} SIGNAL EVENTS"
            )
        )
