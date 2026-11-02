WORKFLOW_FILE = ".github/workflows/gitaudit-tests.yml"

TEMPLATE = """name: gitAudit tests
on:
  push:
    branches: ["gitaudit/**"]
jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - name: Run test
        run: |
COMMAND
"""


def make_workflow(test_command: str):
    command = "\n".join("          " + line for line in test_command.splitlines())
    workflow = TEMPLATE.replace("COMMAND", command)
    return workflow
