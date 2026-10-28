# DispatchBench's Fable adapter

Source: `chimera-defi/chimericlabs-llc`, commit
`c56032fca7ccb5a9661c247f0d6160a576c4b637`. `SOURCE.json` records every source path.
CSS files carry the source path and SHA in their header. The three site token
files, entry stylesheet, checker and guidance retain their upstream contents.
The patterns and benchmark theme contain only the rules used by this report,
with selectors adapted by `scripts/sync.py`.

Re-sync from the read-only GitHub contents API:

```sh
make sync-design-system SHA=c56032fca7ccb5a9661c247f0d6160a576c4b637
```

For an offline checkout with the same Git objects, append
`SOURCE_REPO=/path/to/chimericlabs-llc`. All sources are read before any file is
written, so a failed fetch preserves the existing theme. The SHA must be a full
commit hash; there is no floating-main default.

`docs/page/tokens.css` is the generated, single swappable variable block. It
contains the site's variable definitions, compatibility aliases for the existing
charts, and the readable light palette in `tokens/dispatchbench.css`. Explicit
`data-theme` values take precedence over the system colour preference. Site
spacing, typography, radii and dark data hues come from the pinned tokens.
The source base also contains components and a remote font import; the report
bundle takes its variables without importing unused components or making a
network request. Local Inter is used when installed, with the site's system-font
fallback otherwise. The current page shell links this one bundle separately.

The generated block at the end of `docs/page/style.css` applies the mapped
patterns and theme. Link, kicker, muted-text and failure-grid semantic aliases
keep light mode readable. Existing chart type floors and mobile rules remain in
force. The failure grid uses neutral and maroon ramps from the site theme.

| Site selector | Report selector |
| --- | --- |
| `main,.page` | `main` (with existing vertical/safe-area padding) |
| `nav.toc a` | `.toc a` |
| `.pick,.verdict-pick` | `.picks li` |
| `.verdict-avoid` | `.pill.bad` |
| `.callout,.winner` | `.verdict` |
| `.chart` | `.chart,.ex-chart` |
| `.chart .grid` | `.ex-grid` (the report's `.grid` is an HTML results grid) |
| `.frontier` | `.ex-front,path[data-front]` |
| `.frontier-ring` | `.ex-ring` |
| `.beaten` | `.ex-shade,.zone` |
| `.cell-all,.cell-most,.cell-half` | `.grid .pass,.grid .part,.grid .fail` |
| `.ds-kicker` | `.ex-kicker` |
| `.ds-kv`, `dt`, `dd` | `.ex-values`, `dt`, `dd` |

Dropped without a target: `h2 .emoji,h3 .emoji`, `hr,.rule`, and the
`.pt-claude/.pt-codex/.pt-codex56/.pt-grok/.pt-pipeline` selectors. Family fills
already use the unchanged chart variables on their individual markers. The
site's forced dark `html` rule is replaced by the token block's light/dark
handling. Top-bar patterns belong to the separate top-bar slice.

Run the Python equivalent of the site's colour rule with
`python3 tools/check_colours.py`. `tests/test_colours.py` runs it against the
source templates and a freshly rendered report, and verifies that injected CSS,
HTML/SVG attributes and script colour values fail. Only vendored token CSS and
the marked runtime token block may contain colour literals.
