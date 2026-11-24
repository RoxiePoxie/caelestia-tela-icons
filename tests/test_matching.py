"""Tests for caelestia-tela-icons. Run from the repo root:

    python3 -m unittest discover tests
"""
import importlib.machinery
import importlib.util
import json
import os
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parent.parent / "caelestia-tela-icons"

# The script has no .py extension, so load it by path.
_loader = importlib.machinery.SourceFileLoader("tela", str(SCRIPT))
_spec = importlib.util.spec_from_loader("tela", _loader)
tela = importlib.util.module_from_spec(_spec)
_loader.exec_module(tela)


class ClosestTela(unittest.TestCase):
    def check(self, cases):
        for seed, want in cases.items():
            allowed = want if isinstance(want, tuple) else (want,)
            with self.subTest(seed=seed):
                self.assertIn(tela.closest_tela(seed), allowed)

    def test_tela_colors_map_to_themselves(self):
        self.check({hex_: name for name, hex_ in tela.TELA_COLORS.items()})

    def test_obvious_colors(self):
        self.check({
            "ff0000": "red", "00aa00": "green", "0000ff": "blue", "ffff00": "yellow",
            "ff8800": "orange", "ff66aa": "pink", "8800ff": "purple", "00aaaa": "manjaro",
        })

    def test_dark_colors_keep_their_hue(self):
        # Dark green must not become black just because both are dark.
        self.check({"33653e": "green", "1d3b2a": ("green", "manjaro"), "3a2a1a": "brown"})

    def test_matugen_key_colors(self):
        # Real primary_paletteKeyColor values from Caelestia's built-in schemes.
        self.check({
            "7171ac": "purple",               # catppuccin mocha
            "786fab": "purple",               # rose pine
            "28828e": "manjaro",              # gruvbox (teal)
            "a46a32": "orange",               # gruvbox soft
            "5878ab": ("standard", "blue"),   # one dark
            "6a73ac": ("purple", "blue"),     # catppuccin macchiato
            "4c807d": "manjaro",              # caelestia default (teal)
        })

    def test_grays(self):
        self.check({
            "777777": ("black", "nord"), "222222": ("black", "dracula"),
            "eeeeee": "grey", "6f7b8c": "nord",
        })


class ThemeName(unittest.TestCase):
    def test_names(self):
        self.assertEqual(tela.theme_name("purple", "dark"), "Tela-purple-dark")
        self.assertEqual(tela.theme_name("green", "light"), "Tela-green-light")
        self.assertEqual(tela.theme_name("standard", "dark"), "Tela-dark")


class Input(unittest.TestCase):
    def test_clean_hex(self):
        self.assertEqual(tela.clean_hex("#7E57C2"), "7e57c2")
        for bad in ("zzz", "12345g", "", "#fff", "7e57c2ff"):
            with self.subTest(bad=bad), self.assertRaises(tela.HookError):
                tela.clean_hex(bad)

    def env(self, **values):
        clean = {k: v for k, v in os.environ.items() if not k.startswith("SCHEME_")}
        return mock.patch.dict(os.environ, {**clean, **values}, clear=True)

    def test_scheme_from_environment(self):
        colours = json.dumps({"primary_paletteKeyColor": "#66BB6A", "primary": "ffffff"})
        with self.env(SCHEME_COLOURS=colours, SCHEME_MODE="light"):
            self.assertEqual(tela.read_scheme(), ("66bb6a", "light"))

    def test_falls_back_to_primary(self):
        with self.env(SCHEME_COLOURS='{"primary": "ff9800"}'):
            self.assertEqual(tela.read_scheme(), ("ff9800", "dark"))

    def test_broken_input_gives_clear_errors(self):
        for colours in ("{oops", "[]", "{}", '{"primary": "nope"}'):
            with self.subTest(colours=colours), self.env(SCHEME_COLOURS=colours):
                with self.assertRaises(tela.HookError):
                    tela.read_scheme()

    def test_missing_scheme_file(self):
        with self.env(), mock.patch.object(tela, "SCHEME_FILE", Path("/nonexistent/scheme.json")):
            with self.assertRaises(tela.HookError):
                tela.read_scheme()


if __name__ == "__main__":
    unittest.main()
