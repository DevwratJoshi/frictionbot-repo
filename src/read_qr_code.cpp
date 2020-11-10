#include <iostream>
#include <algorithm>
#include <vector>
#include <zbar.h>

#include <opencv2/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/videoio.hpp>

using namespace std;
using namespace cv;
using namespace zbar;

typedef struct
{
  string type;
  string data;
  vector <Point> location;
}decodedObject;

// Find and decode barcodes and QR codes
Point get_code_center(vector<Point> corners)
{
    Point center;
    int points = 0;
    for(Point corner: corners)
    {
        center.x = center.x + corner.x; 
        center.y = center.y + corner.y; 
        points += 1;
    }

    center.x = center.x/points;
    center.y = center.y/points;

    return center;

}
void decode(Mat &im, vector<decodedObject>&decodedObjects)
{

  // Create zbar scanner
  ImageScanner scanner;

  // Configure scanner
  scanner.set_config(ZBAR_QRCODE, ZBAR_CFG_ENABLE, 1);

  // Convert image to grayscale
  Mat imGray;
  cvtColor(im, imGray,CV_BGR2GRAY);
  threshold( imGray, imGray, 127, 255, THRESH_BINARY);  
  // Wrap image data in a zbar image
  Image image(im.cols, im.rows, "Y800", (uchar *)imGray.data, im.cols * im.rows);

  // Scan the image for barcodes and QRCodes
  int n = scanner.scan(image);

  // Print results
  for(Image::SymbolIterator symbol = image.symbol_begin(); symbol != image.symbol_end(); ++symbol)
  {
    decodedObject obj;

    obj.type = symbol->get_type_name();
    obj.data = symbol->get_data();

    // Print type and data
    // cout << "Type : " << obj.type << endl;
    // cout << "Data : " << obj.data << endl << endl;
    // Obtain location
    for(int i = 0; i< symbol->get_location_size(); i++)
    {
      obj.location.push_back(Point(symbol->get_location_x(i),symbol->get_location_y(i)));
    }
    if(obj.type == "QR-Code")
    {
        Point center = get_code_center(obj.location);
        circle(im, center, 10, Scalar(0,255,255), -1, FILLED,0);
    }
    decodedObjects.push_back(obj);
  }
}

int main(int argc, char *argv[])
{

  // Read image
    // string imagepath = argv[1];
    VideoCapture cap(0);
    cap.set(CV_CAP_PROP_FPS, 10);
    vector<decodedObject> decodedObjects;
    while(1)
    {
        decodedObjects.clear();
        Mat frame;
        // Capture frame-by-frame
        cap >> frame;
    
        // If the frame is empty, break immediately
        if (frame.empty())
        {
           continue;
           cout << "Frame empty \n" << endl;
        }

        decode(frame, decodedObjects);
        
        // Display the resulting frame
        imshow("Frame", frame );

        // Press  ESC on keyboard to exit
        char c=(char)waitKey(25);
        if(c==27)
            break;
  }
   // Variable for decoded objects

   // Find and decode barcodes and QR codes

    return 0;
 }