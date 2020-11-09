import cv2
from pyzbar import pyzbar

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
        
        	# find the barcodes in the frame and decode each of the barcodes
	        
            barcodes = pyzbar.decode(frame)
            for barcode in barcodes:
                # extract the bounding box location of the barcode and draw
                # the bounding box surrounding the barcode on the image
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                # the barcode data is a bytes object so if we want to draw it
                # on our output image we need to convert it to a string first
                barcodeData = barcode.data.decode("utf-8")
                barcodeType = barcode.type
                # draw the barcode data and barcode type on the image
                text = "{} ({})".format(barcodeData, barcodeType)
                cv2.putText(frame, text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

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


