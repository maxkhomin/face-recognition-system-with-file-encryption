import os
import face_recognition
import cv2
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet


def face_id():
    if not os.path.exists("dataset"):
        print("[Error] there is no directory 'dataset'")
        return
    know_encodings = []
    images = os.listdir("dataset")
    images1 = os.listdir("dataset_web")
    ct = 0

    for image in images:
        face_img = face_recognition.load_image_file(f"dataset/{image}")
        face_enc = face_recognition.face_encodings(face_img)[0]
        know_encodings.append(face_enc)

    for image in images1:
        face_img = face_recognition.load_image_file(f"dataset_web/{image}")
        face_enc = face_recognition.face_encodings(face_img)[0]

        for item in range(len(know_encodings)):
            result = face_recognition.compare_faces([face_enc], know_encodings[item])
            if result[0]:
                ct += 1

    if ct >= 1:
        return True
    else:
        return False


def take_screen_from_web():
    cap = cv2.VideoCapture(0)
    count = 0
    ct = 0
    if not os.path.exists("dataset_web"):
        os.mkdir("dataset_web")
    while True:
        ret, frame = cap.read()

        if ret:
            frame_id = int(cap.get(1))

            cv2.imshow("frame", frame)
            cv2.waitKey(1)
            if frame_id == 0:
                count += 1
            if count % 50 == 0 and count <= 250:
                cv2.imwrite(f"dataset_web/{ct}.jpg", frame)
                print(f"Take a screenshot {ct}")
                ct += 1
            if count == 250:
                break
        else:
            print("[Error] Can't get the frame...")
    cap.release()
    cv2.destroyAllWindows()


def add_data_face():
    
    cap = cv2.VideoCapture(0)
    count = 0
    key = 'faceRec0gnition'

    print('Enter password to access the database or press Enter')
    password = input()

    print('Please enter your name')
    name = input()

    if len(password) != len(key):
        print('Incorrect password, access to the database is denied')
        return False
    else:
        for char1, char2 in zip(password, key):
            if char1 != char2:
                print('Incorrect password, access to the database is denied')
                return False

        print('Look at the camera, you will be added to the database')
        while True:
            ret, frame = cap.read()

            if ret:
                frame_id = int(cap.get(1))

                cv2.imshow("frame", frame)
                cv2.waitKey(1)
                if frame_id == 0:
                    count += 1

                if count % 100 == 0:
                    cv2.imwrite(f"dataset/{name}.jpg", frame)
                    print(f"Take a screenshot {name}")

                if count == 100:
                    break
            else:
                print("[Error] Can't get the frame...")
                break

        cap.release()
        cv2.destroyAllWindows()
        return True

# Функция для генерации ключа и сохранения его в файл
def generate_key(key_file):
    key = Fernet.generate_key()
    with open(key_file, "wb") as key_file:
        key_file.write(key)

# Функция для загрузки ключа из файла
def load_key(key_file):
    return open(key_file, "rb").read()

# Функция для шифрования файла
def encrypt_file(key_file, input_file, output_file):
    if not os.path.exists(key_file):
        generate_key(key_file)

    key = load_key(key_file)
    fernet = Fernet(key)

    with open(input_file, "rb") as file:
        file_data = file.read()
        encrypted_data = fernet.encrypt(file_data)

    with open(output_file, "wb") as file:
        file.write(encrypted_data)

    os.remove(input_file)

# Функция для расшифрования файла
def decrypt_file(key_file, input_file, output_file):
    key = load_key(key_file)
    fernet = Fernet(key)

    with open(input_file, "rb") as file:
        encrypted_data = file.read()
        decrypted_data = fernet.decrypt(encrypted_data)

    with open(output_file, "wb") as file:
        file.write(decrypted_data)

# Функция "Распознать лицо" для GUI
def recognize_face():
    take_screen_from_web()
    if face_id():
        decrypt_file("key_file", "encrypted_secret", "secret.txt")
        messagebox.showinfo("Access Granted", "Face recognized, access granted")
    else:
        messagebox.showinfo("Access Denied", "Face not recognized, access is denied")

# Функция "Добавить биометрию в базу данных" для GUI
def add_face():
    if add_data_face():
        messagebox.showinfo("Success", "Biometrics added to the database")
    else:
        messagebox.showwarning("Failure", "Failed to add biometrics")

# Функция "Зашифровать данные" для GUI
def encrypt_data():
    encrypt_file("key_file", "secret.txt", "encrypted_secret")
    messagebox.showinfo("Successfully", "The data has been encrypted.")

# Создание GUI
root = tk.Tk()
root.title("Face Recognition System")

recognize_button = tk.Button(root, text="Recognize Face", command=recognize_face)
recognize_button.pack(pady=10)

add_face_button = tk.Button(root, text="Add Biometrics to Database", command=add_face)
add_face_button.pack(pady=10)

encrypt_data_button = tk.Button(root, text="Encrypt Data", command=encrypt_data)
encrypt_data_button.pack(pady=10)

root.mainloop()
