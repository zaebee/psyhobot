import logging
import apiai
import aiovk
import ujson

import requests
import aiohttp
import asyncio
import async_timeout

from aiovk import TokenSession, API
from aiovk.longpoll import LongPoll
from aiovk.drivers import HttpDriver

from ..models import User

logger = logging.getLogger(__name__)


def get_bits(n):
    b = []
    while n:
        b = [n & 1] + b
        n >>= 1
    return b or [0]


def get_flags(mask):
    flags = [
        'UNREAD',
        'OUTBOX',
        'REPLIED',
        'IMPORTANT',
        'CHAT',
        'FRIENDS',
        'SPAM',
        'DELЕTЕD',
        'FIXED',
        'MEDIA',
        'HIDDEN',
    ]
    bits = get_bits(mask)
    result = map(lambda x, y: (x, y), flags[::-1][-len(bits):], bits)
    return dict(result)


class VKChat:

    def __init__(self, *args, **kwargs):
        self.loop = asyncio.get_event_loop()
        self.vk_token = kwargs.get('vk_token', 0)
        self.ai_token = kwargs.get('ai_token', 0)
        self.peer_id = kwargs.get('peer_id', 0)

        self.session = aiovk.TokenSession(
            access_token=self.vk_token,
            driver=HttpDriver(loop=self.loop)
        )
        self.vk = aiovk.API(self.session)
        self.ai = apiai.ApiAI(self.ai_token)

    @asyncio.coroutine
    def get_answer(self, user_id, message):
        request = self.ai.text_request()
        request.query = message
        request.session_id = user_id
        response = request.getresponse()
        data = ujson.loads(response.read())
        return data

    @asyncio.coroutine
    def send_answer(self, user_id, answer):
        result = answer['result']
        action = result['action']
        params = result['parameters']
        message = result['fulfillment']['speech']

        size = 5 if 'where-is-party-next' in action else 1
        offset = 1 if 'where-is-party-next' in action else 0
        if 'where-is-party-next' in action:
            contexts = result['contexts']
            if len(contexts):
                params = contexts[0]['parameters']

        print('params %s' % params)
        # send `welcome` message
        if message:
            message = yield from self.send_message(user_id, message)
        events = yield from self.search_events(**params)

        if events and events.hits.total:
            for event in events[offset:size]:
                attach_photo = getattr(event, 'attach', '')
                place = event.place
                if event.image and not attach_photo:
                    # TODO upload photo to vk server
                    image = requests.get(event.image, stream=True)
                    files = {'photo': ('photo.jpg', image.content)}
                    server = yield from self.vk(
                        'photos.getMessagesUploadServer',
                        peer_id=user_id
                    )
                    image_response = requests.post(
                        server['upload_url'],
                        files=files
                    )
                    try:
                        image_response_json = image_response.json()
                        response = yield from self.vk(
                            'photos.saveMessagesPhoto',
                            hash=image_response_json['hash'],
                            photo=image_response_json['photo'],
                            server=image_response_json['server'],
                        )
                        print(response)
                    except:
                        response = None
                    ###
                    images = response
                    if images:
                        image = images[0]
                        attach_photo = 'photo%s_%s' % (
                            image['owner_id'],
                            image['id']
                        )
                        event.attach = attach_photo
                        event.save()

                kwargs = {
                    'attachment': attach_photo
                }
                if place.lat and place.lng:
                    kwargs['lat'] = str(place.lat)
                    kwargs['long'] = str(place.lng)

                # TODO serialize dates/places message answer
                dates = event.dates[0] if event.dates else {}
                start = end = ''
                if 'start_date' in dates:
                    start = dates.start_date.strftime('%d.%m.%Y %H:%M')
                    start = 'Начало - %s' % start
                if 'end_date' in dates:
                    end = dates.end_date.strftime('%d.%m.%Y %H:%M')
                    end = 'Окончание - %s' % end
                place = 'Место - %s' % event.place.title
                text = '%s \n %s \n %s \n %s \n %s' % (
                    event.title, place,
                    start, end,
                    (event.description or '')[:100]
                )
                try:
                    yield from self.send_message(
                        user_id,
                        text,
                        **kwargs
                    )
                except:
                    print('error %s' % kwargs)
        return events

    @asyncio.coroutine
    def search_events(self, **kwargs):
        if any(kwargs.values()):
            date = kwargs.get('date', [])
            query = kwargs.get('genre', '')
            category = kwargs.get('category', '')
            # TODO return messages
            events = []
            return events

    @asyncio.coroutine
    def parse_message_updates(self, code, *args):
        user_id = None
        message = ''
        print('code', code, args)
        if code in [1, 2, 3, 4]:
            # `message_id` as first argument
            message_id = args[0]
            if code == 4:
                flags = get_flags(args[1])
                # got NOT outbox messages
                if not flags.get('OUTBOX', 0):
                    print('INBOX message_id', message_id)
                    user_id, timestamp, _, message, attachments = args[2:]
        return user_id, message

    @asyncio.coroutine
    def send_message(self, user_id, message, **kwargs):
        return self.vk(
            'messages.send',
            user_id=user_id,
            message=message,
            domain='whatwhere.world',
            peer_id=self.peer_id,
            **kwargs
        )

    @asyncio.coroutine
    def wait_user_input(self):
        # listen long poll user chat session
        longpoll = LongPoll(self.vk, mode=2)
        while True:
            result = yield from longpoll.wait()
            for update in result.get('updates', []):
                user_id, message = yield from self.parse_message_updates(*update)
                if user_id and message:
                    answer = yield from self.get_answer(user_id, message)
                    print('answer: %s' % answer)
                    events = yield from self.send_answer(user_id, answer)
            print('result: %s' % result)

    @asyncio.coroutine
    def get_user_token(self, user_id, **kwargs):
        queryset = User.query.filter_by(user_id=user_id)
        if queryset.count():
            queryset = queryset.first()
            # TODO check if not expired
            return queryset.extra_data['access_token']

    @asyncio.coroutine
    def observe_chat(self):
        task = self.loop.create_task(self.wait_user_input())
        return self.loop.run_until_complete(task)
