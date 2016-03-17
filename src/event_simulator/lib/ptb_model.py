# coding: utf8
# Python3

import os
import tensorflow as tf
from tensorflow.models.rnn import rnn_cell, seq2seq, rnn
import pickle


# https://github.com/tensorflow/tensorflow/blob/master/tensorflow/models/rnn/ptb/ptb_word_lm.py
class PTBModel:
    """The PTB model."""
    _saver = None
    _model_path = None

    def __init__(self, is_training, config):
        self.config = config
        self.batch_size = batch_size = config.batch_size
        self.num_steps = num_steps = config.num_steps
        hidden_size = config.hidden_size
        vocab_size = config.vocab_size

        self._input_data = tf.placeholder(tf.int32, [batch_size, num_steps])
        self._targets = tf.placeholder(tf.int32, [batch_size, num_steps])

        # Slightly better results can be obtained with forget gate biases
        # initialized to 1 but the hyperparameters of the model would need to be
        # different than reported in the paper.
        lstm_cell = rnn_cell.BasicLSTMCell(hidden_size, forget_bias=0.0)
        if is_training and config.keep_prob < 1:
            lstm_cell = rnn_cell.DropoutWrapper(
                    lstm_cell, output_keep_prob=config.keep_prob)
        cell = rnn_cell.MultiRNNCell([lstm_cell] * config.num_layers)

        self._initial_state = cell.zero_state(batch_size, tf.float32)

        with tf.device("/cpu:0"):
            embedding = tf.get_variable("embedding", [vocab_size, hidden_size])
            inputs = tf.nn.embedding_lookup(embedding, self._input_data)

        # self.inputs_shape = tf.shape(inputs)  # [batch_size, num_steps, size]

        if is_training and config.keep_prob < 1:
            inputs = tf.nn.dropout(inputs, config.keep_prob)

        inputs = [tf.squeeze(input_, [1])
                  for input_ in tf.split(1, num_steps, inputs)]
        outputs, self._final_state = rnn.rnn(cell, inputs, initial_state=self._initial_state)

        # outputs = []
        # states = []
        # state = self._initial_state
        # with tf.variable_scope("RNN"):
        #     for time_step in range(num_steps):
        #         if time_step > 0: tf.get_variable_scope().reuse_variables()
        #         (cell_output, state) = cell(inputs[:, time_step, :], state)
        #         outputs.append(cell_output)
        #         states.append(state)

        output = tf.reshape(tf.concat(1, outputs), [-1, hidden_size])
        self._logits = logits = tf.nn.xw_plus_b(output,
                                                tf.get_variable("softmax_w", [hidden_size, vocab_size]),
                                                tf.get_variable("softmax_b", [vocab_size]))
        self._prob = tf.nn.softmax(logits, "prob")

        loss = seq2seq.sequence_loss_by_example([logits],
                                                [tf.reshape(self._targets, [-1])],
                                                # [tf.ones([batch_size * num_steps])],
                                                [tf.reshape(tf.cast(tf.sign(self._targets), tf.float32), [-1])],
                                                vocab_size)
        self._cost = cost = tf.reduce_sum(loss) / batch_size

        if not is_training:
            return

        self._lr = tf.Variable(0.001, trainable=False)
        tvars = tf.trainable_variables()
        grads, _ = tf.clip_by_global_norm(tf.gradients(cost, tvars),
                                          config.max_grad_norm)
        # optimizer = tf.train.GradientDescentOptimizer(self.lr)
        optimizer = tf.train.AdamOptimizer()
        self._train_op = optimizer.apply_gradients(zip(grads, tvars))

    def init_or_restore(self, session, model_path):
        self._saver = tf.train.Saver()
        self._model_path = model_path

        if os.path.exists(model_path):
            print("restore session from %s" % model_path)
            self.saver.restore(session, model_path)
        else:
            print("initialize new session")
            tf.initialize_all_variables().run()

    def save(self, session):
        self.saver.save(session, self.model_path)

    @staticmethod
    def load_config(model_path):
        filename = "%s.config" % model_path
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                return pickle.load(f)

    def save_config(self):
        with open("%s.config" % self.model_path, "bw") as f:
            pickle.dump(self.config, f)

    def assign_lr(self, session, lr_value):
        session.run(tf.assign(self.lr, lr_value))

    @property
    def saver(self):
        return self._saver

    @property
    def model_path(self):
        return self._model_path

    @property
    def input_data(self):
        return self._input_data

    @property
    def targets(self):
        return self._targets

    @property
    def initial_state(self):
        return self._initial_state

    @property
    def cost(self):
        return self._cost

    @property
    def final_state(self):
        return self._final_state

    @property
    def lr(self):
        return self._lr

    @property
    def train_op(self):
        return self._train_op

    @property
    def logits(self):
        return self._logits

    @property
    def prob(self):
        return self._prob


class SmallConfig:
    """Small config."""
    num_steps = 25
    batch_size = 20
    num_layers = 2
    hidden_size = 20
    init_scale = 0.1
    learning_rate = 1.0
    max_grad_norm = 5
    max_epoch = 4
    max_max_epoch = 13
    keep_prob = 1.0
    lr_decay = 0.5
    vocab_size = None
