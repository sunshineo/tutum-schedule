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

    while True:
        schedule.run_pending()
        time.sleep(1)
