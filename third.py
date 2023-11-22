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
IMAGES_PATH = os.path.join(DATASET_PATH, 'chars')
PRE_PROCESSED_IMAGES_PATH = os.path.join(DATASET_PATH, 'pre_processed_chars')

DATASET_LABEL_CSV_FILENAME = 'chars_responses.csv'

def create_dir_if_not_exists(dir_path):
  if not os.path.exists(dir_path):
    os.makedirs(dir_path)

print('Creating non existant paths')
# Cria os diretórios necessários, se eles não existirem
create_dir_if_not_exists(MODEL_PATH)
create_dir_if_not_exists(PRE_PROCESSED_IMAGES_PATH)

# Funções de pré-processamento de imagem

def load_image(image_path):
  # Verificar se o arquivo existe antes de tentar carregá-lo
  if not os.path.exists(image_path):
      print(f"Arquivo não encontrado: {image_path}")
      return None
  # Carregar imagem em escala de cinza
  image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
  if image is None:
      print(f"Não foi possível carregar a imagem: {image_path}")
  return image

def preprocess_images(images, target_size=(28, 28)):
  processed_images = []

  for image in images:
    # Redimensionar a imagem
    img_resized = cv2.resize(image, target_size)

    # Normalizar os valores dos pixels para o intervalo [0, 1]
    img_normalized = img_resized / 255.0
    # Adicionar uma dimensão de canal
    img_normalized = np.expand_dims(img_normalized, axis=-1)
    processed_images.append(img_normalized)

  return np.array(processed_images)

def save_image(image, image_path):
  # Obter o nome base do arquivo para salvar com o mesmo nome
  base_name = os.path.basename(image_path)

  # Salvar a imagem preprocessada
  save_path = os.path.join(PRE_PROCESSED_IMAGES_PATH, base_name)
  cv2.imwrite(save_path, image * 255)  # cv2.imwrite espera valores no intervalo [0, 255]

# Funções de fuzzificação

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

# Funções de codificação de características

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

# Leitura e processamento do conjunto de dados

def read_dataset():
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

      if image is None:
        print(f"Imagem não encontrada ou erro ao carregar: {full_path}")
        continue

      fuzzified_features = fuzzify_image(image)
      encoded_features = encode_features([fuzzified_features])[0]

      processed_data.append(encoded_features)
      labels.append(label)
  return np.array(processed_data), np.array(labels)

# Construção e treinamento do modelo de CNN

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

def train_model(model, X_train, y_train, X_test, y_test):
  print('Creating Data Augmentation generator')
  # Definindo o gerador de aumento de dados
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

  return test_loss, test_acc

# Execução principal
def main():
  print('Reading Dataset')
  # Lendo e processando o conjunto de dados
  dict_img, label_classes = read_dataset()

  print('Processing Images')
  X, y = process_images(dict_img)

  print('Pre Processing Images')
  pre_processed_images = preprocess_images(X)

  print('Converting Labels')
  label_to_id = {label: idx for idx, label in enumerate(label_classes)}
  y_numeric = np.array([label_to_id[label] for label in y])

  print('Splitting dataset')
  X_train, X_test, y_train, y_test = train_test_split(pre_processed_images, y_numeric, test_size=0.2)

  print('Building CNN')
  model = build_cnn(input_shape=(28, 28, 1), num_classes=len(label_classes))

  test_loss, test_acc = train_model(model, X_train, y_train, X_test, y_test)

  print(f'Test Loss: {test_loss}')
  print(f'Test Accuracy: {test_acc}')

  model_save_path = os.path.join(MODEL_PATH, "modelo.h5")
  model.save(model_save_path)
  print(f"Modelo salvo em: {model_save_path}")

if __name__ == "__main__":
  main()
