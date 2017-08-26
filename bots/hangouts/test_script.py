import argparse
import asyncio
import logging
import os

import hangups
import appdirs

# conversation_id = "108293341917192524905"
conversation_id = "The Peculiar Group"
message_text = "Hejsan detta är ifrån min bot!"

def run_example(example_coroutine, *extra_args):
    """Run a hangups example coroutine.
    Args:
        example_coroutine (coroutine): Coroutine to run with a connected
            hangups client and arguments namespace as arguments.
        extra_args (str): Any extra command line arguments required by the
            example.
    """
    args = _get_parser(extra_args).parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARNING)
    # Obtain hangups authentication cookies, prompting for credentials from
    # standard input if necessary.
    cookies = hangups.auth.get_auth_with_args("email@gmail.com", "password", "refresh_token.txt")
    client = hangups.Client(cookies)
    task = asyncio.async(_async_main(example_coroutine, client, args))
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        task.cancel()
        loop.run_forever()
    finally:
        loop.close()


def _get_parser(extra_args):
    """Return ArgumentParser with any extra arguments."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    dirs = appdirs.AppDirs('hangups', 'hangups')
    default_token_path = os.path.join(dirs.user_cache_dir, 'refresh_token.txt')
    parser.add_argument(
        '--token-path', default=default_token_path,
        help='path used to store OAuth refresh token'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='log detailed debugging messages'
    )
    for extra_arg in extra_args:
        parser.add_argument(extra_arg, required=True)
    return parser

@asyncio.coroutine
def _async_main(example_coroutine, client, args):
    """Run the example coroutine."""
    # Spawn a task for hangups to run in parallel with the example coroutine.
    task = asyncio.async(client.connect())

    # Wait for hangups to either finish connecting or raise an exception.
    on_connect = asyncio.Future()
    client.on_connect.add_observer(lambda: on_connect.set_result(None))
    done, _ = yield from asyncio.wait(
        (on_connect, task), return_when=asyncio.FIRST_COMPLETED
    )
    yield from asyncio.gather(*done)

    # Run the example coroutine. Afterwards, disconnect hangups gracefully and
    # yield the hangups task to handle any exceptions.
    try:
        yield from example_coroutine(client, args)
    finally:
        yield from client.disconnect()
        yield from task

@asyncio.coroutine
def sync_recent_conversations(client, _):
    user_list, conversation_list = (
        yield from hangups.build_user_conversation_list(client)
    )
    all_users = user_list.get_all()
    all_conversations = conversation_list.get_all(include_archived=True)

    print('{} known users'.format(len(all_users)))
    for user in all_users:
        print('    {}: {}'.format(user.full_name, user.id_.gaia_id))

    print('{} known conversations'.format(len(all_conversations)))
    for conversation in all_conversations:
        if conversation.name:
            name = conversation.name
        else:
            name = 'Unnamed conversation ({})'.format(conversation.id_)
        print('    {}'.format(name))

@asyncio.coroutine
def send_message(client, args):
    print("Trying to send message: \"%s\" to conversation: %s"%(message_text, conversation_id))
    request = hangups.hangouts_pb2.SendChatMessageRequest(
        request_header=client.get_request_header(),
        event_request_header=hangups.hangouts_pb2.EventRequestHeader(
            conversation_id=hangups.hangouts_pb2.ConversationId(
                id=conversation_id
            ),
            client_generated_id=client.get_client_generated_id(),
        ),
        message_content=hangups.hangouts_pb2.MessageContent(
            segment=[
                hangups.ChatMessageSegment(message_text).serialize()
            ],
        ),
    )
    yield from client.send_chat_message(request)

if __name__ == '__main__':
    # run_example(sync_recent_conversations)
    run_example(send_message)

