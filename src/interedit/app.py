import os
import pathlib
import subprocess
import typing as t

import attr
import fuzzywuzzy.process
import hyperlink
import marshmallow
import pyramid.config
import pyramid.response
import pyramid.view
import requests

import interedit.github
import interedit.schemas


@attr.dataclass(frozen=True)
class AppConfig:
    username: str
    token: str


CONFIG = AppConfig(os.environ["GITHUB_USERNAME"], os.environ["GITHUB_TOKEN"])


RST = t.TypeVar("RST", bound=str)
HTML = t.TypeVar("HTML", bound=str)


class URLField(marshmallow.fields.String):
    def _deserialize(self, value, *a, **kw) -> hyperlink.URL:
        return hyperlink.URL.from_text(value)


@attr.dataclass(frozen=True)
class EditRequest:
    rendered_rst_url: hyperlink.URL = attr.ib(
        metadata={"marshmallow_field": URLField()}
    )
    rendered_html_url: hyperlink.URL = attr.ib(
        metadata={"marshmallow_field": URLField()}
    )
    index: int
    old_html: str
    new_html: str


@attr.dataclass(frozen=True)
class RenderedDocument:
    # TODO This class needs a better name.
    # TODO Make this feel more like `hyperlink.URL`.
    rendered_url: hyperlink.URL

    @property
    def owner(self):
        return self.rendered_url.path[0]

    @property
    def repository(self):
        return self.rendered_url.path[1]

    @property
    def branch(self):
        return self.rendered_url.path[3]

    @property
    def path(self):
        return hyperlink.URL.from_text("/".join(self.rendered_url.path[4:]))

    @property
    def raw_url(self):
        return self.rendered_url.replace(
            host="raw.githubusercontent.com",
            path=[self.owner, self.repository, self.branch] + list(self.path.path),
        )

    @property
    def api_url(self):
        url = hyperlink.URL.from_text("https://api.github.com/repos")
        return url.child(self.owner).child(self.repository)

    @classmethod
    def from_text(cls, text):
        return cls(hyperlink.URL.from_text(text))


def parse_rendered_url(url: hyperlink.URL):
    return RenderedDocument(url)


edit_request_schema = interedit.schemas.schema(EditRequest)


def html2rst(html: HTML) -> RST:
    return subprocess.run(
        ["pandoc", "-f", "html", "-t", "rst"],
        input=html.encode(),
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode()


def apply_edit(original_markup: RST, edit_request: EditRequest) -> RST:
    paragraphs = original_markup.split("\n\n")
    old_rst: RST = html2rst(edit_request.old_html)
    paragraph, _ = fuzzywuzzy.process.extractOne(old_rst, paragraphs)
    new_rst: RST = html2rst(edit_request.new_html)
    whole_file_rst = original_markup.replace(paragraph, new_rst)
    return t.cast(RST, whole_file_rst)


@pyramid.view.view_config(renderer="json")
def handle_edit_request(request):
    edit_request = edit_request_schema.load(dict(request.json_body))
    rendered_spec = parse_rendered_url(edit_request.rendered_rst_url)
    raw_body = requests.get(rendered_spec.raw_url).text
    edited = apply_edit(raw_body, edit_request)
    interedit.github.request_edit(CONFIG.username, CONFIG.token, rendered_spec, edited)
    return pyramid.response.Response("ok")


def main():
    with pyramid.config.Configurator() as config:
        config.add_route("hello", "/")
        config.add_view(handle_edit_request, route_name="hello")
        app = config.make_wsgi_app()
        return app


if __name__ == "__main__":
    import wsgiref.simple_server

    wsgiref.simple_server.make_server("0.0.0.0", 6543, main()).serve_forever()
