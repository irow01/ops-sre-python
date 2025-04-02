from rest_framework.response import Response


class APIResponse(Response):
    def __init__(self, data_status, data, results=None, headers=None, status=None, **kwargs):
        data = {
            'code': data_status,
            'data': data,
        }
        if results:
            data['results'] = results
        data.update(kwargs)
        super().__init__(data=data, headers=headers, status=status)
