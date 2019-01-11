# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/12/24 16:26
"""
import numpy as np
import tensorflow as tf


class DNN:
    """
    基本的DNN模型，在不对来类进行重载的情况下，相当于一个
    单层感知机，通过重写该类的某些方法可以实现真正的DNN
    """
    def __init__(self, x_train=None, y_train=None, x_test=None,
                 y_test=None, episode=None):
        if x_train is None or y_train is None or \
                x_test is None or y_test is None:
            pass    # 允许没有相关的训练或测试数据
        else:
            self.x_train = x_train
            self.y_train = y_train
            self.x_test = x_test
            self.y_test = y_test
            self._num_examples = x_train.shape[0]  # 参与训练的实例数
            self.n_in = x_train.shape[1]    # 输入层的维度
            self.n_out = y_train.shape[1]   # 输出层的维度
            self.batch_size = 100  # 参与每次梯度迭代的数据量
            # 计算每一个回合有多少个batch
            self.epochs = self._num_examples // self.batch_size + 1
        self.episode = episode  # 回合数，每一个回合会把所有的训练数据用一遍
        self.regular_rate = 0.00001
        self.learning_rate = 0.001
        self._epochs_completed = 0
        self._index_in_epoch = 0
        self.sess = tf.Session()
        pass

    @classmethod
    def convert_to_one_hot(cls, Y, C):
        Y = np.eye(C)[Y.reshape(-1)].T  # np.eye 生成对角矩阵
        return Y

    def initialize_parameters(self):
        """
        单层感知机的模型初始化。
        根据隐藏层的神经元节点数构建各层W,b, 默认是没有隐藏层的
        需要添加隐藏层的需要重载这个函数，并实现所有权重和偏倚矩阵
        的初始化。权重和偏倚矩阵变量定义时最好
        """
        weights = {
            'W1': tf.Variable(tf.random_normal(shape=[self.n_in, self.n_out],
                                               stddev=0.01), name='W1'),
            # "W2": tf.Variable(tf.random_normal(shape=[512, 256], stddev=0.01)),
            # "W3": tf.Variable(tf.random_normal(shape=[256, self.n_out], stddev=0.01)),
        }

        bias = {
            'b1': tf.Variable(tf.zeros([self.n_out]), dtype=tf.float32,
                              name='b1'),
            # 'b2': tf.Variable(tf.zeros([256]), dtype=tf.float32),
            # 'b3': tf.Variable(tf.zeros([10]), dtype=tf.float32)
        }
        return weights, bias

    def forward_propagation(self, x, weights, bias,
                            outputs_variable_name):
        """
        前向传播算法为：X -> LINEAR -> A -> LINEAR -> A -> LINEAR -> A
        :param outputs_variable_name: 模型最终输出的变量的name
        :param x: 输入集作为占位符，维度大小为（输入大小，样本数目）
        :param weights: 包含W1, W2, ...
        :param bias: 包含b1, b2, ...
        :return:
        """
        output = tf.matmul(x, weights['W1']) + bias['b1']
        Z = tf.nn.softmax(output, name=outputs_variable_name)
        return Z

    def loss(self, y_, y, **kwargs):
        """
        损失函数
        :param y_:
        :param y:
        :param kwargs:
        :return:
        """
        regular = tf.contrib.layers.l2_regularizer(self.regular_rate)
        with tf.name_scope("loss"):
            loss = tf.reduce_sum(-tf.log(y_) * y) + regular(kwargs['weights']['W1'])

        return loss

    def optimizer(self, loss):
        """
        损失函数的优化算法
        :param loss:
        :return:
        """
        return tf.train.GradientDescentOptimizer(self.learning_rate).minimize(loss)

    def accuracy(self, y_, y):
        """
        通过输出值与真实值计算准确率
        :param y_:
        :param y:
        :return:
        """
        with tf.name_scope('accuracy'):
            accuracy_op = tf.reduce_mean(
                tf.cast(tf.equal(tf.arg_max(y_, 1), tf.arg_max(y, 1)),
                        dtype=tf.float32)
            )
        return accuracy_op

    def next_batch(self, batch_size, shuffle=True):
        """
        Return the next `batch_size` examples from this train data set.
        :param shuffle:
        :param batch_size:
        :return:
        """
        start = self._index_in_epoch
        # Shuffle for the first epoch
        if self._epochs_completed == 0 and start == 0 and shuffle:
            perm0 = np.arange(self._num_examples)
            np.random.shuffle(perm0)
            self.x_train = self.x_train[perm0]
            self.y_train = self.y_train[perm0]
        # Go to the next epoch
        if start + batch_size > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            # Get the rest examples in this epoch
            rest_num_examples = self._num_examples - start
            x_train_rest_part = self.x_train[start:self._num_examples]
            y_train_rest_part = self.y_train[start:self._num_examples]
            # Shuffle the data
            if shuffle:
                perm = np.arange(self._num_examples)
                np.random.shuffle(perm)
                self.x_train = self.x_train[perm]
                self.y_train = self.y_train[perm]
            # Start next epoch
            start = 0
            self._index_in_epoch = batch_size - rest_num_examples
            end = self._index_in_epoch
            x_train_new_part = self.x_train[start:end]
            y_train_new_part = self.y_train[start:end]
            return np.concatenate(
                (x_train_rest_part, x_train_new_part), axis=0), np.concatenate(
                (y_train_rest_part, y_train_new_part), axis=0)
        else:
            self._index_in_epoch += batch_size
            end = self._index_in_epoch
            return self.x_train[start:end], self.y_train[start:end]
        pass

    def restore(self, model_save_path):
        """
        加载已保存的tf模型
        :param model_save_path:
        :return:
        """
        saver = tf.train.import_meta_graph(model_save_path + '.meta')
        saver.restore(self.sess, model_save_path)
        return self
        pass

    def predict(self, x):
        """
        给出输入值x的对应输出
        :param x:
        :return:
        """
        graph = tf.get_default_graph()
        inputs = graph.get_tensor_by_name('inputs:0')
        outputs = graph.get_tensor_by_name('outputs:0')
        y = self.sess.run(outputs, feed_dict={inputs: x})
        return y

    def fit(self, model_save_path=None, steps=100):
        x = tf.placeholder(tf.float32, shape=[None, self.n_in], name='inputs')
        y = tf.placeholder(tf.float32, shape=[None, self.n_out])
        w, b = self.initialize_parameters()
        y_ = self.forward_propagation(x, w, b, 'outputs')
        init = tf.global_variables_initializer()
        loss = self.loss(y_, y, weights=w)
        optimizer_op = self.optimizer(loss)
        accuracy_op = self.accuracy(y_, y)
        tf.summary.scalar("loss", loss)
        tf.summary.scalar("accuracy", accuracy_op)
        self.sess.run(init)
        m_saver = None
        if model_save_path is not None:
            m_saver = tf.train.Saver()
        summary_op = tf.summary.merge_all()
        # test_feed = {x: self.mnist.test.images, y: self.mnist.test.labels}
        # print ("accuracy:",sess.run(accuracy_op,feed_dict=test_feed));
        summary_writer = tf.summary.FileWriter("./log/", self.sess.graph)
        for e in range(self.episode):
            for i in range(self.epochs):
                batch_x, batch_y = self.next_batch(self.batch_size)
                train_feed = {x: batch_x, y: batch_y}
                self.sess.run(optimizer_op, feed_dict=train_feed)
                summary_output = self.sess.run(summary_op, feed_dict=train_feed)
                summary_writer.add_summary(summary_output, i + e * self.epochs)
                if i % steps == 0:
                    l = self.sess.run(loss, feed_dict=train_feed)
                    test_feed = {x: self.x_test, y: self.y_test}
                    acc = self.sess.run(accuracy_op, feed_dict=test_feed)
                    print('Epoch {}/{}'.format(i, self.episode * self.epochs))
                    print("{}/{} [".format(e + 1, self.episode) +
                          '=' * 30 + '] -loss: {} - acc: {}'.format(round(l, 2), round(acc, 2)))
                    if model_save_path is not None:
                        m_saver.save(self.sess, model_save_path, global_step=i + e * self.epochs)

            # test_feed = {x: self.x_test, y: self.y_test}
            # acc = self.sess.run(accuracy_op, feed_dict=test_feed)
            # print("this episode {} accuracy:{}".format(e + 1, acc))
            self._epochs_completed = 0
        summary_writer.close()
        return self
        pass

    def close(self):
        self.sess.close()


def f1():
    from tensorflow.examples.tutorials.mnist import input_data
    mnist = input_data.read_data_sets('E:\wv\\tf\input_data', one_hot=True, validation_size=100)
    # d = mnist.train.next_batch(20)
    x_train, y_train = mnist.train.images, mnist.train.labels
    x_test, y_test = mnist.test.images, mnist.test.labels

    # DNN(np.zeros((100, 784), dtype=np.float32), np.zeros((100, 10), dtype=np.float32),
    #  np.zeros((100, 784), dtype=np.float32),
    #     np.zeros((100, 10), dtype=np.float32), []).initialize_parameters()
    # plt.imshow(img.reshape(28, 28), cmap=plt.cm.binary)
    # plt.show()
    class MyDNN(DNN):

        def initialize_parameters(self):
            weights = {
                'W1': tf.Variable(tf.random_normal(shape=[self.n_in, 512], stddev=0.01), name='W1'),
                "W2": tf.Variable(tf.random_normal(shape=[512, 256], stddev=0.01), name='W2'),
                "W3": tf.Variable(tf.random_normal(shape=[256, self.n_out], stddev=0.01), name='W3'),
            }

            bias = {
                'b1': tf.Variable(tf.zeros([512]), dtype=tf.float32, name='b1'),
                'b2': tf.Variable(tf.zeros([256]), dtype=tf.float32, name='b2'),
                'b3': tf.Variable(tf.zeros([self.n_out]), dtype=tf.float32, name='b3')
            }
            return weights, bias

        def forward_propagation(self, x, weights, bias, outputs_variable_name):
            with tf.name_scope('hidden1'):
                output1 = tf.nn.relu(tf.matmul(x, weights['W1']) + bias['b1'], name='output1')
            with tf.name_scope('hidden2'):
                output2 = tf.nn.relu(tf.matmul(output1, weights['W2']) + bias['b2'], name='output2')
            with tf.name_scope('hidden3'):
                output = tf.matmul(output2, weights['W3'], name='output3') + bias['b3']
            Z = tf.nn.softmax(output, name=outputs_variable_name)
            return Z

    MyDNN(x_train, y_train, x_test, y_test, episode=4).fit(model_save_path='./model/mnist')
    # import matplotlib.pyplot as plt
    # plt.imshow(x_test[1].reshape(28, 28), cmap=plt.cm.binary)
    # plt.show()
    # y = MyDNN().restore('./model/mnist-1500').predict(x_test[0:12])
    # v = np.argmax(y, 1)

    pass


# f1()
# with tf.name_scope('conv1') as scope:
#     weights1 = tf.Variable([1.0, 2.0])
#     bias1 = tf.Variable([0.3], name='bias')
# print(weights1.name)
