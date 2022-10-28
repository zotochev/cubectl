import json
import os
import requests
from pydantic import BaseModel
from typing import Union, Protocol
import logging


__all__ = [
    "send_message",
    "SendMessageSimplified",
    "Messanger",
    "TelegramMessanger",
]


log = logging.getLogger(__file__)


class Messanger(Protocol):
    def post(self, message: Union[str, dict]):
        pass


class TelegramMessanger:
    def __init__(self, token):
        self._token = token
        self._subscribers = []

    def add_subscribers(self, ids: Union[int, str, list, tuple, set]):
        if isinstance(ids, str) and ids.count(',') != 0:
            ids = [int(x.strip()) for x in ids.split(',') if x.strip()]
        elif isinstance(ids, str):
            ids = [int(ids.strip())]
        elif isinstance(ids, int):
            ids = [ids]

        if isinstance(ids, (list, tuple, set)):
            self._subscribers = list(
                {*self._subscribers, *[int(x) for x in ids]}
            )
            return
        log.warning(f"cubectl: TelegramMessanger: no subscribers added. Ids: {ids}")

    def post(self, message: Union[str, dict]):
        if not self._token:
            log.error(f"cubectl: TelegramMessanger: token was not supplied.")
            return

        if isinstance(message, dict):
            message = self._prepare_message(message)

        for subscriber in self._subscribers:
            body = self._create_body(message=message, chat_id=subscriber)
            send_message(request=body)

    @staticmethod
    def _prepare_message(message: dict) -> str:
        return json.dumps(message, indent=2)

    @staticmethod
    def _create_body(message, chat_id):
        return {
            'chat_id': chat_id,
            'text': str(message)
        }


class SendMessageSimplified(BaseModel):
    chat_id: Union[int, str]
    text: str
    parse_mode: str = None
    disable_web_page_preview: bool = None
    disable_notification: bool = None
    allow_sending_without_reply: bool = None


def make_post_request(url: str, json_body: dict):
    r = requests.post(url=url, data=json_body)
    return r.json(), r.status_code


def send_message(request: Union[SendMessageSimplified, dict]):
    """
    request:
        {
            "chat_id": 123456798,
            "text": "Hi!"
        }
    """

    if isinstance(request, SendMessageSimplified):
        pass
    elif isinstance(request, dict):
        request = SendMessageSimplified(**request)
    else:
        raise TypeError(f'Wrong request type: {type(request)}')

    telegram_token = os.getenv('CUBECTL_TELEGRAM_TOKEN')

    if telegram_token is None:
        raise ValueError(
            f'or TELEGRAM_TOKEN({telegram_token}) '
            'were not supplied.'
        )

    telegram_url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'

    response, status_code = make_post_request(
        url=telegram_url,
        json_body=request.dict(exclude_none=True)
    )
    return response, status_code


def send_message_to_subscribers(message: Union[str, dict]):
    """

    TELEGRAM_CHAT_IDS=464332561

    :param message:
    :return:
    """
    telegram_chat_ids = os.getenv('CUBECTL_TELEGRAM_CHAT_IDS')

    if telegram_chat_ids is None:
        raise ValueError(
            f'or TELEGRAM_CHAT_IDS({telegram_chat_ids}) '
            'were not supplied.'
        )
    telegram_chat_ids = [x.strip() for x in telegram_chat_ids.split(',') if x.strip()]

    for subscriber in telegram_chat_ids:
        message_body = {
            'chat_id': subscriber,
            'text': json.dumps(message)
        }
        send_message(request=message_body)
