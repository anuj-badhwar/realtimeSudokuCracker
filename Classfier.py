import tensorflow as tf
import os
import numpy as np

def get_trained_model():
    modelPath = './model/mnist/mnistModel.meta'
    if not os.path.exists(modelPath):
        print "No trained model!."
        return
    sess = tf.Session()
    saver = tf.train.import_meta_graph(modelPath)
    saver.restore(sess, tf.train.latest_checkpoint('./model/mnist/'))
    graph = tf.get_default_graph()
    op_to_restore = graph.get_tensor_by_name("accuracy:0")
    x = graph.get_tensor_by_name("input_image:0")
    y_ = graph.get_tensor_by_name("input_label:0")
    keep_prob = graph.get_tensor_by_name("keep_prob:0")
    pred_label = graph.get_tensor_by_name("pred_label:0")
    def predict(Input):
        feed = {x:Input, y_:np.zeros((81,9)), keep_prob:1.0}
        prediction = pred_label.eval(session=sess, feed_dict=feed)
        return prediction
    return predict
