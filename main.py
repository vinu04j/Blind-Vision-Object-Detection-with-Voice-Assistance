import cv2
import threading
from object_detector import ObjectDetector
from voice_output import VoiceOutput
from gui import BlindVisionGUI

class BlindVisionApp:
    def __init__(self):
        self.detector = ObjectDetector()
        self.voice = VoiceOutput()
        self.gui = BlindVisionGUI(self)
        self.running = False
        self.language = "en"  # Default language
        self.camera = None
        
    def start_detection(self, language="en"):
        """Start object detection in a separate thread"""
        self.language = language
        self.running = True
        detection_thread = threading.Thread(target=self._detection_loop)
        detection_thread.daemon = True
        detection_thread.start()
        
    def _detection_loop(self):
        """Main detection loop"""
        self.camera = cv2.VideoCapture(0)
        
        if not self.camera.isOpened():
            self.voice.speak("Camera not found", self.language)
            return
        
        frame_count = 0
        detection_interval = 10  # Detect every 10 frames to reduce CPU usage
        
        while self.running:
            ret, frame = self.camera.read()
            
            if not ret:
                break
            
            # Detect objects every N frames
            if frame_count % detection_interval == 0:
                objects = self.detector.detect_objects(frame)
                if objects:
                    self.voice.speak_objects(objects, self.language)
                    self.gui.update_objects_display(objects)
            
            # Display frame in GUI
            self.gui.display_frame(frame)
            frame_count += 1
            
            # Check for exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.stop_detection()
    
    def stop_detection(self):
        """Stop object detection"""
        self.running = False
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = BlindVisionApp()
    app.gui.run()