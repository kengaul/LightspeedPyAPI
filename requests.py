class Response:
    def __init__(self, status_code=200, content=b''):
        self.status_code = status_code
        self.content = content
    def json(self):
        return {}

def get(*args, **kwargs):
    return Response()
