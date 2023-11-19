import tkinter as tk
from PIL import Image, ImageOps
import cv2 
import numpy as np
import tensorflow as tf
import os

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Drawing App with Digit Recognition")

        self.canvas = tk.Canvas(root, bg="white", width=600, height=300)
        self.canvas.pack()

        self.setup()
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        # Botão para exportar caracteres
        self.button_export = tk.Button(root, text="Exportar png", command=self.export_characters)
        self.button_export.pack()

        self.export_count = 0  # Inicializar o contador para nomes únicos de arquivo
        self.word = ""  # Inicializar a string para armazenar a palavra atual

        # Botão para reconhecimento de dígitos
        self.button_recognize = tk.Button(root, text="Reconhecer Dígito", command=self.recognize_digit)
        self.button_recognize.pack()

        # Carregar o modelo treinado
        self.model = tf.keras.models.load_model('handwritten_digits.model')

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = 2
        self.color = "black"

    def paint(self, event):
        x, y = event.x, event.y
        if self.old_x and self.old_y:
            self.canvas.create_line(self.old_x, self.old_y, x, y,
                                    width=self.line_width, fill=self.color,
                                    capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36)
        self.old_x = x
        self.old_y = y

    def reset(self, event):
        self.old_x, self.old_y = None, None

    def export_characters(self):
        # Salvar o desenho atual do canvas em um arquivo temporário
        self.export_count += 1  # Incrementar o contador
        temp_filename = f"temp_canvas_{self.export_count}.png"

        # Encontrar um nome de arquivo único para o desenho atual
        while os.path.exists(temp_filename):
            self.export_count += 1
            temp_filename = f"temp_canvas_{self.export_count}.png"

        self.save_canvas_image(temp_filename)

        # Reconhecer os caracteres na imagem
        characters = self.recognize_characters(temp_filename)

        # Criar o diretório se não existir
        char_directory = "chars"
        if not os.path.exists(char_directory):
            os.makedirs(char_directory)

        # Exportar cada caractere individualmente
        for i, char in enumerate(characters):
            char_filename = f"chars/char_{self.export_count}_{i}.png"
            # Encontrar um nome de arquivo único para o caractere
            while os.path.exists(char_filename):
                i += 1
                char_filename = f"chars/char_{self.export_count}_{i}.png"
            char.save(char_filename, "png")
            print(f"Caractere exportado como {char_filename}")

        print(f"Palavra exportada como {temp_filename}")
        self.word = ""  # Resetar a palavra após a exportação

    def save_canvas_image(self, filename):
        self.canvas.postscript(file="temp_canvas.eps", colormode="color")
        img = Image.open("temp_canvas.eps")
        img.save(filename, "png")

    def recognize_characters(self, image_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        # Aplicar filtro gaussiano para suavizar a imagem
        img = cv2.GaussianBlur(img, (5, 5), 0)

        # Aplicar limiarização para binarizar a imagem
        _, threshold_img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Encontrar contornos dos caracteres
        contours, hierarchy = cv2.findContours(threshold_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Ordenar os contornos da esquerda para a direita
        contours = sorted(contours, key=lambda x: (cv2.boundingRect(x)[1], cv2.boundingRect(x)[0]))

        # Extrair os caracteres
        char_images = []
        for i, contour in enumerate(contours):
            # Encontrar o retângulo delimitador do contorno
            x, y, w, h = cv2.boundingRect(contour)

            # Extrair a região da imagem dentro do retângulo delimitador
            char_array = threshold_img[y:y + h, x:x + w]

            # Ignorar regiões muito pequenas
            if w > 10 and h > 10:
                # Converter para imagem PIL
                char_image = Image.fromarray(char_array)
                char_images.append(char_image)

        return char_images

    def recognize_digit(self):
        # Salvar o desenho atual do canvas em um arquivo temporário
     #   self.canvas.postscript(file="temp_canvas.png")
        img = Image.open("temp_canvas.png")
        img = img.resize((28, 28))  # Redimensionar a imagem
        img = ImageOps.grayscale(img)

        # Preparar a imagem para o modelo
        img_array = np.array(img)
        img_array = img_array / 255.0
        img_array = img_array.reshape(1, 28, 28, 1)

        # Fazer a predição
        prediction = self.model.predict(img_array)
        digit = np.argmax(prediction)

        # Mostrar o resultado
        print("Dígito Reconhecido:", digit)   

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()