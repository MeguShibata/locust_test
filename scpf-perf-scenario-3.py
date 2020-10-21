from locust import task, between, LoadTestShape, constant
from locust.contrib.fasthttp import FastHttpUser
import LocustUtil as Util

device_instance = {}  # keep the status of device instance


# The instance of HttpUser can represent one sensor/device.
class WindSensor(FastHttpUser):
#    wait_time = between(1, 2)
    wait_time = between(1, 2)

    # instance of task can represent one type. (One device may send various data)
    @task
    def post_input(self):

        # retrieve the dev instance
        dev_id = Util.get_id(self, "dev")
        if dev_id in device_instance:
            dev = device_instance[dev_id]
        else:
            dev = Util.get_simple_random_sensor_data(init_value=20, min=0, max=50, increment=10, error_rate=0.1)
#            dev.set_failure_rate(20, 10)
            device_instance[dev_id] = dev

        # create json data
        json_data = {
            "id": dev_id,
            "value": dev.next_int(),
            "seq": dev.get_message_seq(),
            "time": Util.get_current_time()
        }

        # send data to target
        response = self.client.post(
            path="/api/v1/resources/topics//locust/scenario/1",
            data=Util.get_json_with_size(json_data, 1000),
            auth=None,
            headers={"Authorization": "Bearer {}".format(Util.get_access_token()),
                     "Content-Type": "application/json"},
            name=Util.get_class_name(self)
        )


class TemperatureSensor(FastHttpUser):
#    wait_time = between(1, 2)
    wait_time = between(1, 2)

    # instance of task can represent one type. (One device may send various data)
    @task
    def post_input(self):

        # retrieve the dev instance
        dev_id = Util.get_id(self, "dev")
        if dev_id in device_instance:
            dev = device_instance[dev_id]
        else:
            dev = Util.get_cyclic_random_sensor_data(init_elapsed_time=0, period=300, min=-10, max=45, error_rate=0.1)
            device_instance[dev_id] = dev

        json_data = {
            "id": Util.get_id(self, "dev"),
            "value": dev.next_value(),
            "seq": dev.get_message_seq(),
            "time": Util.get_current_time()
        }

        response = self.client.post(
            path="/api/v1/resources/topics//locust/scenario/1",
            data=Util.get_json_with_size(json_data, 1000),
            auth=None,
            headers={"Authorization": "Bearer {}".format(Util.get_access_token()),
                     "Content-Type": "application/json"},
            name=Util.get_class_name(self)
        )


class BatterySensor(FastHttpUser):
#    wait_time = between(1, 2)
    wait_time = between(1, 2)

    # instance of task can represent one type. (One device may send various data)
    @task
    def post_input(self):

        # retrieve the dev instance
        dev_id = Util.get_id(self, "dev")
        if dev_id in device_instance:
            dev = device_instance[dev_id]
        else:
            dev = Util.get_diminishing_random_sensor_data(init_value=100, half_life_time=30, restart_time=120, error_rate=0.01)
            device_instance[dev_id] = dev

        # Send requests at Xth second of every minute.
#        Util.wait_until_xth_second(10)

        message = {
            "id": Util.get_id(self, "dev"),   # "dev-xxxxx-n"
            "value": dev.next_value(),
            "seq": dev.get_message_seq(),
            "time": Util.get_current_time()
        }
        json = Util.get_json_with_size(message, 1000)

        response = self.client.post(
            path="/api/v1/resources/topics//locust/scenario/1",
            data=Util.get_json_with_size(message, 1000),
            auth=None,
            headers={"Authorization": "Bearer {}".format(Util.get_access_token()),
                     "Content-Type": "application/json"},
            name=Util.get_class_name(self)
        )

#        print(response.request.headers)
#       print("{}".format(json_data))

class CustomLoadTestShape(LoadTestShape):
    time_limit = 3600
    spawn_rate = 20
    start_user = 1000
    stage_increment = 1000
    stage_duration = 300
    cool_down_duration = 60

    def tick(self):

        run_time = self.get_run_time()

        cycle = int(run_time) // (self.stage_duration + self.cool_down_duration)

        if run_time % (self.stage_duration + self.cool_down_duration) < self.stage_duration:
            user_count = self.start_user + cycle * self.stage_increment
        else:
            user_count = 0

        return user_count, self.spawn_rate
