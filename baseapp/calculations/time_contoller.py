import time
from django.conf import settings


def time_controller(method):
    def wrapper(*args, **kwargs):
        process_name = method.__name__
        processing_start = time.time()
        if not settings.PRODACTION_MODE:
            print(f"\nStart {process_name}")
        rez = method(*args, **kwargs)
        # try:
        #     rez = method(*args, **kwargs)
        # except BaseException as err:
        #     self.reg_error(
        #         f"Cannot {process_name}: {err=}, {type(err)=}")
        #     rez = None

        if not settings.PRODACTION_MODE:
            processing_time = round(
                time.time() - processing_start, 2)
            print(f"{process_name}, time={processing_time} sec ")

        return rez

    return wrapper
