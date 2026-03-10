import cv2
import base64
import time

class Camera:
    def __init__(self):
        self.camera_index = 0
        self.cap = None
        self._open()

    def _open(self):
        """Internal method: open the camera safely."""
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_AVFOUNDATION)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        if not self.cap.isOpened():
            raise RuntimeError("Error: Could not open camera.")

        # Warm up the camera
        # time.sleep(2)
            
    def _close(self):
        """Internal method: release the camera safely."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()

    def take_picture(self):
        """
        Opens → captures → closes with retry logic.
        Returns a JPEG image as base64 string.
        """
        # MAX_RETRIES = 5
        
        # for attempt in range(MAX_RETRIES):
        #     try:
        #         print(f"Attempt {attempt + 1}: Opening camera...")
        #         self._open()
                
        #         ok, frame = self.cap.read()
        #         if not ok:
        #             raise RuntimeError("Failed to grab frame.")

        #         ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        #         if not ok:
        #             raise RuntimeError("Failed to encode frame as JPEG.")

        #         cv2.imwrite("pic.jpg", frame)
        #         print(f"Attempt {attempt + 1}: Success!")
        #         return base64.standard_b64encode(buf.tobytes()).decode("utf-8")
                
        #     except Exception as e:
        #         print(f"Attempt {attempt + 1}: Failed - {e}")
        #         if attempt < MAX_RETRIES - 1:
        #             time.sleep(1)
        #         else:
        #             raise RuntimeError(f"Failed to capture photo after {MAX_RETRIES} attempts")
        #     finally:
        #         self._close()
    
        # raise RuntimeError(f"Failed to capture photo after {MAX_RETRIES} attempts")
        """
        Captures a frame from the already-open camera.
        Returns a JPEG image as base64 string.
        """
        if self.cap is None or not self.cap.isOpened():
            raise RuntimeError("Camera is not open. Call open() first.")

        ok, frame = self.cap.read()
        if not ok:
            raise RuntimeError("Failed to grab frame.")

        ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        if not ok:
            raise RuntimeError("Failed to encode frame as JPEG.")

        cv2.imwrite("pic.jpg", frame)
        return base64.standard_b64encode(buf.tobytes()).decode("utf-8")

    def __del__(self):
        self._close()
