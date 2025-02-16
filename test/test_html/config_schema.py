from properpy import component, config_wrapper


@component
def html(title: str):
    pass

@component
def div():
    pass

RESULT = {}
@config_wrapper(RESULT)
def define_config(title: str):
    pass