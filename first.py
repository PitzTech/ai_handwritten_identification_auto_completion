#pip freeze > requirements.txt
#pip install -r requirements.txt

# pip3 install numpy opencv-python matplotlib tensorflow

# import keras
# from keras.datasets import mnist
# from keras.models import Sequential
# from keras.layers import Dense, Dropout, Flatten
# from keras.layers import Conv2D, MaxPooling2D
# from keras import backend as K

import os
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

print("Starting Handwritten Digits Recognition")

# Load existing model or train new
train_new_model = False
test_local_images = True

if train_new_model:
    # split data between test and train
    mnist = tf.keras.datasets.mnist
    (X_train, y_train), (X_test, y_test) = mnist.load_data()

    # Normalizing the data (making length = 1)
    X_train = tf.keras.utils.normalize(X_train, axis=1)
    X_test = tf.keras.utils.normalize(X_test, axis=1)

    # Create a neural network model
    # 1 flattened input layer for the pixels
    # 2 dense hidden layers
    # 1 dense output layer for the 10 digits
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(units=128, activation=tf.nn.relu))
    model.add(tf.keras.layers.Dense(units=128, activation=tf.nn.relu))
    model.add(tf.keras.layers.Dense(units=10, activation=tf.nn.softmax))

    # Compiling and optimizing model
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Training the model
    model.fit(X_train, y_train, epochs=3)
    print('Training completed')

    # Evaluating the model
    print('Evaluating the model')
    val_loss, val_acc = model.evaluate(X_test, y_test)
    print(f'Test Loss: {val_loss}')
    print(f'Test Accuracy: {val_acc}')

    # Saving the model
    model.save('handwritten_digits.model')
    print('Model saved as handwritten_digits.model')
else:
    # Load the model
    model = tf.keras.models.load_model('handwritten_digits.model')

    # split data between test and train
    mnist = tf.keras.datasets.mnist
    (X_train, y_train), (X_test, y_test) = mnist.load_data()

    # Normalizing the data (making length = 1)
    X_test = tf.keras.utils.normalize(X_test, axis=1)

    # Evaluating the model
    print('Evaluating the model')
    val_loss, val_acc = model.evaluate(X_test, y_test)
    print(f'Test Loss: {{val_loss}}')
    print(f'Test Accuracy: {{val_acc}}')

# Load custom images and predict them
if test_local_images:
  image_number = 9
  while os.path.isfile('digits/digit{}.png'.format(image_number)):
      try:
          img = cv2.imread('digits/digit{}.png'.format(image_number))[:,:,0]
          img = np.invert(np.array([img]))
          prediction = model.predict(img)
          print("The number is probably a {}".format(np.argmax(prediction)))
          plt.imshow(img[0], cmap=plt.cm.binary)
          plt.show()
          image_number += 1
      except:
          print("Error reading image! Proceeding with next image...")
          image_number += 1
