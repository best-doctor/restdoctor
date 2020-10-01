from rest_framework.response import Response


def unpacked_error_message(response: Response) -> str:
    return response.json()['errors'][0]['message']
