#include <opencv2/highgui.hpp>
#include <opencv2/aruco.hpp>
#include<string>
#include<iostream>
using namespace cv;

namespace {
const char* about = "Create an ArUco marker image";
const char* keys  =
        "{m       |       | Marker id in the dictionary }";
        // "{@outfile |<none> | Output image }"
        // "{d        |       | dictionary: DICT_4X4_50=0, DICT_4X4_100=1, DICT_4X4_250=2,"
        // "DICT_4X4_1000=3, DICT_5X5_50=4, DICT_5X5_100=5, DICT_5X5_250=6, DICT_5X5_1000=7, "
        // "DICT_6X6_50=8, DICT_6X6_100=9, DICT_6X6_250=10, DICT_6X6_1000=11, DICT_7X7_50=12,"
        // "DICT_7X7_100=13, DICT_7X7_250=14, DICT_7X7_1000=15, DICT_ARUCO_ORIGINAL = 16}"
        // "{ms       | 200   | Marker size in pixels }"
        // "{bb       | 1     | Number of bits in marker borders }"
        // "{si       | false | show generated image }";
}


int main(int argc, char *argv[]) {
    CommandLineParser parser(argc, argv, keys);
    parser.about(about);


    int markers = parser.get<int>("m");
    int dictionaryId = 0;
    int borderBits = 1;
    int markerSize = 300;
    bool showImage = false;
    // int dictionaryId = parser.get<int>("d");
    // int markerSize = parser.get<int>("ms");

    //String out = parser.get<String>(0);

    if(!parser.check()) {
        std::cout << "There was an error \n";
        parser.printErrors();
        return 0;
    }

    Ptr<aruco::Dictionary> dictionary =
        aruco::getPredefinedDictionary(aruco::PREDEFINED_DICTIONARY_NAME(dictionaryId));

    String out = "../aruco_codes/";
    for(int i = 1; i <= markers; i++)
    {
        Mat markerImg;
        aruco::drawMarker(dictionary, i, markerSize, markerImg, borderBits);

        if(showImage) {
            imshow("marker", markerImg);
            waitKey(0);
        }
        String output = out + std::to_string(i)+".jpg";
        imwrite(output, markerImg);
        std::cout << "Wrote  " << output << "\n";
    }

    return 0;
}