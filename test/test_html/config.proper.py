from config_schema import define_config
from config_schema import html, div
from properpy import attrs
from utils import add

test="hello"
html(
    div(
        attrs(style={"color": "red"}),
        "Sum: " + str(add(10, 20))
    ),
    class_="container"
)
define_config(
    html(
        div(
            attrs(style={"color": "red"}),
            "Sum: " + str(add(10, 20))
        ),
        class_="container"
    ),
    title = "define_config_title"
)
