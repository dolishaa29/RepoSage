WORKFLOW_FILE = ".github/workflows/gitaudit-tests.yml"

# ubuntu-latest already has Python, Node, Java, Go, Ruby, PHP, .NET and Rust installed,
# so one workflow works for every language: it only runs the test command the AI gave.
# It runs on pushes to gitaudit/... branches only, so it never touches the repo's normal CI.
TEMPLATE = """name: gitAudit tests
on:
  push:
    branches: ["gitaudit/**"]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run test
        run: |
COMMAND
"""


def make_workflow(test_command: str):
    # indent every line so it sits inside "run: |" in the YAML
    command = "\n".join("          " + line for line in test_command.splitlines())
    return TEMPLATE.replace("COMMAND", command)
