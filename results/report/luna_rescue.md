| config | passed | $ per pass | median s |
|---|---|---|---|
| luna-low baseline | 21/35 | 0.00129 | 8.5 |
| B1: no shell, plus a "list edge cases and trace the examples first" nudge | 25/35 | 0.00097 | 8.6 |
| B2: B1 plus a detailed reasoning summary | 19/35 | 0.00116 | 8.9 |
| C: shell on, told to test its code before answering | 29/35 | 0.00364 | 21.9 |
| D: luna-medium, stripped harness | 21/35 | 0.00120 | 8.4 |
| D: luna-high, stripped harness | 31/35 | 0.00105 | 13.2 |
| E (original run, prompt not kept): luna-low answer, then haiku-low reviews and repairs it | 35/35 | 0.00348 | 27.4 |
| F: haiku-low writes a plan, luna-low builds from it | 30/35 | 0.00336 | 22.1 |
| F: haiku-low writes a plan, luna-high (stripped harness) builds from it | 31/35 | 0.00357 | 27.4 |
| G: luna-high (stripped) builds; haiku-low repairs only if the statement's examples fail | 32/35 | 0.00135 | 10.6 |
| G: luna-high (stripped) builds; luna-high retries only if the statement's examples fail | 32/35 | 0.00115 | 10.6 |
| G: luna-low builds; haiku-low repairs only if the statement's examples fail | 34/35 | 0.00216 | 7.9 |
| G: luna-high (stripped) builds; haiku-low reviews every answer, as in E | 35/35 | 0.00348 | 26.1 |
| G: luna-low builds; haiku-low reviews every answer (arm E rerun from committed code) | 34/35 | 0.00391 | 23.1 |
| haiku-low | 32/35 | 0.00157 | 13.1 |
| sonnet-medium | 35/35 | 0.01530 | 11.4 |
