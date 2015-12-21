import functools
import schedule
import time
import tutum
import logging
import sys

log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)

def catch_exceptions(job_func):
    @functools.wraps(job_func)
    def wrapper(*args, **kwargs):
        try:
            job_func(*args, **kwargs)
        except:
            import traceback
            log.warn(traceback.format_exc())
    return wrapper

@catch_exceptions
def start_service(uuid, note):
    """
    Wrapper function to start a stopped Tutum Service by its UUID.
    """
    log.info("Start service: " + note)
    log.info("Get service by uuid: " + uuid)
    service = tutum.Service.fetch(uuid)
    log.info("Successfully got the service.")
    log.info("Starting the service.")
    service.start()
    log.info("Successfully started the service.")

@catch_exceptions
def stop_service(uuid, note):
    """
    Wrapper function to stopped a Tutum Service by its UUID.
    """
    log.info("Stop service: " + note)
    log.info("Get service by uuid: " + uuid)
    service = tutum.Service.fetch(uuid)
    log.info("Successfully got the service.")
    log.info("Stopping the service.")
    service.stop()
    log.info("Successfully stopped the service.")

@catch_exceptions
def create_service(**kwargs):
    """
    Wrapper function to create a new Tutum Service.

    For possible parameters, see https://docs.tutum.co/v2/api/?python#create-a-new-service.
    """
    service = tutum.Service.create(**kwargs)
    service.save()
    service.start()

if __name__ == "__main__":
    """
    Add your own scheduled jobs here.
    See https://github.com/dbader/schedule for schedule syntax.

    Examples:

    If you have already created a Service on Tutum with the UUID of 
    '2463a0c3-bacd-4195-8493-bcbb49681f4a', you can start it every
    hour with:
    schedule.every().hour.do(start_service, '2463a0c3-bacd-4195-8493-bcbb49681f4a')

    If you would like to create a Service to be run every day at 2:15 AM, set
    the schedule with:
    schedule.every(5).day.at("2:15").do(create_service, 
                                        image='tutum.co/user/my-job', 
                                        name='created',
                                        autodestroy="ALWAYS")
    """

    # gordonsun.me mariadb backup
    schedule.every().day.do(start_service, 'fbb5646e-f5b6-428d-8846-aff09469349f', 'gordonsun.me mariadb backup daily')

    # craigsmenu prod to dev sync
    schedule.every().day.do(start_service, '19ba2002-8a97-414c-a5da-c8fd3d42412a', 'craigsmenu prod to dev sync daily')
    # craigsmenu prod backup
    schedule.every().day.do(start_service, 'eb3aeb88-c363-4bad-8060-7fbcb5d50ca7', 'craigsmenu prod backup daily')

    # nolostdogs.org crawler JavaScript
    # This service occationally just cannot stop. So we try to stop it every time before we try to start it.
    schedule.every(15).minutes.do(stop_service, 'a4a376be-24df-4668-91fd-a0ba56eacc70', 'nld-crawler-js stop (may fail) every 15 minutes')
    schedule.every(15).minutes.do(start_service, 'a4a376be-24df-4668-91fd-a0ba56eacc70', 'nld-crawler-js start every 15 minutes')
    # nolostdogs.org crawler Python
    schedule.every(15).minutes.do(start_service, '7b958fe9-dfa4-4dad-acdc-5d8c7a212032', 'nld-crawler-python every 15 minutes')

    while True:
        schedule.run_pending()
        time.sleep(1)
