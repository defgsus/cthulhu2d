

class LogMixin:

    LOG_LEVEL = 0

    def log(self, *args):
        if args:
            level = 1
            if len(args) > 1 and isinstance(args[0], int):
                level = args[0]
                args = args[1:]

            if level <= self.LOG_LEVEL:
                print(f"log: {self.__class__.__name__}:", *args)
