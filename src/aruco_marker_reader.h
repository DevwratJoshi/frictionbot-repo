#ifndef ARUCOREADER_H
#define ARUCOREADER_H
#include <iostream>
#include <vector>
#include <opencv2/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/aruco.hpp>

#define MARKER_SIDE_LENGTH 40 //Each marker is assumed to have a 40 mm side length
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
        // This factor will determine the number of pixels per mm
        float current_pixels_per_mm;  
        float current_side_length;
    private:
    cv::Point get_code_center(std::vector<cv::Point2f> corners);
    cv::Ptr<cv::aruco::Dictionary> dictionary;
    void get_pixels_per_mm_factor(std::vector<std::vector<cv::Point2f>> markers);
};

// Constructor
ArucoReader::ArucoReader()
{
    this->dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_100);
    this->current_pixels_per_mm = 0.;
    this->current_side_length = 0.;

}
// Decstructor
ArucoReader::~ArucoReader()
{
}
void ArucoReader::get_pixels_per_mm_factor(std::vector<std::vector<cv::Point2f>> markers)
{
  // Get the average side length in pixels of each marker in the frame
  float overall_avg_side_length = 0;
  for(std::vector<cv::Point2f> marker_vertices : markers)
  { 
    // Get the average side length in pixels of each side of a marker 
    float current_marker_side_length = 0.;
    for(int i = 0; i < 4; i++) // There are 4 vertices in each "marker". Add up the distance between each neighboring pair
    {
      int next_index = (i+1)%4; // This is so that when i is 2, the final index will be 0, not 4
      current_marker_side_length += sqrt(pow(marker_vertices[i].x - marker_vertices[next_index].x, 2) 
                                       + pow(marker_vertices[i].y - marker_vertices[next_index].y, 2));
    }
    current_marker_side_length /= 4.0; // 4 sides for each marker

    overall_avg_side_length += current_marker_side_length;
  }
  overall_avg_side_length /= markers.size();

  this->current_side_length = overall_avg_side_length;
  // Use this side length to get the average side length in mm for the markers
  this->current_pixels_per_mm = overall_avg_side_length/MARKER_SIDE_LENGTH;

  // Get the conversion factor between pixels and mm
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

    this->get_pixels_per_mm_factor(corners);
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