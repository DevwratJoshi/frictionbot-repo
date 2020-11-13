#ifndef ARUCOREADER_H
#define ARUCOREADER_H
#include <iostream>
#include <vector>
#include <opencv2/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/aruco.hpp>

 
typedef struct
{
    cv::Point center;
    int id;
    bool is_seed;
}marker_state; 

class ArucoReader
{
    public:
        ArucoReader();
        ~ArucoReader();
        std::vector<marker_state> markers;
        void detect_markers(cv::Mat& frame);

    private:
    cv::Point get_code_center(std::vector<cv::Point2f> corners);
    cv::Ptr<cv::aruco::Dictionary> dictionary;
};

// Constructor
ArucoReader::ArucoReader()
{
    this->dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_100);

}
// Decstructor
ArucoReader::~ArucoReader()
{
}
cv::Point ArucoReader::get_code_center(std::vector<cv::Point2f> corners)
{
    cv::Point center;
    int points = 0;
    for(cv::Point corner: corners)
    {
        center.x = center.x + corner.x; 
        center.y = center.y + corner.y; 
        points += 1;
    }

    center.x = (int)(center.x/points);
    center.y = (int)(center.y/points);

    return center;

}

void ArucoReader::detect_markers(cv::Mat& frame)
{
    std::vector<std::vector<cv::Point2f> > corners;
    std::vector<int> ids;
    cv::Mat binary_frame;
    cv::cvtColor(frame, binary_frame,CV_BGR2GRAY);
    cv::threshold( binary_frame, binary_frame, 100, 255, cv::THRESH_BINARY);
    cv::aruco::detectMarkers(binary_frame, this->dictionary, corners, ids);

    this->markers.clear();
    this->markers.resize(corners.size() + 10); // Larger than it needs to be
    int counter = 0;
    while(counter < corners.size())
    {
        cv::Point center = this->get_code_center(corners[counter]);
        cv::putText(frame, std::to_string(ids[counter]), center, 
    cv::FONT_HERSHEY_COMPLEX_SMALL, 0.8, cvScalar(200,200,250), 1, CV_AA);

        int id = ids[counter];
        marker_state m;
        m.center = center;
        m.id = id;
        this->markers[counter] = m;    
        counter++;    
    }

    this->markers.erase(this->markers.begin()+counter, this->markers.end());

}
#endif