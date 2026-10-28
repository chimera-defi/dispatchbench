"""Check the site's six accessibility pairs against shipped report theme tokens."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAIRS = (
    ('card-meta text', '--color-card-meta', '--panel', 4.5),
    ('kicker / tag text', '--color-kicker', '--panel', 4.5),
    ('pressed button text', '--color-pressed-text', '--bg', 4.5),
    ('primary button text', '--color-primary-text', '--panel', 4.5),
    ('input border on surface', '--color-input-border', '--panel', 3),
    ('input border on bg', '--color-input-border', '--bg', 3),
)


def declarations(body):
    return dict(re.findall(r'(--[\w-]+)\s*:\s*([^;]+)', body))


def theme_values(css, mode, *, automatic=False):
    # Only top-level :root blocks form the base; media/explicit overrides follow.
    values = {}
    for body in re.findall(r'(?:^|\n):root\{([^}]*)\}', css):
        values.update(declarations(body))
    selector = (r'@media\(prefers-color-scheme:' + mode
                + r'\)\{:root:not\(\[data-theme="[^"]+"\]\)\{'
                if automatic else r':root\[data-theme="' + mode + r'"\]\{')
    for body in re.findall(selector + r'([^}]*)\}', css):
        values.update(declarations(body))
    return values


def rgb(value, values, background):
    value = value.strip()
    if value.startswith('--'):
        return rgb(values[value], values, background)
    alias = re.fullmatch(r'var\((--[\w-]+)\)', value)
    if alias:
        return rgb(alias[1], values, background)
    mix = re.fullmatch(r'color-mix\(in srgb,var\((--[\w-]+)\) ([\d.]+)%,transparent\)', value)
    if mix:
        weight = float(mix[2]) / 100
        return tuple(int(a * weight + b * (1 - weight) + .5)
                     for a, b in zip(rgb(mix[1], values, background), background))
    if re.fullmatch(r'#[0-9a-fA-F]{6}', value):
        return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))
    raise ValueError(f'unsupported contrast token: {value}')


def luminance(channels):
    def linear(channel):
        channel /= 255
        return channel / 12.92 if channel <= .04045 else ((channel + .055) / 1.055) ** 2.4
    return sum(linear(c) * w for c, w in zip(channels, (.2126, .7152, .0722)))


def contrast(a, b):
    low, high = sorted((luminance(a), luminance(b)))
    return (high + .05) / (low + .05)


def check(css):
    for mode in ('dark', 'light'):
        for automatic in (False, True):
            values = theme_values(css, mode, automatic=automatic)
            for name, foreground, ground, minimum in PAIRS:
                back = rgb(ground, values, None)
                ratio = contrast(rgb(foreground, values, back), back)
                yield f'{mode}/{"system" if automatic else "explicit"} {name}', ratio, minimum


def main():
    results = list(check((ROOT / 'docs/page/tokens.css').read_text()))
    for name, ratio, minimum in results:
        print(f'{"ok" if ratio >= minimum else "FAIL"} {ratio:.2f}:1 (min {minimum}) {name}')
    return any(ratio < minimum for _, ratio, minimum in results)


if __name__ == '__main__':
    raise SystemExit(main())
