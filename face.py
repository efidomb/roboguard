import cv2
import os
import time
from watson_developer_cloud import VisualRecognitionV3, WatsonApiException
import json
import uuid


class Person(object):
    def __init__(self, name='dummy', age='dummy', gender='dummy'):
        self.name = name
        self.age = age
        self.gender = gender

    def __str__(self):
        msg = 'name: {0} age:{1} gender:{2}'
        return msg.format(self.name, self.age, self.gender)


def ask_watson_built_in(file_path):
    visual_recognition = VisualRecognitionV3(
        '2018-03-19', iam_api_key='**********')
    with open(file_path, 'rb') as images:
        response = visual_recognition.detect_faces(images)
        g_a_f = response.items()[0][1][0].items()[1][1][0].items()
        return g_a_f


def resize_image(filename, x, y, w, h, tmp):
    add_size = 20
    new_image_name = os.path.join('temp', str(uuid.uuid1()) + '.jpg')
    img = cv2.imread(filename)
    crop_img = img[(y - add_size):y + (h + add_size), (x - add_size):x + (w + add_size)]
    cv2.imwrite(new_image_name, crop_img)
    return new_image_name


def ask_to_watson(file_path):
    visual_recognition = VisualRecognitionV3(
        '2018-03-19', iam_api_key='**********')
    with open(file_path, 'rb') as images:
        try:
            response = visual_recognition.classify(images, threshold=0.0,
                                                   classifier_ids='**********')
            # print(json.dumps(response, indent=1))
            try:
                name = response.items()[0][1][0].items()[1][1][0].items()[0][1][0].items()[1][1]
                return name.split('.')[0]
            except Exception as e:
                return None
        except WatsonApiException as ex:
            print "Status code: {}\nError message: {}\nError info: \n{}" \
                .format(ex.code, ex.message, json.dumps(ex.info, indent=1))


def get_person_info_from_watson(img):
    p = Person()
    try:
        g_a_f = ask_watson_built_in(img)
        name = ask_to_watson(img)
        p.name = name
        gender = g_a_f[0][1].items()[0][1]
        p.gender = gender
        min = g_a_f[1][1].items()[2][1]
        max = g_a_f[1][1].items()[0][1]
        age = (max + min) / 2
        p.age = age if age >20 else 24

    except Exception as e:
        pass
    return p


def face_detect(imagePath):
    imag = None
    # Get user supplied values

    cascPath = "haarcascade_frontalface_default.xml"

    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier(cascPath)

    # Read the image
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),

    )

    print("Found {0} faces!".format(len(faces)))
    imags = []
    # Draw a rectangle around the faces
    for i, (x, y, w, h) in enumerate(faces):
        imag = resize_image(imagePath, x, y, w, h, i)
        imags.append(imag)
    return imags


def execute_face_recognaize(root):
    while True:
        while len(os.listdir(root)) > 0:
            for img in os.listdir(root):
                full_img = os.path.join(root, img)
                if not full_img.endswith('ini'):
                    time.sleep(0.1)
                    imgs = face_detect(full_img)
                    if img:
                        for img in imgs:
                            p = get_person_info_from_watson(img)
                            print str(p)
                    try:
                        os.remove(full_img)
                    except Exception as e:
                        pass

        time.sleep(0.2)


execute_face_recognaize(r'~home/pi')