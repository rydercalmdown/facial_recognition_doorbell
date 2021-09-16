import os
import logging
import face_recognition


class FaceRecognizer():
    """Face recognition module for facial-recognition doorbell"""

    def __init__(self):
        self._load_known_faces()

    def _load_known_faces(self):
        """Loads known faces from the filesystem"""
        faces_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'faces')
        faces = [
            os.path.join(faces_dir, f) for f in os.listdir(faces_dir) \
            if f.endswith('.jpeg') or f.endswith('.jpg') or f.endswith('.png')
        ]
        known_images = [face_recognition.load_image_file(i) for i in faces]
        self.known_faces = []
        self.faces_names = [x.split('/')[-1].split('.')[0].replace('_', ' ').title() for x in faces]
        for image in known_images:
            encoding = face_recognition.face_encodings(image)
            if len(encoding) > 0:
                logging.debug('Adding known face')
                self.known_faces.append(encoding[0])

    def check_for_known_faces(self, frame):
        """Checks for known faces and returns names or None"""
        faces_detected = face_recognition.face_encodings(frame)
        if len(faces_detected) > 0:
            unknown = face_recognition.face_encodings(frame)[0]
            results = face_recognition.compare_faces(self.known_faces, unknown)
            if True in results:
                logging.info('Known face detected')
                return [self.faces_names[index] for index, value in enumerate(results)]
            logging.info('Unknown face detected')
            return False
