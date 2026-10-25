# Task tests are benchmark inputs, run in isolated workspaces by agentic.run.
# They are not importable (or meant to pass) in the harness's outer test suite.
collect_ignore = ["agentic/tasks", "pilot/agentic"]
