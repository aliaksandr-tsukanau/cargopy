import time
import logging

from happyly import Handler, Executor


logging.basicConfig(level=logging.INFO)


class MyHandler(Handler):
    def handle(self, message):
        print(message['info'])
        return {'a': '42'}

    def on_handling_failed(self, message, error):
        print('Incorrect message')


if __name__ == '__main__':
    executor = Executor(handler=MyHandler())
    executor.run({'info': 'Hello, world!'})
    print('-' * 10)
    time.sleep(1)
    print('Result is', executor.run_for_result({'info': 'another message'}))
    print('-' * 10)
    time.sleep(1)
    executor.run({'incorrect': 'oops'})
