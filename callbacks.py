import tensorflow as tf
from keras.callbacks import Callback
from keras.callbacks import TensorBoard

import io
from PIL import Image

from constants import batch_size


def get_callbacks():
    # (ml-gpu) C:\...\SR-ResCNN-Keras-\logs>
    # tensorboard --logdir .
    tbCallBack = TensorBoard(log_dir='./logs',
                             histogram_freq=1,
                             write_graph=True,
                             write_images=True,
                             write_grads=True,
                             batch_size=batch_size)

    tbi_callback = TensorBoardImage('Image test')

    # TODO: add "Reduced Learning Rate" (https://keras.io/callbacks/#ReduceLROnPlateau)
    # keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=10, verbose=0, mode='auto',
    #                                   min_delta=0.0001, cooldown=0, min_lr=0)

    #return [tbCallBack, tbi_callback]  TODO: re-add once the BoardImage issue is sorted out
    #return [tbCallBack]  TODO: currently too slow...
    return []


def make_image(tensor):
    """
    Convert an numpy representation image to Image protobuf.
    Copied from https://github.com/lanpa/tensorboard-pytorch/
    """
    height, width, channel = tensor.shape
    image = Image.fromarray(tensor.astype('uint8'))  # TODO: maybe float ?

    output = io.BytesIO()
    image.save(output, format='JPEG')
    image_string = output.getvalue()
    output.close()

    return tf.Summary.Image(height=height,
                            width=width,
                            colorspace=channel,
                            encoded_image_string=image_string)


class TensorBoardImage(Callback):
    def __init__(self, tag):
        super().__init__()
        self.tag = tag

    def on_epoch_end(self, epoch, logs={}):
        # Load image
        img_input = self.validation_data[0][0]  # X_train
        img_valid = self.validation_data[1][0]  # Y_train

        print(self.validation_data[0].shape)  # (8, 128, 128, 3)
        print(self.validation_data[1].shape)  # (8, 512, 512, 3)

        image = make_image(img_input)
        summary = tf.Summary(value=[tf.Summary.Value(tag=self.tag, image=image)])
        writer = tf.summary.FileWriter('./logs')
        writer.add_summary(summary, epoch)
        writer.close()

        image = make_image(img_valid)
        summary = tf.Summary(value=[tf.Summary.Value(tag=self.tag, image=image)])
        writer = tf.summary.FileWriter('./logs')
        writer.add_summary(summary, epoch)
        writer.close()

        return


class PeriodicLogger(Callback):

    def on_train_begin(self, logs={}):
        # Initialization code
        self.epochs = 0

    def on_epoch_end(self, batch, logs={}):
        self.epochs += 1
        if self.epochs % 2 == 0:
            # Do stuff like printing metrics
            print("bob")