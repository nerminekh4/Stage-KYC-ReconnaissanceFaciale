import cv2
import easyocr
import matplotlib.pyplot as plt

# 1. Charger l'image
image_path = 'identite_test.JPG'
image = cv2.imread(image_path)

# 2. Afficher l'image
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.title("Image d'identité chargée")
plt.show()

# 3. OCR avec EasyOCR
reader = easyocr.Reader(['fr'])  # langue française
results = reader.readtext(image_path)

# 4. Afficher les résultats de l’OCR
print("\n--- Résultats OCR ---")
for (bbox, text, prob) in results:
    print(f"{text} (confiance : {prob:.2f})")
