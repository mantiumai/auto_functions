from auto_functions.common.services import create_app

app = create_app(
    title="Auto Functions API",
    description="Use OpenAPI specs to automatically generate OpenAI function tool parameters",
)
