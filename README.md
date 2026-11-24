# caelestia-tela-icons

Make your [Tela](https://github.com/vinceliuice/Tela-icon-theme) folder icons follow your
[Caelestia](https://github.com/caelestia-kde/caelestia) wallpaper colors.

Caelestia generates its color scheme from the wallpaper with Matugen, but icon themes
are plain image files with their colors baked in, so they never change along with it.
Tela comes in 15 fixed colors. This small script picks the one that looks closest to the
current scheme and switches to it, every time the colors change.

| Scheme / wallpaper color | Icons it picks |
|---|---|
| Lavender (Catppuccin Mocha, Rosé Pine) | `Tela-purple` |
| Teal (Gruvbox, Everforest, Caelestia default) | `Tela-manjaro` |
| Blue (One Dark, Tokyo Night, Solarized) | `Tela` (standard blue) |
| Dark green (Darkgreen) | `Tela-green` |
| Rust / amber (Gruvbox soft) | `Tela-orange` |
| Gray-blue, gray | `Tela-nord`, `Tela-black`, `Tela-grey` |

Dark schemes get the `-dark` variant, light schemes the `-light` one.

## Requirements

- The [Caelestia KDE port](https://github.com/caelestia-kde/caelestia) on KDE Plasma 6.
  Tested on Fedora 45 with Plasma 6.8. Elsewhere, `--dry-run` works as long as
  `~/.local/state/caelestia/scheme.json` exists, and the theme is set through `gsettings`
  when `plasma-changeicons` is missing.
- Python 3.8 or newer (no extra packages).
- All Tela color variants installed (next section).

## Install

1. Install every Tela color, for your user only (no `sudo` needed):

   ```bash
   git clone --depth 1 https://github.com/vinceliuice/Tela-icon-theme.git
   cd Tela-icon-theme
   ./install.sh -a
   ```

   This adds 45 themes (15 colors × normal/light/dark) to `~/.local/share/icons`,
   about 355 MB of data. `du` shows more, because the themes are made of about
   10,000 tiny files each.

2. Put the script on your `PATH`:

   ```bash
   install -m 755 caelestia-tela-icons ~/.local/bin/
   ```

3. Tell Caelestia to run it after every color change. Add `theme.postHook` to
   `~/.config/caelestia/cli.json` (create the file if it does not exist; if it does,
   merge the `theme` block into it):

   ```json
   {
     "theme": {
       "postHook": "\"$HOME/.local/bin/caelestia-tela-icons\""
     }
   }
   ```

4. Apply it once for the current colors:

   ```bash
   caelestia-tela-icons
   ```

From now on, changing the wallpaper (or picking a named scheme) also changes the icons.

## Usage

```text
caelestia-tela-icons                     apply the closest Tela theme
caelestia-tela-icons --dry-run           only print what it would pick
caelestia-tela-icons --test ff0000 ...   show the pick for any hex colors
caelestia-tela-icons --help
```

The script does nothing when the right theme is already active, so apps don't reload
their icons for no reason. If something goes wrong it prints one clear line and exits
with code 1; Caelestia shows that line as a warning, and the color change itself still
works.

## How the matching works

1. Read the scheme's **key color** (`primary_paletteKeyColor`): the strong color Matugen
   built the palette from. (`primary` is only a fallback: in dark mode it is a pale tint.)
2. Convert it to [OKLab / OKLCH](https://bottosson.github.io/posts/oklab/), a color space
   where equal distances look equally different to the eye. That gives three numbers:
   lightness, chroma (how colorful) and hue (angle on the color wheel).
3. Sort the color into a group by its chroma:
   - **gray** (below 0.03): pick the nearest of black, grey, nord and dracula;
   - **muted** (0.03 to 0.06): any Tela color except pure black and grey;
   - **colorful** (0.06 and up): only the colorful Tela colors.
4. Within the group, the score is *hue difference in degrees* plus small penalties for
   differences in lightness and chroma. Lowest score wins. Hue comes first, so a dark
   green still picks green, not black.

To tune it, change `GRAY_LIMIT`, `MUTED_LIMIT`, `LIGHTNESS_PENALTY` and `CHROMA_PENALTY`
at the top of the script, then run the tests:

```bash
python3 -m unittest discover tests
```

## How the theme is applied

- `plasma-changeicons` sets the KDE icon theme and tells running KDE/Qt apps to reload.
  Plasma's `gtkconfig` module then copies it into the GTK 3/4 `settings.ini` files.
- `gsettings set org.gnome.desktop.interface icon-theme` covers GTK 4 apps such as
  Nautilus (Files).

## Uninstall

1. Remove the `postHook` line from `~/.config/caelestia/cli.json`.
2. Delete the script: `rm ~/.local/bin/caelestia-tela-icons`
3. Pick another icon theme in System Settings → Colors & Themes → Icons.
4. Optionally remove Tela: run `./install.sh -r` in the Tela folder.

## Credits

- [Tela icon theme](https://github.com/vinceliuice/Tela-icon-theme) by vinceliuice
  (GPL-3.0). This repo contains none of its files, only its 15 folder color values.
- [Caelestia KDE port](https://github.com/caelestia-kde/caelestia), based on
  [Caelestia](https://github.com/caelestia-dots/shell).
- [OKLab](https://bottosson.github.io/posts/oklab/) by Björn Ottosson.

## License

[GPL-3.0](LICENSE)
