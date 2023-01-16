#!/usr/bin/env python3
#   If you develop a new program, and you want it to be of the greatest
# possible use to the public, the best way to achieve this is to make it
# free software which everyone can redistribute and change under these terms.

#   To do so, attach the following notices to the program.  It is safest
# to attach them to the start of each source file to most effectively
# state the exclusion of warranty; and each file should have at least
# the "copyright" line and a pointer to where the full notice is found.

#        TO-DO List chat bot.
#        Copyright (C) 2022 - All Rights Reserved
#        Group:
#            Faiella Ciro              0622701816  c.faiella8@studenti.unisa.it
#            Giannino Pio Roberto      0622701713	p.giannino@studenti.unisa.it
#            Scovotto Luigi            0622701702  l.scovotto1@studenti.unisa.it
#            Tortora Francesco         0622701700  f.tortora21@studenti.unisa.it

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import cv2
import numpy as np
import random

from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
import os
from glob import glob
from scipy.spatial.distance import cosine
import numpy as np
import pickle
from time import sleep

import rospy
from std_msgs.msg import String, Bool

class Face_Recognition():
    """
    This class implements the face re-identification system using the ResNet50 pre-trained on VGGFace.
    """
    def __init__(self, means=np.array([131.0912, 103.8827, 91.4953]), input_size=(224,224)) -> None:
        rospy.init_node('face_recognition', anonymous=True)
        self._sub = rospy.Subscriber('new_person', String, queue_size=10)
        self._sub_start = rospy.Subscriber('start', Bool, queue_size=1)
        self._pub_rec = rospy.Publisher('recognition', String, queue_size=1)
        self._pub_det = rospy.Publisher('detection', Bool, queue_size=1)
        self.pub = rospy.Publisher('bot_answer', String, queue_size=10)
        self._webcam = cv2.VideoCapture(0) # 0 camera mia, 2 usb esterna
        self.means = means
        self.input_size = input_size
        self.dataset_path = os.getenv("PROJECT_DIR", default='/media/psf/TO-DO_List/ros_chatbot/chatbot_ws') + "/src/face_recognition/src/"
        self.model = VGGFace(model='resnet50', include_top=False, pooling='avg')
        self.people_dict = dict()
        # try opening a dictionary, in which the id-person-name pair are present;
        # the id represents the name of the training folder of a specific person
        try:
            with open('./dizionario4.pkl', 'rb') as f:
                self.people_dict = pickle.load(f)
                f.close()
        except:
            print('EOF exception')
        self.dataset_feature = self.train_feature(self.model)


    def add_training_data(self, bbox):
        """
        A method that take a sequential picture of the person, calculate the distance and add the new person in the 
        dataset.
        """
        tmp = None
        while tmp is None:
            self._pub_rec.publish(String('unkn0wn'))
            self.there_is_someone(bbox)
            try:
                tmp = rospy.wait_for_message("new_person", String, timeout=1)
            except:
                pass
        user = tmp.data

        data_to_send = String()
        data_to_send.data = "Move the head, i'm going to capture your face"
        self.pub.publish(data_to_send)

        id = self.people_dict.get(user)
        max = len(self.people_dict)
        if id is None:
            id = self.people_dict[user] =  max + 1
        if not os.path.exists(self.dataset_path + "dataset/training/" + str(id)):
            os.makedirs(self.dataset_path + "dataset/training/" + str(id))

        # Check success
        if not self._webcam.isOpened():
            raise Exception("Could not open video device")

        # Pic 20 frames from the webcam, get the face jpg and add to dataset.
        for i in range(20):
            frame = self._webcam.read()[1]
            face = self.get_face_jpg(bbox, frame)[0]
            cv2.imwrite(self.dataset_path + "dataset/training/"+ str(id) + "/image" + str(random.randint(1, 1000)) + str(i) + ".jpg", face)
            sleep(0.2)

        with open('./dizionario4.pkl', 'wb') as f:
            pickle.dump(self.people_dict, f)
            f.close()
        self.dataset_feature = self.train_feature(self.model)

    def _count_person_dataset(self):
        return len(self.people_dict)

    def extract_features(self, model, faceim):
        """
        This method takes as input the face recognition model and the filename of the image and returns the feature vector
        """
        faceim = cv2.resize(faceim, (224,224))
        faceim = preprocess_input([faceim.astype(np.float32)], version=2)
        feature_vector = (model.predict(faceim)).flatten()
        return feature_vector
    
    def get_face_box(self, frame, conf_threshold=0.8):
        """
        Method to take the bounding box of the face and return the bboxes of the faces and the frame with the rectangle draw
        """
        # Initialize detector
        faceProto = self.dataset_path + "opencv_face_detector.pbtxt"
        faceModel = self.dataset_path + "opencv_face_detector_uint8.pb"
        net = cv2.dnn.readNet(faceModel, faceProto)

        frameOpencvDnn  = frame.copy()
        frameHeight     = frameOpencvDnn.shape[0]
        frameWidth      = frameOpencvDnn.shape[1]
        
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
                cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight / 300)), 8)
        return frameOpencvDnn, bboxes

    def train_feature(self, model, number_of_training_images_per_person = 20):
        """
        Method that, with the net model and the number of images per person, performs 
        feature training and saves the results into a list, called database. Then, It returns the list.
        """
        number_of_known_people = self._count_person_dataset()
        database = []
        training_path = os.path.join(self.dataset_path, 'dataset', 'training')
        for i in range(number_of_known_people + 1):
            person_path = os.path.join(training_path, str(i))
            count = 0
            person = []
            for filename in glob(os.path.join(person_path, '*.jpg')):
                if count < number_of_training_images_per_person:
                    faceim = cv2.imread(filename)
                    feature_vector = self.extract_features(model, faceim)
                    person.append({"id": i, "feature_vector": feature_vector})
                    count += 1
                    print("Loading %d - %d" % (i, count))
            database.append(person)
        return database

    def evaluate_distance(self, face_reco_model, resized_face, dataset_feature):
        """
        Method that from the input face do the face recognition
        """
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
        """
        This method return the most common index into results. If latter is greater then 3 return the max index value,
        otherwise, return 0 (i.e. doesn't recognize the face).
        """
        count = np.bincount(results)
        max_result = np.amax(count)
        max_result_index = np.where(count == max_result)
        if max_result > 3:
            return max_result_index[0][0]
        else:
            return 0
        
    def get_face_jpg(self, bbox, frame):
        """
        In this method we pass the bounding box of the face and the frame, it will crop the face from the frame
        """
        padding = 0.2
        # Adjust crop
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        padding_px = int(padding * max(h, w))
        face = frame[max(0,bbox[1]-padding_px):min(bbox[3]+padding_px,frame.shape[0]-1),max(0,bbox[0]-padding_px):min(bbox[2]+padding_px, frame.shape[1]-1)]
        face = face[ face.shape[0]//2 - face.shape[1]//2 : face.shape[0]//2 + face.shape[1]//2, :, :]
        # Preprocess image
        resized_face = cv2.resize(face, self.input_size)
        return resized_face, w, h

    def there_is_someone(self, bboxes):
        """
        Method to check if inside the frame is a person.
        """
        x = Bool()
        i = 0
        for i, _ in enumerate(bboxes):
            i = i + 1
        x.data = y = True if i >= 1 else False
        self._pub_det.publish(x)
        return y

    def run(self):
        """
        Start an infinite loop that performs the face recognition and re-identification.
        """
        results = []
        person  = 'unkn0wn'
        start   = rospy.wait_for_message("start", Bool)
        while start.data:
            # Read frame
            ii = 0
            while ii < 10:
                frame = self._webcam.read()[1]
                frameFace, bboxes = self.get_face_box(frame) # Get face
                ret = 0 # when there is a swap in person
                if self.there_is_someone(bboxes):
                    for _, bbox in enumerate(bboxes):
                        face, w, h = self.get_face_jpg(bbox, frame)
                        # Predict
                        distance_calc = self.evaluate_distance(self.model, face, self.dataset_feature)
                        results.append(distance_calc[0])
                    ii = ii + 1
                    cv2.putText(frameFace, str(distance_calc[0]), (bbox[0]+w//20, bbox[1]+h//20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.imshow("Demo", frameFace)
                cv2.waitKey(1)
            ret = self.counter(results)
            # print(ret)
            results.clear()
            if ret == 0:
                self._pub_rec.publish(String('unkn0wn'))
                self.there_is_someone(bboxes)
                self.add_training_data(bbox)
            else:
                person = list(self.people_dict.keys())[list(self.people_dict.values()).index(ret)]
                print(person)
                self._pub_rec.publish(String(person))
                while self.there_is_someone(bboxes):
                    frame = self._webcam.read()[1]
                    frameFace,bboxes = self.get_face_box(frame)
                    self._pub_rec.publish(String(person))
                    print(self.there_is_someone(bboxes))
                    cv2.putText(frameFace, str(distance_calc[0]), (bbox[0]+w//20, bbox[1]+h//20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                    cv2.imshow("Demo", frameFace)
                    cv2.waitKey(1)

if __name__ == '__main__':
    r = Face_Recognition()
    r.run()
    exit(-1)