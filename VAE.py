# -*- coding: utf-8 -*-
"""Copy of AutoEncoder.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FDc5DrF1xSgaNSgPFL4GsEzAmQppq74m
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt

training_images = np.load('mnist_train_images.npy')
print(np.shape(training_images))
print(np.max(training_images))

class Encoder(tf.keras.layers.Layer):
  def __init__(self):
    super(Encoder,self).__init__()

    self.flattenLayer = tf.keras.layers.Flatten()

    self.encoder1 = tf.keras.layers.Dense(200, activation ='tanh')
    self.encoder1drop = tf.keras.layers.Dropout(rate=0.2)

    # self.encoder2 = tf.keras.layers.Dense(120, activation ='tanh')
    # self.encoder2drop = tf.keras.layers.Dropout(rate=0.2)

    # For the mean of the normal distrubution
    self.zmean = tf.keras.layers.Dense(16, activation='tanh')

    #For the variance of the normal distrubution, Relu is used to ensure positivity    
    self.zVariance = tf.keras.layers.Dense(16, activation='relu')


  def call(self,images):

      images_flattened = self.flattenLayer(images)

      x = self.encoder1(images)
      x = self.encoder1drop(x)

      # x = self.encoder2(x)
      # x = self.encoder2drop(x)
      
      mean = self.zmean(x)
      variance = self.zVariance(x)
      
      # Draw samples corresponding to the batch size, number of dimensions of the gaussain from which the sample is to be drawn
      #(given by first part of shape of mean, second part of variance/mean)
      epsilon = tf.keras.backend.random_normal(shape=(tf.shape(mean)[0], tf.shape(variance)[1]))
      
      # Generating the vector z which will be provided to the input of the decoder, square variance for positivity
      sampledZ = mean + tf.exp(0.5 * variance) * epsilon

      return mean, variance, sampledZ

class Decoder(tf.keras.layers.Layer):
  def __init__(self):
    super(Decoder,self).__init__()

    self.decoder1 = tf.keras.layers.Dense(200, activation='tanh')
    # self.decoder2 = tf.keras.layers.Dense(300, activation='tanh')
    self.finaLayer = tf.keras.layers.Dense(784, activation='sigmoid')

  def call(self,sampled_input):

    x = self.decoder1(sampled_input)

    # x = self.decoder2(x)

    expectedOutput = self.finaLayer(x)

    return expectedOutput

class VariationalAutoEncoder(tf.keras.Model):
  def __init__(self):
    super(VariationalAutoEncoder,self).__init__()

    self.encoder = Encoder()
    self.decoder = Decoder()

  def call(self,inputImages):

      mean, variance, sampledZ = self.encoder(inputImages)

      # epsilon = tf.keras.backend.random_normal(shape=(tf.shape(mean), tf.shape(variance)))

      # sampledZ = mean + tf.exp(0.5 * variance) * epsilon

      estimate = self.decoder(sampledZ)

      # Adding KL divergence to the loss 
      #Log loss is the other loss which the model will use, the built in Binary Cross Entropy Loss.

      # Using a factor of 0.009 as the weighting factor for KL loss gave decent new generation of images
      kl_loss = - 0.5* 0.009*tf.reduce_mean(variance - tf.square(mean) - tf.exp(variance) + 1)
      self.add_loss(kl_loss)

      return estimate

vaeKL = VariationalAutoEncoder()

# Using Adam as an Optimizer
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

# In the call method for the model, the KL divergence loss is being added to the loss defined below.
# Using Binary Cross entropy (log loss) for reconstruction loss and KL divergence loss which is defined in the call method
vaeKL.compile(optimizer, loss=tf.keras.losses.BinaryCrossentropy())
vaeKL.fit(training_images, training_images, epochs=50, batch_size=100)

KLreconstructed = vaeKL.predict(training_images)
print(np.shape(KLreconstructed))

klImage = np.reshape(KLreconstructed[999,:],(28,28))
checkImage = np.reshape(training_images[999,:],(28,28))
#plt.imshow(klImage,cmap='gray')

fig=plt.figure(figsize=(16, 16))

upper = 70

for i in range(0,16):
  klImage = np.reshape(KLreconstructed[i+upper,:],(28,28))
  fig.add_subplot(1,16 , 1+i)
  plt.imshow(klImage,cmap='gray')
  checkImage = np.reshape(training_images[i+upper,:],(28,28))
  fig.add_subplot(2,16 , 1+i)
  plt.imshow(checkImage,cmap='gray')

plt.show()

## This is the part where new examples are generated by sampling from a gaussian
# and passing it through the decoder, 25 examples are generated for this case 
epsilon2 = tf.keras.backend.random_normal(shape=(25, 16))
#print(epsilon2)
random_image = vaeKL.decoder(epsilon2).numpy()
print(np.shape(random_image))
fig=plt.figure(figsize=(25, 25))

for i in range(0,25):
  first_random = np.reshape(random_image[i,:],(28,28))
  fig.add_subplot(1,25 , 1+i)
  plt.imshow(first_random,cmap='gray')
plt.show()

