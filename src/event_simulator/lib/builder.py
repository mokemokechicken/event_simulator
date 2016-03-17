# coding: utf8

import math
import time

import numpy as np
import tensorflow as tf

from event_simulator.lib.ptb_model import PTBModel


def build_model(session, config, model_data_path):
    loaded_config = PTBModel.load_config(model_data_path)
    if loaded_config:
        config.vocab_size = loaded_config.vocab_size
        config.hidden_size = loaded_config.hidden_size
        config.num_layers = loaded_config.num_layers
    initializer = tf.random_uniform_initializer(-config.init_scale, config.init_scale)
    with tf.variable_scope("model", reuse=None, initializer=initializer):
        model = PTBModel(is_training=True, config=config)
    with tf.variable_scope("model", reuse=True, initializer=initializer):
        model_validate = PTBModel(is_training=False, config=config)

    model.init_or_restore(session, model_data_path)
    return model, model_validate


def train_model(session, model, data_feeder):
    """
    :type session: tf.Session
    :type model: PTBModel
    :type data_feeder: event_simulator.lib.data_feeder.DataFeeder
    """
    model.save_config()

    for i in range(model.config.max_max_epoch):
        lr_decay = model.config.lr_decay ** max(i - model.config.max_epoch, 0.0)
        model.assign_lr(session, model.config.learning_rate * lr_decay)

        print("Epoch: %d Learning rate: %.3f" % (i + 1, session.run(model.lr)))
        train_perplexity = run_epoch(session, model, data_feeder, model.train_op, verbose=True)
        print("Epoch: %d Train Perplexity: %.3f" % (i + 1, train_perplexity))
        # valid_perplexity = run_epoch(session, model_validate, valid_data, tf.no_op())
        # print("Epoch: %d Valid Perplexity: %.3f" % (i + 1, valid_perplexity))
        model.save(session)


def run_epoch(session, model, data_feeder, eval_op, verbose=False):
    """Runs the model on the given data.
    :type session: tf.Session
    :type model: PTBModel
    :type data_feeder: event_simulator.lib.data_feeder.DataFeeder
    :param eval_op: TensorFlow Operation
    :param verbose: verbose flag
    """
    # epoch_size = ((len(data_feeder) // model.batch_size) - 1) // model.num_steps
    start_time = time.time()
    costs = 0.0
    iters = 0
    state = model.initial_state.eval()
    init_state = state[0]
    for step, (x, y) in enumerate(data_feeder):  # enumerate(ptb_iterator(data_feeder, model.batch_size, model.num_steps)):
        state[data_feeder.batch_list_of_starting_flag()] = init_state
        cost, state, _ = session.run([model.cost, model.final_state, eval_op],
                                     {model.input_data: x,
                                      model.targets: y,
                                      model.initial_state: state})
        costs += cost
        iters += model.num_steps

        if verbose and (step % int(math.ceil(data_feeder.epoch_size / 10))) == 0:
            print("step %.3f perplexity: %.3f speed: %.0f wps" %
                  (step, np.exp(costs / iters),
                   iters * model.batch_size / (time.time() - start_time)))

    return np.exp(costs / iters)


