import time
import logging

from happyly import Handler, Executor


logging.basicConfig(level=logging.INFO)


def handle_my_message(message: dict):
    try:
        print(message['info'])
        return {'a': '42'}
    except Exception:
        print('Something went wrong')


class MyHandler(Handler):
    def handle(self, message):
        print(message['info'])
        return {'a': '42'}

    def on_handling_failed(self, message, error):
        print('Something went wrong')


if __name__ == '__main__':
    executor = Executor(handler=handle_my_message)
    executor.run({'info': 'Hello, world!'})
    print('-' * 10)
    time.sleep(1)
    print('Result is', executor.run_for_result({'info': 'another message'}))
    print('-' * 10)
    time.sleep(1)
    executor.run({'incorrect': 'oops'})

    publishing_executor = Executor(
        handler=lambda x: {'a': 2 * x['a']}, publisher=lambda x: print(x)
    )
    publishing_executor.run({'a': 4})
