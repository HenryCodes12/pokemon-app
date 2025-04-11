from PIL import Image

# Test if the image can be opened
try:
    img = Image.open("question_mark.png")  # Ensure the image is in the same folder as this script
    img.show()  # This will open the image using your default image viewer
except FileNotFoundError:
    print("Image not found")