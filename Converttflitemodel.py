from os import listdir
from os.path import isfile, join, exists, isdir, abspath
import tensorflow_hub as hub
import tensorflow as tf


def load_model(model_path):
    if model_path is None or not exists(model_path):
        raise ValueError("saved_model_path must be the valid directory of a saved model to load.")

    # model = tf.keras.models.load_model(model_path)
    model = tf.keras.models.load_model(model_path, custom_objects={'KerasLayer': hub.KerasLayer})
    # model.summary()
    print(model.summary())
    return model


model = load_model("mask_detector2.model")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the model.
with open('tflite_model1.tflite', 'wb') as f:
    f.write(tflite_model)