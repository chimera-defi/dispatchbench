| config | passed | $ per pass | Claude $ per pass | median s |
|---|---|---|---|---|
| luna-low baseline | 21/35 | 0.00129 | 0.00000 | 8.5 |
| B1: no shell, plus a "list edge cases and trace the examples first" nudge | 25/35 | 0.00097 | 0.00000 | 8.6 |
| B2: B1 plus a detailed reasoning summary | 19/35 | 0.00116 | 0.00000 | 8.9 |
| C: shell on, told to test its code before answering | 29/35 | 0.00364 | 0.00000 | 21.9 |
| D: luna-medium, stripped harness | 21/35 | 0.00120 | 0.00000 | 8.4 |
| D: luna-high, stripped harness | 31/35 | 0.00105 | 0.00000 | 13.2 |
| E (original run, prompt not kept): luna-low answer, then haiku-low reviews and repairs it | 35/35 | 0.00348 | 0.00271 | 27.4 |
| F: haiku-low writes a plan, luna-low builds from it | 30/35 | 0.00336 | 0.00231 | 22.1 |
| F: haiku-low writes a plan, luna-high (stripped harness) builds from it | 31/35 | 0.00357 | 0.00223 | 27.4 |
| G: luna-high (stripped) builds; haiku-low repairs only if the statement's examples fail | 32/35 | 0.00135 | 0.00030 | 10.6 |
| G: luna-high (stripped) builds; luna-high retries only if the statement's examples fail | 32/35 | 0.00115 | 0.00000 | 10.6 |
| G: luna-low builds; haiku-low repairs only if the statement's examples fail | 34/35 | 0.00216 | 0.00134 | 7.9 |
| G: luna-high (stripped) builds; haiku-low reviews every answer, as in E | 35/35 | 0.00348 | 0.00252 | 26.1 |
| G: luna-low builds; haiku-low reviews every answer (arm E rerun from committed code) | 34/35 | 0.00391 | 0.00308 | 23.1 |
| G: sol61-high builds; haiku-low repairs only if the statement's examples fail | 35/35 | 0.02181 | 0.00000 | 32.7 |
| G: astra-medium builds; haiku-low repairs only if the statement's examples fail | 35/35 | 0.08680 | 0.00000 | 21.4 |
| haiku-low | 32/35 | 0.00157 | 0.00157 | 13.1 |
| haiku-medium | 35/35 | 0.00192 | 0.00192 | 14.8 |
| haiku-high | 35/35 | 0.00347 | 0.00347 | 17.4 |
| sonnet-medium | 35/35 | 0.01530 | 0.01530 | 11.4 |
| sol61-medium | 33/35 | 0.01785 | 0.00000 | 25.6 |
| sol61-high | 35/35 | 0.02218 | 0.00000 | 33.4 |
| astra-medium | 35/35 | 0.08642 | 0.00000 | 26.0 |
| sol56-high | 35/35 | 0.05068 | 0.00000 | 19.5 |
| luna56-high | 32/35 | 0.00360 | 0.00000 | 14.1 |
| luna56-low | 29/35 | 0.00248 | 0.00000 | 12.3 |
