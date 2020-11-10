#include <iostream>
#include <algorithm>
#include <vector>
#include <zbar.h>

#include <opencv2/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/aruco.hpp>

using namespace std;
using namespace cv;
using namespace zbar;

// Find and decode barcodes and QR codes
Point get_code_center(std::vector<Point2f> corners)
{
    Point center;
    int points = 0;
    for(Point corner: corners)
    {
        center.x = center.x + corner.x; 
        center.y = center.y + corner.y; 
        points += 1;
    }

    center.x = (int)(center.x/points);
    center.y = (int)(center.y/points);

    return center;

}


int main(int argc, char *argv[])
{
  std::cout << "Reading aruco markers" << std::endl;
  // Read image
    // string imagepath = argv[1];
    VideoCapture cap(0);
    cv::Ptr<cv::aruco::Dictionary> dictionary = aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_100);
    std::vector<std::vector<Point2f> > corners;
    std::vector<int> ids;
    while(1)
    {
        corners.clear();
        ids.clear();
        Mat frame;
        // Capture frame-by-frame
        cap >> frame;
        Mat binary_frame;
        cvtColor(frame, binary_frame,CV_BGR2GRAY);
        threshold( binary_frame, binary_frame, 100, 255, THRESH_BINARY);
        cv::aruco::detectMarkers(frame, dictionary, corners, ids);
        // If the frame is empty, break immediately
        if (frame.empty())
        {
           continue;
           cout << "Frame empty \n" << endl;
        }

        aruco::detectMarkers(frame, dictionary, corners, ids);
        for(std::vector<Point2f> corner: corners)
        {
          Point center = get_code_center(corner);
          circle(frame, center, 10, Scalar(255,255,0), -1, FILLED,0);

        }      
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