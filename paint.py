import tkinter as tk

from PIL import Image, ImageOps
import numpy as np
import tensorflow as tf

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Drawing App with Digit Recognition")

        self.canvas = tk.Canvas(root, bg="white", width=600, height=300)
        self.canvas.pack()

        self.setup()
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

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

    def recognize_digit(self):
        # Salvar o desenho atual do canvas em um arquivo temporário
        self.canvas.postscript(file="temp_canvas.eps")
        img = Image.open("temp_canvas.eps")
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
