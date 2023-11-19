import cv2
import numpy as np
import os
import pandas as pd
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

PATH = os.getcwd()
DATASET_PATH = os.path.join(PATH, 'dataset')
MODEL_PATH = os.path.join(PATH, 'model')

DATASET_LABEL_CSV_FILENAME = 'chars_responses.csv'

# Criar o diretório para os modelos, se ele não existir
if not os.path.exists(MODEL_PATH):
    os.makedirs(MODEL_PATH)

def load_image(image_path):
    # Carregar imagem em escala de cinza
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    return image

def calculate_gradient_orientation(image):
    # Calcular gradientes usando o operador de Sobel
    grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=5)
    grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=5)

    # Calcular a orientação dos gradientes
    orientation = np.arctan2(grad_y, grad_x)
    avg_orientation = np.mean(orientation)

    return avg_orientation

def calculate_character_compactness(image):
    # Encontrar a caixa delimitadora do caractere
    _, thresh = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        cnt = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(cnt)
        character_area = cv2.contourArea(cnt)
        bounding_box_area = w * h
        compactness = character_area / bounding_box_area
        return compactness
    else:
        return 0

def fuzzify_image(image):
    # Calcular a densidade de pixels pretos
    black_density = np.sum(image < 128) / image.size
    # Calcular a orientação média dos gradientes
    orientation = calculate_gradient_orientation(image)
    # Calcular a compactação do caractere
    compactness = calculate_character_compactness(image)

    # Fuzzificação das características
    fuzzy_black_density = "alta" if black_density > 0.5 else "baixa"
    fuzzy_orientation = "vertical" if abs(orientation) < np.pi / 4 else "horizontal"
    fuzzy_compactness = "compacto" if compactness > 0.5 else "não compacto"

    return {
        "black_density": fuzzy_black_density,
        "orientation": fuzzy_orientation,
        "compactness": fuzzy_compactness
    }

def encode_features(fuzzified_features):
  encoded_features = []
  for features in fuzzified_features:
      # Codificar cada característica fuzzy. Exemplo: 'alta' -> 1, 'baixa' -> 0
      encoded_feature = [
          1 if features["black_density"] == "alta" else 0,
          1 if features["orientation"] == "vertical" else 0,
          1 if features["compactness"] == "compacto" else 0
      ]
      encoded_features.append(encoded_feature)
  return np.array(encoded_features)

def readDataset():
  dict_img = {}

  df = pd.read_csv(os.path.join(DATASET_PATH, DATASET_LABEL_CSV_FILENAME))
  all_links = df['image']
  all_labels = df['label']
  labels = all_labels.unique()

  for label in labels:
      dict_img[label] = []

  for i in range(len(all_links)):
      dict_img[all_labels[i]].append(all_links[i])
  return dict_img, all_labels.unique()

def process_images(dict_img):
  processed_data = []
  labels = []

  for label, image_paths in dict_img.items():
      for image_path in image_paths:
          full_path = os.path.join(DATASET_PATH, image_path)
          image = load_image(full_path)
          fuzzified_features = fuzzify_image(image)
          encoded_features = encode_features([fuzzified_features])[0]
          processed_data.append(encoded_features)
          labels.append(label)

  return np.array(processed_data), np.array(labels)

def build_cnn(input_shape, num_classes):
  model = tf.keras.Sequential([
      Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=input_shape),
      MaxPooling2D(pool_size=(2, 2)),
      Conv2D(64, (3, 3), activation='relu'),
      MaxPooling2D(pool_size=(2, 2)),
      Flatten(),
      Dense(128, activation='relu'),
      Dense(num_classes, activation='softmax')
  ])
  model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
  return model

def preprocess_images(images, target_size=(28, 28)):
  processed_images = []
  for img in images:
      # Redimensionar a imagem
      img_resized = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
      # Normalizar os valores dos pixels para o intervalo [0, 1]
      img_normalized = img_resized / 255.0
      # Adicionar uma dimensão de canal
      img_normalized = np.expand_dims(img_normalized, axis=-1)
      processed_images.append(img_normalized)
  return np.array(processed_images)

print('Starting Training')

# Lendo e processando o conjunto de dados

print('Reading Dataset')
dict_img, label_classes = readDataset()
print('Processing Images')
X, y = process_images(dict_img)

print('Pre processing the image')
# Aplicar pré-processamento a todas as imagens
X_processed = preprocess_images(X)

print('Converting Labels')
# Convertendo rótulos em números
label_to_id = {label: idx for idx, label in enumerate(label_classes)}
y_numeric = np.array([label_to_id[label] for label in y])

print('Splitting dataset')
# Dividindo os dados em conjuntos de treino e teste
X_train, X_test, y_train, y_test = train_test_split(X_processed, y_numeric, test_size=0.2)

print('Building CNN')
# Criar a CNN
model = build_cnn(input_shape=(28, 28, 1), num_classes=len(label_classes))

print('Creating Data Augmentation generator')
# Definindo o gerador de aumento de dados
# datagen = ImageDataGenerator(
#     rotation_range=10,  # rotação aleatória
#     width_shift_range=0.1,  # deslocamento horizontal aleatório
#     height_shift_range=0.1,  # deslocamento vertical aleatório
#     zoom_range=0.1,  # zoom aleatório
#     horizontal_flip=False,  # não aplicar flip horizontal
#     fill_mode='nearest'  # preencher pixels novos com o 'mais próximo'
# )
datagen = ImageDataGenerator(
    rotation_range=0,  # rotação aleatória
    width_shift_range=0,  # deslocamento horizontal aleatório
    height_shift_range=0,  # deslocamento vertical aleatório
    zoom_range=0.1,  # zoom aleatório
    horizontal_flip=False,  # não aplicar flip horizontal
    fill_mode='nearest'  # preencher pixels novos com o 'mais próximo'
)

print('Starting Training')
# Treinamento do modelo com aumento de dados
print('With augmented data')
datagen.fit(X_train)
print('Final fit')
model.fit(datagen.flow(X_train, y_train, batch_size=32),
          steps_per_epoch=len(X_train) / 32,
          epochs=10,
          validation_data=(X_test, y_test))
print('Training completed')

# Avaliação do modelo
print('Evaluating the model')
test_loss, test_acc = model.evaluate(X_test, y_test)
print(f'Test Loss: {test_loss}')
print(f'Test Accuracy: {test_acc}')

# Definir o caminho do arquivo onde o modelo será salvo
model_save_path = os.path.join(MODEL_PATH, "modelo.h5")

# Salvar o modelo
model.save(model_save_path)
print(f"Modelo salvo em: {model_save_path}")
