import base64
import os
import pathlib
import random
import string
import time
import typing as t

import attr
import hyperlink
import requests

import interedit.app


SHA = t.TypeVar("SHA", bound=str)


def make_get_branch_url(doc: interedit.app.RenderedDocument) -> hyperlink.URL:
    url = hyperlink.URL.from_text("https://api.github.com/repos")
    return (
        url.child(doc.owner).child(doc.repository).child("branches").child(doc.branch)
    )


def get_last_commit(
    session: requests.Session, doc: interedit.app.RenderedDocument
) -> SHA:
    url = make_get_branch_url(doc)
    response = session.get(url)
    response.raise_for_status()
    data = response.json()
    return data["commit"]["sha"]


def make_file_content_url(doc) -> hyperlink.URL:
    url = doc.api_url.child("contents")
    url = url.replace(path=url.path + doc.path.path)
    return url


def get_file_sha(
    session: requests.Session, doc: interedit.app.RenderedDocument, branch: str
) -> SHA:
    response = session.get(make_file_content_url(doc), json={"ref": branch})
    return response.json()["sha"]


def edit_file(
    session: requests.Session,
    doc: interedit.app.RenderedDocument,
    old_file_sha: SHA,
    new_branch: str,
    body: str,
) -> SHA:
    url = make_file_content_url(doc)
    data = {
        "message": "Interactive edit",
        "content": base64.b64encode(body.encode()).decode(),
        "sha": old_file_sha,
        "branch": new_branch,
    }
    response = session.put(url, json=data)
    response.raise_for_status()
    return response.json()["commit"]["sha"]


def create_branch(
    session: requests.Session, doc: interedit.app.RenderedDocument, parent_sha: SHA
) -> str:
    url = doc.api_url.child("git").child("refs")
    name = "interdoc/" + "".join(random.choices(string.ascii_lowercase, k=10))
    session.post(
        url, json={"ref": f"refs/heads/{name}", "sha": parent_sha}
    ).raise_for_status()
    return name


def fork_repository(session, doc) -> interedit.app.RenderedDocument:
    r = session.post(doc.api_url.child("forks"))
    html_url = hyperlink.URL.from_text(r.json()["html_url"])
    url = html_url.replace(path=html_url.path + ("blob", doc.branch) + doc.path.path)
    new_doc = interedit.app.RenderedDocument(url)
    while True:
        # TODO Use async.
        r = session.get(new_doc.api_url)
        if r.status_code == 404:
            time.sleep(30)
        elif r.status_code == 200:
            return new_doc
        else:
            r.raise_for_status()


def create_pull_request(session, upstream, fork, head_branch):
    data = {
        "base": upstream.branch,
        "head": f"{fork.owner}:{head_branch}",
        "title": "Interactive edit",
    }
    session.post(upstream.api_url.child("pulls"), json=data).raise_for_status()


def main(username, token, upstream_document, text):

    sess = requests.Session()
    sess.auth = username, token
    forked_document = fork_repository(sess, upstream_document)
    last_commit_sha = get_last_commit(sess, forked_document)
    new_branch_name = create_branch(sess, forked_document, last_commit_sha)
    old_file_sha = get_file_sha(sess, forked_document, new_branch_name)
    edit_file(sess, forked_document, old_file_sha, new_branch_name, text)
    create_pull_request(sess, upstream_document, forked_document, new_branch_name)


if __name__ == "__main__":
    main(
        os.environ["GITHUB_USERNAME"],
        os.environ["GITHUB_TOKEN"],
        upstream_document=interedit.app.RenderedDocument.from_text(
            "https://github.com/interdoc-edit-bot/hyperlink/blob/master/docs/api.rst"
        ),
        text="Hello world",
    )
