| config | passed | $ per pass | Claude $ per pass | median s |
|---|---|---|---|---|
| luna-low baseline | 19/35 | $0.0012 | $0 | 9.0 |
| B1: no shell, plus a "list edge cases and trace the examples first" nudge | 25/35 | $0.00097 | $0 | 8.6 |
| B2: B1 plus a detailed reasoning summary | 19/35 | $0.0012 | $0 | 8.9 |
| C: shell on, told to test its code before answering | 29/35 | $0.0036 | $0 | 21.9 |
| D: luna-medium, stripped harness | 21/35 | $0.0012 | $0 | 8.4 |
| D: luna-high, stripped harness | 31/35 | $0.0010 | $0 | 13.2 |
| E (original run, prompt not kept): luna-low answer, then haiku-low reviews and repairs it | 35/35 | $0.0035 | $0.0027 | 27.4 |
| F: haiku-low writes a plan, luna-low builds from it | 30/35 | $0.0034 | $0.0023 | 22.1 |
| F: haiku-low writes a plan, luna-high (stripped harness) builds from it | 31/35 | $0.0036 | $0.0022 | 27.4 |
| G: luna-high (stripped) builds; haiku-low repairs only if the statement's examples fail | 32/35 | $0.0014 | $0.00030 | 10.6 |
| G: luna-high (stripped) builds; luna-high retries only if the statement's examples fail | 32/35 | $0.0011 | $0 | 10.6 |
| G: luna-low builds; haiku-low repairs only if the statement's examples fail | 34/35 | $0.0022 | $0.0013 | 7.9 |
| G: luna-high (stripped) builds; haiku-low reviews every answer, as in E | 35/35 | $0.0035 | $0.0025 | 26.1 |
| G: luna-low builds; haiku-low reviews every answer (arm E rerun from committed code) | 34/35 | $0.0039 | $0.0031 | 23.1 |
| G: sol61-high builds; haiku-low repairs only if the statement's examples fail | 35/35 | $0.022 | $0 | 32.7 |
| G: astra-medium builds; haiku-low repairs only if the statement's examples fail | 35/35 | $0.087 | $0 | 21.4 |
| haiku-low | 32/35 | $0.0016 | $0.0016 | 13.1 |
| haiku-medium | 35/35 | $0.0019 | $0.0019 | 14.8 |
| haiku-high | 35/35 | $0.0035 | $0.0035 | 17.4 |
| sonnet-medium | 35/35 | $0.015 | $0.015 | 11.4 |
| sol61-medium | 33/35 | $0.018 | $0 | 25.6 |
| sol61-high | 35/35 | $0.022 | $0 | 33.4 |
| sol61-high, fast mode | 35/35 | $0.043 | $0 | 18.9 |
| astra-medium | 35/35 | $0.086 | $0 | 26.0 |
| astra-medium, fast mode | 35/35 | $0.17 | $0 | 10.9 |
| sol56-high | 35/35 | $0.051 | $0 | 19.5 |
| luna56-high | 32/35 | $0.0036 | $0 | 14.1 |
| luna56-low | 29/35 | $0.0025 | $0 | 12.3 |
