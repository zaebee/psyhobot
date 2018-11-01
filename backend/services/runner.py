import logging

from .vk import VKChat

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# TODO remove hard coded tokens
VK_ACCESS_TOKEN = '861765b84b9a76c19ddb6d9fbfca27e1d5fb20201ffb33f121cb35e0895f3ddbc87f4b692a71129ec5484'
PEER_ID = -155406641

AI_ACCESS_TOKEN = '490d6a1fb84141cda768a766ab1173a8'
VK_ACCESS_TOKEN = 'da71f9d32db98bf4bf9cdfd9953d68d42d48eff54d475e446f47345162fc3c3788bed82a48fdaa972fa9f'
PEER_ID = -173396634


def vk(*args):
    """
    Example: `./manage.py vk --script-args <peer_id> <vk_token> <dialog_token>`
    """
    # TODO pass args via params
    if len(args) == 3:
        peer_id = args[0]
        vk_token = args[1]
        ai_token = args[2]
    else:
        peer_id = PEER_ID
        vk_token = VK_ACCESS_TOKEN
        ai_token = AI_ACCESS_TOKEN

    chat = VKChat(
        peer_id=peer_id,
        vk_token=vk_token,
        ai_token=ai_token
    )
    gen = chat.observe_chat()
    logger.debug('run vk bot')
    while True:
        # TODO catch TimeoutError
        try:
            next(gen)
        except:
            gen = chat.observe_chat()
            next(gen)


def tlg(*args):
    """
    Example: `./manage.py tlg --script-args <peer_id> <vk_token> <dialog_token>`
    """
    # chat = TLGChat(
    #     peer_id=peer_id,
    #     tlg_token=vk_token,
    #     ai_token=ai_token
    # )
    # gen = chat.observe_chat()
    gen = lambda x: x
    logger.debug('run tlg bot')
    while True:
        # TODO catch TimeoutError
        try:
            next(gen)
        except StopIteration:
            # gen = chat.observe_chat()
            next(gen)
