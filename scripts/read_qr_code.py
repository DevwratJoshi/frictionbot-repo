import cv2

class QRCodeReader:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)   
        self.qrCodeDetector = cv2.QRCodeDetector()
    # Capture frame-by-frame

    def show_video(self):
        while True:
            ret, frame = self.cap.read()
            # Our operations on the frame come here
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Display the resulting frame
            cv2.imshow('frame',gray)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything done, release the capture
        self.cap.release()
        cv2.destroyAllWindows()

    def detect(self):
        while True:
            ret, frame = self.cap.read()
            decodedText, points, _ = self.qrCodeDetector.detectAndDecode(frame)
            if not points is None:
                # The points list contains the corner coordinates of qr codes in the list
                # The decodedText list contains decoded qr codes  in the same order as points
                # TODO: Lower the frame rate to speed up the process
                for point in points:
                    print(point)
                    for p in point:
                        cv2.circle(frame, tuple(p), 10, (1.,0.,0.), -1)
            else:
                print("QR code not detected")
            
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.cap.release()
        cv2.destroyAllWindows()
if __name__ == '__main__':
    q = QRCodeReader()

    i = ""
    while True:
        print("Enter s to show video")
        print("Enter d to detect")
        print("Enter x to exit")
        i = input()
        if i == 's':
            q.show_video()
        elif i == 'd':
            q.detect()
        elif i == 'x':
            break


