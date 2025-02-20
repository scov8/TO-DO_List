import cv2
import numpy as np
import random

from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
import os
from glob import glob
from scipy.spatial.distance import cosine
# from sklearn.metrics import accuracy_score, confusion_matrix
import tensorflow as tf
import numpy as np
import pickle
from time import sleep

class Face_Recognition():

    def __init__(self, means = np.array([131.0912, 103.8827, 91.4953]), input_size = (224,224)) -> None:
        self._webcam = cv2.VideoCapture(0)
        self.means = means
        self.input_size = input_size
        self.dataset_path = ''
        self.model = VGGFace(model='resnet50', include_top=False, pooling='avg')
        self.dataset_feature = self.train_feature(self.model)

    def add_training_data(self, bbox):
        try:
            with open('dict.pkl', 'rb') as f:
                people_dict = pickle.load(f)
                f.close()
        except EOFError:
            people_dict = dict()
        user=input("Enter the name of the person \n")
        id = people_dict.get(user)
        max=len(people_dict)
        if id is None:
            id = people_dict[user] =  max + 1
        if not os.path.exists("dataset/training/" + str(id)):
            os.makedirs("dataset/training/" + str(id))
        # Check success
        if not self._webcam.isOpened():
            raise Exception("Could not open video device")
        # Read picture. ret === True on success
        for i in range(20):
            frame = self._webcam.read()[1]
            face = self.get_face_jpg(bbox, frame)[0]
            cv2.imwrite("dataset/training/"+ str(id) + "/image" + str(random.randint(1, 1000)) + str(i) + ".jpg", face)
            sleep(0.2)

        with open('dict.pkl', 'wb') as f:
            pickle.dump(people_dict, f)
            f.close()

        self.dataset_feature = self.train_feature(self.model)

    def _count_person_dataset(self):
        try:
            with open('dict.pkl', 'rb') as f:
                people_dict = pickle.load(f)
        except EOFError:
            people_dict = dict()
        return len(people_dict)


    def extract_features(self, model, faceim):
        """
        This method takes as input the face recognition model and the filename of the image and returns the feature vector
        """
        faceim = cv2.resize(faceim, (224,224))
        faceim = preprocess_input([faceim.astype(np.float32)], version=2)
        feature_vector = (model.predict(faceim)).flatten()
        return feature_vector
    
    def get_face_box(self, frame, conf_threshold=0.8):
        # Initialize detector
        faceProto = "opencv_face_detector.pbtxt"
        faceModel = "opencv_face_detector_uint8.pb"
        net = cv2.dnn.readNet(faceModel, faceProto)

        frameOpencvDnn = frame.copy()
        frameHeight = frameOpencvDnn.shape[0]
        frameWidth = frameOpencvDnn.shape[1]
        
        #swapRB =True
        # flag which indicates that swap first and last channels in 3-channel image is necessary.
        #crop = False
        # flag which indicates whether image will be cropped after resize or not
        # If crop is false, direct resize without cropping and preserving aspect ratio is performed
        blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

        net.setInput(blob)
        detections = net.forward()
        bboxes = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf_threshold and detections[0, 0, i, 5] < 1 and detections[0, 0, i, 6] < 1:
                x1 = int(detections[0, 0, i, 3] * frameWidth)
                y1 = int(detections[0, 0, i, 4] * frameHeight)
                x2 = int(detections[0, 0, i, 5] * frameWidth)
                y2 = int(detections[0, 0, i, 6] * frameHeight)
                bboxes.append([x1, y1, x2, y2])
                cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight/300)), 8)
        return frameOpencvDnn, bboxes

    def train_feature(self,model, number_of_training_images_per_person = 20):
        number_of_known_people = self._count_person_dataset()
        database = []
        training_path = os.path.join(self.dataset_path, 'dataset', 'training')
        for i in range(number_of_known_people+1):
            person_path = os.path.join(training_path, str(i))
            count = 0
            person = []
            for filename in glob(os.path.join(person_path,'*.jpg')):
                if count < number_of_training_images_per_person:
                    faceim = cv2.imread(filename)
                    feature_vector = self.extract_features(model, faceim)
                    person.append({"id": i, "feature_vector": feature_vector})
                    count += 1
                    print("Loading %d - %d" % (i, count))
            database.append(person)
        return database

    def calcolo_distanza(self, face_reco_model, resized_face, dataset_feature):
        rejection_threshold = 0.5

        feature_vector = self.extract_features(face_reco_model, resized_face)
        min_distance = [0, 1000000000000]
        for person in dataset_feature:
            for face in person:
                distance = cosine(feature_vector, face['feature_vector'])
                if distance < min_distance[1] and distance < rejection_threshold:
                    min_distance[0] = face['id']
                    min_distance[1] = distance
        return min_distance
        
    def counter(self, results):
        count = np.bincount(results)
        max_result = np.amax(count)
        max_result_index = np.where(count == max_result)

        if(max_result>8):
            return max_result_index[0][0]
        else:
            return 0
        
    def get_face_jpg(self, bbox, frame):
        padding = 0.2
        # Adjust crop
        w = bbox[2]-bbox[0]
        h = bbox[3]-bbox[1]
        padding_px = int(padding*max(h,w))
        face = frame[max(0,bbox[1]-padding_px):min(bbox[3]+padding_px,frame.shape[0]-1),max(0,bbox[0]-padding_px):min(bbox[2]+padding_px, frame.shape[1]-1)]
        face = face[ face.shape[0]//2 - face.shape[1]//2 : face.shape[0]//2 + face.shape[1]//2, :, :]
        # Preprocess image
        resized_face = cv2.resize(face, self.input_size)
        return resized_face,w,h

    def there_is_someone(self, bboxes):
        return True if enumerate(bboxes)!=0 else False

    def run(self):
        results = []
        while True:
            # Read frame 
            ret, frame = self._webcam.read()
            frameFace, bboxes = self.get_face_box(frame)     # Get face

            for i, bbox in enumerate(bboxes):
                face,w,h = self.get_face_jpg(bbox, frame)
                # blob = np.array([resized_face.astype(float)-MEANS])
                # Predict
                distance_calc = self.calcolo_distanza(self.model, face, self.dataset_feature)
                results.append(distance_calc[0])
                if len(results)==10:
                    ret = self.counter(results)
                    print(ret)
                    results.clear()
                    if ret == 0:
                        self.add_training_data(bbox)
                # Draw
                cv2.putText(frameFace, str(distance_calc[0]), (bbox[0]+w//20, bbox[1]+h//20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow("Demo", frameFace)
            cv2.waitKey(1)

if __name__ == "__main__":
    r = Face_Recognition()
    r.run()