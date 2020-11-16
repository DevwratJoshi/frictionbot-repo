#include "aruco_marker_reader.h"
#include<stdio.h>
#include<stdlib.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<netinet/in.h>
#include<thread>
#include <unistd.h>
// The id of the seed module. Defined here
#define SEED_ID 1 
// Separate distance values for high and low friction. Hysterisis for stability
#define HIGH_FRICTION_THRESHOLD_DISTANCE 100 // If the distance to the seed is less than this, friction high
#define LOW_FRICTION_THRESHOLD_DISTANCE 200 // If distance to the seed is greater than this, friction low
typedef struct 
{
  int id; // The id of the module
  float position[2]; // x,y position of the module, in real world coordinates
  bool high_friction; // determine whether the module should be high friction
}module_state;

class CentralController
{
  public:
  CentralController();
  ~CentralController();
  ArucoReader reader;
  // Store the states of the modules and respond with the appropriate value when queried by a module
  std::vector<module_state> module_states; 
  void store_module_states();
  bool get_module_state_from_id(module_state& mo_s, int id);

  private:
  void evaluate_module_states();
  module_state get_module_state_from_marker_state(marker_state state);
  float high_fric_dist_thresh_pixels; // The threshold distances in pixels 
  float low_fric_dist_thresh_pixels;  // Calculated using the mm to pixel conversion factor stored by the marker reader
  bool update_state_flag;
  std::thread thr1;
};

CentralController::CentralController():update_state_flag(true)
{
  // Initialize the thread keep getting detected AR markers and their positions
  this->thr1 = std::thread(&CentralController::store_module_states, this);
  this->high_fric_dist_thresh_pixels = 0.;
  this->low_fric_dist_thresh_pixels = 0.;


}
CentralController::~CentralController()
{
  this->thr1.join();
}
bool CentralController::get_module_state_from_id(module_state& mo_s, int id)
{
  // Get a copy of the state to avoid memory access conflicts
  // Maybe inefficient
  std::vector<module_state> module_states_copy = this->module_states;
  for(module_state m : module_states_copy)
  {
    if(m.id == id)
    {
      mo_s = m;
      return true;
    }

  }
  return false;
}
module_state CentralController::get_module_state_from_marker_state(marker_state state)
{
  module_state m;
  m.id = state.id;
  m.high_friction = false;
  // TODO: Add a section to convert screen coordinates to real-world coordinates if required. 
  // Directly saving screen coordinates as real world coordinates for now

  m.position[0] = state.center.x;
  m.position[1] = state.center.y;
  return m;
}
void CentralController::evaluate_module_states()
{
  module_state seed_module_state;
  bool seed_available = false;

  for(marker_state mr_s : this->reader.markers)
  {
    bool module_info_stored = false;
    // Get the module state of the detected marker
    module_state mo_s = this->get_module_state_from_marker_state(mr_s);
    // Check if a marker of this id is already registered
    for(int i = 0; i < this->module_states.size(); i++)
    {
      // If the module state for this id is already stored, just update the information
      if(this->module_states[i].id == mr_s.id)
      {
        // Update the stored marker position
        this->module_states[i].position[0] = mo_s.position[0];  
        this->module_states[i].position[1] = mo_s.position[1];  
        module_info_stored = true;
        break;
      }
    }
    // If not registered, add it to the stored module list
    if(!module_info_stored)
    {
      this->module_states.push_back(mo_s);
    }
    if(mo_s.id == SEED_ID)
    {
      seed_module_state = mo_s;
      seed_available = true;
    }
  }


  if(!seed_available) // If seed not found in the current frame, use the latest available seed state
  {
    for(module_state m : this->module_states)
    {
      if(m.id == SEED_ID)
      {
        seed_module_state = m;
        seed_available = true;
      }
    }
  }
 // If there is neither a seed module visible in this frame nor is there a latest seed state available, end the evaluation
 
  if(!seed_available)
    return;
 ///////// End getting seed position
 
  // If there is a seed state to work with, update the module states for each of the available markers
  for(int i = 0; i < this->module_states.size(); i++)
  {
    float distance_from_seed = sqrt(pow((this->module_states[i].position[0] - seed_module_state.position[0]),2) + pow((this->module_states[i].position[1] - seed_module_state.position[1]),2));
    if(distance_from_seed < this->high_fric_dist_thresh_pixels)
    {
      this->module_states[i].high_friction = true;
    }
    if(distance_from_seed > this->low_fric_dist_thresh_pixels)
    {
      this->module_states[i].high_friction = false;
    }
  }
}

void CentralController::store_module_states()
{
  cv::VideoCapture cap(-1);
  while(this->update_state_flag)
  {
      cv::Mat frame;
      // Capture frame-by-frames
      cap >> frame;

      // If the frame is empty, break immediately
      if (frame.empty())
      {
          continue;
          std::cout << "Frame empty \n" << std::endl;
      }

      this->reader.detect_markers(frame);
      // Use pixel to mm conversion factor to get distance thresholds in pixels
      this->high_fric_dist_thresh_pixels = this->reader.current_pixels_per_mm * HIGH_FRICTION_THRESHOLD_DISTANCE;
      this->low_fric_dist_thresh_pixels = this->reader.current_pixels_per_mm * LOW_FRICTION_THRESHOLD_DISTANCE;

      //std::cout << reader.markers.size() << " markers detected in this frame" << std::endl;
      // Use the states gotten in this frame to get the distance from the seed 
      // Store the resulting required module state (high-friction/low-friction mode)
      this->evaluate_module_states();
      
      // Overlay the markers with the appropriate colors to show module type

    
      for(module_state m : this->module_states)
      {
        if(m.id == SEED_ID)
        {
          // Circle to show the range for high friction modules
          try
          {
            cv::circle(frame, cv::Point((int)m.position[0], (int)m.position[1]), 10, cv::Scalar(0,0,255), -1, cv::FILLED,0);
            cv::circle(frame, cv::Point((int)m.position[0], (int)m.position[1]), this->high_fric_dist_thresh_pixels, cv::Scalar(0,0,255), 4, cv::FILLED,0);
            cv::circle(frame, cv::Point((int)m.position[0], (int)m.position[1]), this->low_fric_dist_thresh_pixels, cv::Scalar(0,255,0), 4, cv::FILLED,0);
          }
          catch(cv::Exception e)
          {
            std::cout << "Could not show the circle \n";
          }
          
        }
        
        else
        {
          cv::Scalar col;
          if(m.high_friction)
            col = cv::Scalar(0,0,255);
          else
            col = cv::Scalar(0,255,0);

          cv::circle(frame, cv::Point((int)m.position[0], (int)m.position[1]), 10, col, -1, cv::FILLED,0);
        }

      }
      std::string s = "Pixels per mm = " + std::to_string(reader.current_pixels_per_mm);
      cv::putText(frame, s, cv::Point(10, frame.size().height-100), 
                  cv::FONT_HERSHEY_COMPLEX_SMALL, 0.8, cvScalar(200,200,250), 1, CV_AA);
      // Display the resulting frame
      cv::imshow("Frame", frame );

      // Press  ESC on keyboard to exit
      char c=(char)cv::waitKey(25);
      if(c==27)
          break;
  }
}

std::string get_char_array_as_string(char array[], int size)
{
  std::string s;
  for(int i=0; i < size; i++)
  {
    if(array[i] != '\0')
    {
      s += array[i];
    }
    else 
      break;
  }
  return s;
}

std::string get_server_response(module_state& state)
{
  // Set the appropriate response message here
  // As of now, the message is "high_friction" if the module should be high_friction and "low_friction" if the module shoule be low friction
  std::string default_string = "low_friction";
  if(state.high_friction)
    return "high_friction";
  return default_string;
}
void fill_with_EOL(char array[], int size)
{
  for(int i =0; i<size; i++)
  {
    array[i] = '\0';
  }
}
int main()
{
  std::cout << "Reading aruco markers" << std::endl;
  CentralController c;
  
  // Create socket server
  int server_socket;
  server_socket = socket(AF_INET, SOCK_STREAM, 0);
  struct sockaddr_in server_addr;
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(9002);
  // The address of the server address. This will change for my application
  server_addr.sin_addr.s_addr = INADDR_ANY;
  // Bind the socket to the specified ip and port
  bind(server_socket, (struct sockaddr*) &server_addr, sizeof(server_addr));

  // Accept client connections while running
  while (true)
  {
    listen(server_socket, 50);

    int client_socket;
    // Accept a connection and get a socket handle (somehow an int)
    // The params currently set as NULL can be used to determine the ip address of the client
    // Not sure how this can be done, but not needed
    client_socket = accept(server_socket, NULL, NULL);
    char client_request[256];
    recv(client_socket, &client_request,sizeof(client_request), 0);
    // Get client request as string. This request will always be a module number 
    std::string client_request_str = get_char_array_as_string(client_request, 256);
    
    int module_id = stoi(client_request_str);
    std::cout << "client_request is : " << module_id << "\n";

    // Get the response message appropriate for this request string
    module_state mo_s;
    mo_s.high_friction = false;
    c.get_module_state_from_id(mo_s, module_id);
    std::string server_response = get_server_response(mo_s);

    // Send the server_message
    char server_message[256];
    fill_with_EOL(server_message, sizeof(server_message));
    for(int i = 0; i < server_response.length(); i++)
    {
      server_message[i] = server_response[i];
    }

    send(client_socket, server_message, sizeof(server_message), 0);
    // close(client_socket);
  }

  return 0;
}