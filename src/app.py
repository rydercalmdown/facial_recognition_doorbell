import os
import logging
import threading
import time
import subprocess
from rtsparty import Stream
from objectdaddy import Daddy
from face_recognizer import FaceRecognizer


class Doorbell():

    def __init__(self):
        logging.info('Starting doorbell')
        self.person_at_door = False
        self.announcement = None
        self.doorbell_ring_timeout = 1
        self._setup_stream()
        self._setup_object_recognition()
        self._setup_facial_recognition()

    def _setup_stream(self):
        """Set up the stream to the camera"""
        logging.info('Starting stream')
        self.stream = Stream(os.environ.get('STREAM_URI'))

    def _setup_object_recognition(self):
        """Set up object recognition and load models"""
        logging.info('Loading ML models')
        self.daddy = Daddy()
        self.daddy.set_callbacks(self.object_detected, self.object_expired)

    def _setup_facial_recognition(self):
        """Set up facial recognition"""
        self.facial_recognizer = FaceRecognizer()

    def object_detected(self, detection):
        """Callback for an object being detected"""
        logging.info(f'{detection.label} detected')
        try:
            if detection.is_person():
                self.person_at_door = True
        except Exception:
            pass

    def object_expired(self, detection):
        """Callback for an object expiring"""
        logging.info(f'{detection.label} expired')
        self.announcement = None
        try:
            if detection.is_person():
                self.person_at_door = False
        except Exception:
            pass

    def check_for_known_faces(self, frame):
        """Checks the latest frame for known faces"""
        results = self.facial_recognizer.check_for_known_faces(frame)
        if not results:
            self.announcement = None
        else:
            if len(results) == 1:
                announcement = f'{results[0]} is at the door'
            else:
                announcement = f'{" ".join(results)} are at the door'
            self.announcement = announcement
            logging.info(announcement)

    def make_announcement(self):
        """Makes an announcement with text to speech"""
        logging.info('Announcing: {}'.format(self.announcement))
        subprocess.call(['say', "'" + self.announcement + "'"], stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)

    def ring_doorbell(self):
        """Plays the doorbell sound effect"""
        if self.announcement:
            self.make_announcement()
        logging.info('Ringing doorbell')
        base_dir = os.path.dirname(os.path.realpath(__file__))
        doorbell_audio = os.path.join(base_dir, 'audio/doorbell.mp3')
        subprocess.call(['mpg321', doorbell_audio], stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)

    def doorbell_listener(self):
        """Listens for the change of self.person_at_door"""
        while True:
            if self.person_at_door:
                self.ring_doorbell()
                time.sleep(self.doorbell_ring_timeout)
            else:
                time.sleep(0.5)

    def start_doorbell_listener_thread(self):
        """Starts the doorbell_listener function in a background thread"""
        server_thread = threading.Thread(name='doorbell_listener', target=self.doorbell_listener)
        server_thread.setDaemon(True)
        server_thread.start()

    def process_frames_from_stream(self):
        """Processes the frames from the stream"""
        while True:
            frame = self.stream.get_frame()
            if self.stream.is_frame_empty(frame):
                continue
            self.latest_frame = frame
            results, frame = self.daddy.process_frame(frame)
            if self.person_at_door:
                self.check_for_known_faces(frame)

    def run(self):
        """Run the application"""
        self.start_doorbell_listener_thread()
        try:
            self.process_frames_from_stream()
        except KeyboardInterrupt:
            logging.info('Exiting application')


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    db = Doorbell()
    db.run()
