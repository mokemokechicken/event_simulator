# coding: utf8
from event_simulator.lib.simulator import Simulator


class WebSimulator:
    simulator = None
    data_feeder = None

    def setup(self, data_feeder, session, config, model_path):
        self.data_feeder = data_feeder
        self.simulator = Simulator(data_feeder, session, config, model_path)

    def get_event_list(self):
        return [k for k, v in self.data_feeder.mapping.items() if v >= self.data_feeder.NORMAL_EVENT_START_ID]

    def simulate_sequence(self, init_sequence, target_event_list):
        return self.simulator.simulate_sequence(init_sequence, target_event_list)
