from types import SimpleNamespace
from unittest.mock import patch

import httpx
import pytest
from fastapi import HTTPException

from app.services import github_service as gh
from app.services.agent import code_index, tools
from app.services.fix import fix_service, github_files


def response(code, **kwargs):
    return httpx.Response(code, request=httpx.Request("GET", "http://x"), **kwargs)


def test_github_timeout_gives_502():
    with patch("httpx.request", side_effect=httpx.ReadTimeout("x")):
        with pytest.raises(HTTPException) as error:
            gh.call_github("t", "/user")
    assert error.value.status_code == 502


@pytest.mark.parametrize("code,text", [(401, "connect GitHub again"), (404, "status 404")])
def test_github_error_messages(code, text):
    with patch("httpx.request", return_value=response(code)):
        with pytest.raises(HTTPException) as error:
            gh.call_github("t", "/x")
    assert text in error.value.detail


def test_repos_are_read_from_all_pages():
    def pages(method, url, **kwargs):
        count = 100 if "&page=1" in url else 7
        return response(200, json=[{"id": i} for i in range(count)])

    with patch("httpx.request", side_effect=pages):
        assert len(gh.get_account_repos("t")) == 107


def test_unverified_email_is_refused():
    with patch.object(gh, "call_github", return_value=[{"primary": True, "verified": False, "email": "a@b.co"}]):
        with pytest.raises(HTTPException):
            gh.get_email("t")


def test_code_search_stays_in_this_repo():
    seen = {}

    def search(method, url, **kwargs):
        seen.update(kwargs["params"])
        return response(200, json={"items": []})

    with patch("httpx.request", side_effect=search):
        gh.search_github_code("t", "me/mine", 'x" repo:other/secret')
    assert seen["q"] == '"x  repo:other/secret" repo:me/mine'


@pytest.mark.parametrize("path", ["../../other/secret", "./.github/workflows/x.yml", ".github/x.yml", "a//b"])
def test_unsafe_paths_cannot_be_changed(path):
    context = tools.Context(token="t", repo="me/mine", ref="abc")
    assert tools.check_path(context, path) is not None


def test_normal_path_can_be_changed():
    assert tools.check_path(tools.Context(token="t", repo="me/mine", ref="abc"), "src/a.py") is None


def test_edit_keeps_windows_line_endings():
    context = tools.Context(token="t", repo="me/mine", ref="abc", originals={"a.py": "one\r\ntwo\r\nthree\r\n"})
    result = tools.edit_file.func("a.py", "one\ntwo", "ONE\nTWO", SimpleNamespace(context=context))
    assert result == "Edited a.py" and context.changes["a.py"] == "ONE\r\nTWO\r\nthree\r\n"


def test_embedding_waits_when_the_limit_is_hit():
    state = {"calls": 0}
    waits = []

    def embed(texts, task_type):
        state["calls"] += 1
        if state["calls"] == 2:
            raise RuntimeError("429 RESOURCE_EXHAUSTED")
        return [[0.0]] * len(texts)

    chunks = [SimpleNamespace(path="p", content=str(i), embedding=None) for i in range(60)]
    with patch.object(type(code_index.embeddings), "embed_documents", side_effect=embed), patch.object(code_index.time, "sleep", waits.append):
        code_index.add_embeddings(chunks)
    assert waits == [code_index.EMBED_WAIT] and all(chunk.embedding for chunk in chunks)


def test_other_embedding_errors_fail_at_once():
    with patch.object(type(code_index.embeddings), "embed_documents", side_effect=RuntimeError("bad key")):
        with pytest.raises(HTTPException) as error:
            code_index.embed_batch(["x"])
    assert error.value.status_code == 502


def test_changed_file_blocks_approve():
    fix = SimpleNamespace(repo="me/mine", changes=[{"file": "a.py", "old_code": "old"}, {"file": "t.py", "old_code": ""}])
    current = {"a.py": "old", "t.py": None}
    with patch.object(fix_service, "get_raw_file", lambda token, repo, path, ref: current[path]):
        fix_service.check_files_unchanged("t", fix, "sha")
        current["a.py"] = "newer"
        with pytest.raises(HTTPException) as error:
            fix_service.check_files_unchanged("t", fix, "sha")
    assert error.value.status_code == 409


def test_commit_keeps_the_file_mode():
    sent = {}

    def fake_call(token, path):
        if "/branches/" in path:
            return {"commit": {"sha": "h"}}
        if "/git/commits/" in path:
            return {"tree": {"sha": "tr"}}
        return {"tree": [{"path": "run.sh", "mode": "100755"}]}

    def fake_send(token, method, path, body):
        if path.endswith("/git/trees"):
            sent.update({entry["path"]: entry["mode"] for entry in body["tree"]})
        return {"sha": "s"}

    with patch.object(github_files, "call_github", fake_call), patch.object(github_files, "send_github", fake_send):
        github_files.commit_files("t", "me/mine", "b", {"run.sh": "x", "new.py": "y"}, "m")
    assert sent == {"run.sh": "100755", "new.py": "100644"}
