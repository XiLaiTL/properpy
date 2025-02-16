from config_schema import html, div, define_config
from properpy import attrs

other = "wrong"
define_config(
    html(
        div(
            attrs(style={"color": "red"}),
            "Dynamic content"
        ),
        class_="container"
    ),
    title="My App"
)