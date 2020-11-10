import cv2
from pyzbar import pyzbar
import imutils
class QRCodeReader:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)   
        # self.qrCodeDetector = cv2.QRCodeDetector()
        # This is a dictionary of known QR codes
        # Any newly detected code will be added in it if it begins with the substring "module" [:6]
        self.QR_codes = {}
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
        ret, frame = self.cap.read()
        #gray = imutils.resize(frame, width=400)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        (thresh, gray) = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        # TODO Pass a cropped window subsection of the image to the decoder to speed up the process
        # find the barcodes in the frame and decode each of the barcodes
        
        barcodes = pyzbar.decode(gray)
        for barcode in barcodes:
            # extract the bounding box location of the barcode and draw
            # the bounding box surrounding the barcode on the image
            (x, y, w, h) = barcode.rect
            # cv2.circle(frame, (x,y), 8, (255,0,0), -1)
            # the barcode data is a bytes object so if we want to draw it
            # on our output image we need to convert it to a string first
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            barcodeData = barcode.data.decode("utf-8")
            if(barcodeData[:6] == "module"):
                center = (int(x+w/2),int(y+h/2))
                self.QR_codes[barcodeData] = {"coords":center}


            # barcodeType = barcode.type
            # draw the barcode data and barcode type on the image
            # text = "{}".format(barcodeData)
            # cv2.putText(frame, text, (x, y - 10),
            #     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        return frame


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
            frame = []
            while True:
                frame = q.detect()
                print("Codes found so far are: ")
                for key in q.QR_codes:
                    print(key)
                    cv2.circle(frame, q.QR_codes[key]["coords"], 8, (255,0,0), -1)
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            q.cap.release()
            cv2.destroyAllWindows()

        elif i == 'x':
            break


