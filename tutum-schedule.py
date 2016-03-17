import functools
import schedule
import time
import dockercloud
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
    Wrapper function to start a stopped dockercloud Service by its UUID.
    """
    log.info("Start service: " + note)
    log.info("Get service by uuid: " + uuid)
    service = dockercloud.Service.fetch(uuid)
    log.info("Successfully got the service.")
    log.info("Starting the service.")
    service.start()
    log.info("Successfully started the service.")

@catch_exceptions
def stop_service(uuid, note):
    """
    Wrapper function to stopped a dockercloud Service by its UUID.
    """
    log.info("Stop service: " + note)
    log.info("Get service by uuid: " + uuid)
    service = dockercloud.Service.fetch(uuid)
    log.info("Successfully got the service.")
    log.info("Stopping the service.")
    service.stop()
    log.info("Successfully stopped the service.")

@catch_exceptions
def create_service(**kwargs):
    """
    Wrapper function to create a new dockercloud Service.

    For possible parameters, see https://docs.dockercloud.co/v2/api/?python#create-a-new-service.
    """
    service = dockercloud.Service.create(**kwargs)
    service.save()
    service.start()

if __name__ == "__main__":
    """
    Add your own scheduled jobs here.
    See https://github.com/dbader/schedule for schedule syntax.

    Examples:

    If you have already created a Service on dockercloud with the UUID of 
    '2463a0c3-bacd-4195-8493-bcbb49681f4a', you can start it every
    hour with:
    schedule.every().hour.do(start_service, '2463a0c3-bacd-4195-8493-bcbb49681f4a')

    If you would like to create a Service to be run every day at 2:15 AM, set
    the schedule with:
    schedule.every(5).day.at("2:15").do(create_service, 
                                        image='user/my-job', 
                                        name='created',
                                        autodestroy="ALWAYS")
    """

    # gordonsun.me mariadb backup
    schedule.every(10).days.do(start_service, 'e0c656be-89f6-42d4-81e8-8ebba44c19f2', 'gordonsun.me mariadb backup every 10 day')

    # craigsmenu prod to dev sync
    schedule.every().day.do(start_service, 'ce61d5c7-fe9d-4535-a17b-4f3edac2f134', 'craigsmenu prod to dev sync daily')
    # craigsmenu prod backup
    schedule.every().day.do(start_service, '7e1857be-99e4-4581-bb6f-647d4d3d9c6e', 'craigsmenu prod backup daily')

    # nolostdogs.org crawler JavaScript
    # This service occationally just cannot stop. So we try to stop it every time before we try to start it.
    schedule.every(15).minutes.do(stop_service, '0cdbba7a-ce6b-4ca3-8f08-8135f0cede71', 'nld-crawler-js stop (may fail) every 15 minutes')
    schedule.every(15).minutes.do(start_service, '0cdbba7a-ce6b-4ca3-8f08-8135f0cede71', 'nld-crawler-js start every 15 minutes')
    # nolostdogs.org crawler Python
    schedule.every(15).minutes.do(stop_service, 'af40dbce-71ab-42c4-9c06-fdb1ac933552', 'nld-crawler-python stop (may fail) every 15 minutes')
    schedule.every(15).minutes.do(start_service, 'af40dbce-71ab-42c4-9c06-fdb1ac933552', 'nld-crawler-python every 15 minutes')

    while True:
        schedule.run_pending()
        time.sleep(1)
