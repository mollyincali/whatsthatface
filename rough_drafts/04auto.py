'''
UPDATING 03AUTO
- comment out line 84 for no more warning message
- increasing batch size to 32 
- epochs to 5
code credit: https://github.com/alyserecord/wine/blob/master/src/cnn-autoencoder.py
'''
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
sns.set()
import tensorflow as tf
from tensorflow.keras import layers
from keras.layers import Conv2D, MaxPooling2D, UpSampling2D, Flatten, Reshape
from keras.models import Sequential 
from keras.preprocessing.image import ImageDataGenerator
from keras import backend as K
from sklearn.cluster import KMeans

class Autoencoder():
    def __init__(self, model=None):
        ''' initializes the autoencoder model '''
        if model != None:
            self.model = model

    def build_autoencoder(self):
        ''' build autoencoder model '''
        autoencoder = tf.keras.Sequential([
            layers.Conv2D(128, (3, 3), activation = 'relu', padding = 'same', input_shape=(128, 128, 3)),
            layers.MaxPooling2D((2,2), padding = 'same'),
            layers.Conv2D(64, (3, 3), activation = 'relu', padding = 'same'),
            layers.MaxPooling2D((2,2), padding = 'same'),
            layers.Conv2D(32, (3, 3), activation = 'relu', padding = 'same'),
            layers.MaxPooling2D((2,2), padding = 'same'),
            layers.Conv2D(8, (3, 3), activation = 'relu', padding = 'same'),
            layers.MaxPooling2D((2,2), padding = 'same'),
            
            layers.Flatten(),
            layers.Reshape((8, 8, 8)), #reshape for next layer

            layers.Conv2D(8, (3, 3), activation = 'relu', padding = 'same'),
            layers.UpSampling2D((2,2)),
            layers.Conv2D(32, (3, 3), activation = 'relu', padding = 'same'),
            layers.UpSampling2D((2,2)),
            layers.Conv2D(64, (3, 3), activation = 'relu', padding = 'same'),
            layers.UpSampling2D((2,2)),
            layers.Conv2D(128, (3, 3), activation = 'relu', padding = 'same'),
            layers.UpSampling2D((2,2)),
            layers.Conv2D(3, (3,3), activation = 'sigmoid', padding = 'same')
            ])
        
        autoencoder.summary()

        autoencoder.compile(optimizer = 'adam', loss = 'mean_squared_error')

        self.model = autoencoder 

    def fit(self, train, test, batch_size, epochs):
        ''' this method will fit the model using train & test data '''
        self.model.fit(train, 
                    epochs = epochs,
                    batch_size = batch_size,
                    validation_data = test)
        self.history = self.model.history.history

    def get_rmse(self, test):
        ''' calcuate the RMSE of the model after it is trained '''
        return self.model.evaluate(test, test)

    def predict(self, X):
        ''' 
        using the trained autoencoder 
        predicts on the provided image array and returns reconstructed images 
        input: X is val_generator
        output: reconstructed np.array of shape 128,128,3
        ''' 
        return self.model.predict(X)

    def before_after_img(self, test, test_decoded, n=10):
        ''' plot the images before and after the autoencoder '''
        plt.figure(figsize=(20,4))
        for i in range(n):
            #display before
            ax = plt.subplot(2, n, i + 1)
            plt.imshow(test[i])

            #display after
            ax = plt.subplot(2, n, i + 1 + n)
            plt.imshow(test_decoded[i])
        plt.show()

    def get_later(self, X):
        ''' get the flattened layer of the autoencoder model to do kmeans cluster '''
        batches = np.split(X, 5)
        for i, batch in enumerate(batches):
            get_later_output = K.function([self.model.layers[0].input],
                                        [self.model.layers[8].output])
            layer_output = get_later_output([batch])[0]

            if i == 0:
                final_layers = layer_output
            else:
                final_layers = np.vstack((final_layers, layer_output))

        self.encoding = final_layers
        return self.encoding
    
    def get_flat_layer(self):
        ''' get only middle lay needed for kmeans '''
        return [self.autoencoder.layers[8].output]

if __name__ == "__main__":
    img_width, img_height = 128, 128
    train_data_dir = '../animals/train/w.wild'
    val_data_dir = '../animals/val/w.wild'
    batch_size = 32

    train_datagen = ImageDataGenerator(
            rescale = 1. / 255,
            shear_range = 0.2,
            zoom_range = 0.2,
            horizontal_flip = True)

    val_datagen = ImageDataGenerator(rescale = 1. / 255)
        
    train_generator = train_datagen.flow_from_directory(
            train_data_dir,
            target_size=(img_width, img_height),
            batch_size=batch_size,
            class_mode='input')
        
    val_generator = val_datagen.flow_from_directory(
            val_data_dir,
            target_size=(img_width, img_height),
            batch_size = batch_size,
            class_mode = 'input')

    cnn = Autoencoder()
    cnn.build_autoencoder()
    cnn.fit(train_generator, val_generator, 32, 1)


# Epoch 1/5
# 149/149 [==============================] - 1765s 12s/step - loss: 0.0287 - val_loss: 0.0222
# Epoch 2/5
# 149/149 [==============================] - 1569s 11s/step - loss: 0.0179 - val_loss: 0.0200
# Epoch 3/5
# 149/149 [==============================] - 1480s 10s/step - loss: 0.0166 - val_loss: 0.0195
# Epoch 4/5
# 149/149 [==============================] - 1450s 10s/step - loss: 0.0162 - val_loss: 0.0187
# Epoch 5/5
# 149/149 [==============================] - 928s 6s/step - loss: 0.0156 - val_loss: 0.0183
