from properpy import component, config_wrapper

@component
def html(title: str, class_: str = ""):
    pass

@component
def div(content: str, style: dict = None):
    pass

RESULT = {}
@config_wrapper(RESULT)
def define_config(html_component, title: str):
    pass