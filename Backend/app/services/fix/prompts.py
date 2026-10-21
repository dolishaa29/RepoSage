from langchain_core.prompts import PromptTemplate

from ...core.llm import model
from ...schemas.fix import FixResult

prompt = PromptTemplate(
    template="""You are a senior software engineer. Fix only this one problem in the file below.

Problem: {title}
Line: {line}
Why it is a problem: {explanation}
How to fix it: {suggestion}

Change only what is needed for this problem and keep everything else exactly the same.
Return the complete fixed file.

Also write a unit test for the fix:
- use the usual test framework of this language and repo (pytest, Jest, JUnit, go test, RSpec, PHPUnit, xUnit, cargo test, ...)
- put the test where this language expects it (for example Go: same folder as the file, named *_test.go)
- test_command: one shell command, run from the repo root on ubuntu-latest, that installs what is needed and runs only this test
- do not use the network or a real database
If this file cannot have a unit test (config, docs, ...), return empty test_file, test_code and test_command.

File: {file}
{code}""",
    input_variables=["title", "line", "explanation", "suggestion", "file", "code"],
)

retry_prompt = PromptTemplate(
    template="""You are a senior software engineer. Your fix for "{title}" failed its tests.

File: {file}
{code}

Test file: {test_file}
{test_code}

Test command: {test_command}

Test output:
{log}

Fix the code, the test or the test command so the tests pass. The fix for "{title}" must stay in place.
Return the complete file, the complete test file and the test command.""",
    input_variables=["title", "file", "code", "test_file", "test_code", "test_command", "log"],
)

structured_model = model.with_structured_output(FixResult)
chain = prompt | structured_model
retry_chain = retry_prompt | structured_model
