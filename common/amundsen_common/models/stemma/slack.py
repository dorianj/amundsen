import attr

from marshmallow3_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class SlackMessage:
    key: str = attr.ib()
    channel: str = attr.ib()
    channel_id: str = attr.ib()
    team: str = attr.ib()
    text: str = attr.ib()
    thread_ts: str = attr.ib()
    ts: str = attr.ib()
    type: str = attr.ib()
    author: str = attr.ib()


class SlackMessageSchema(AttrsSchema):
    class Meta:
        target = SlackMessage
        register_as_scheme = True
