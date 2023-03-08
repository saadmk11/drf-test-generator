from typing import Dict

HTTP_METHOD_STATUS_CODE_MAP: Dict[str, str] = {
    "head": "status.HTTP_200_OK",
    "options": "status.HTTP_200_OK",
    "get": "status.HTTP_200_OK",
    "post": "status.HTTP_201_CREATED",
    "put": "status.HTTP_200_OK",
    "patch": "status.HTTP_200_OK",
    "delete": "status.HTTP_204_NO_CONTENT",
}
