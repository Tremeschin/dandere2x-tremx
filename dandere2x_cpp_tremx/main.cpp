/*/
 *
 *
 * DISCLAIMER
 *
 * Tremx is new to CPP so there might be quite some weird things going on here
 *
 *
 * NEED HEAVY HEAVY REFACTORING
 * NEED HEAVY HEAVY CLEANUP
 *
 *
/*/



#include <opencv2/opencv.hpp>

#include <algorithm>
#include <iostream>
#include <string>
#include <fstream>

#include <cstdlib>
#include <cmath>
#include <math.h>

#include "constants.h"




#define ONLY_FIRST_FRAME 0

#define DEBUG_SAVE_BLOCKS 0
#define DEBUG_SAVE_FRAMES 0
#define WRITE_DEBUG_FRAMES_VIDEO 1

#define SHOW_MAIN_OPTIONS 0

#define VERBOSE_DEBUG 0
#define SHOW_STATS 0


#define METHOD_USE_MSSIM 0
#define METHOD_USE_MSE 1







cv::Mat createOne(std::vector<cv::Mat> & images, int cols, int min_gap_size)
{
    // let's first find out the maximum dimensions
    int max_width = 0;
    int max_height = 0;
    for ( int i = 0; i < images.size(); i++) {
        // check if type is correct
        // you could actually remove that check and convert the image
        // in question to a specific type
        if ( i > 0 && images[i].type() != images[i-1].type() ) {
            std::cerr << "WARNING:createOne failed, different types of images";
            return cv::Mat();
        }
        max_height = std::max(max_height, images[i].rows);
        max_width = std::max(max_width, images[i].cols);
    }
    // number of images in y direction
    int rows = std::ceil(images.size() / cols);

    // create our result-matrix
    cv::Mat result = cv::Mat::zeros(rows*max_height + (rows-1)*min_gap_size,
                                    cols*max_width + (cols-1)*min_gap_size, images[0].type());
    size_t i = 0;
    int current_height = 0;
    int current_width = 0;
    for ( int y = 0; y < rows; y++ ) {
        for ( int x = 0; x < cols; x++ ) {
            if ( i >= images.size() ) // shouldn't happen, but let's be safe
                return result;
            // get the ROI in our result-image
            cv::Mat to(result,
                       cv::Range(current_height, current_height + images[i].rows),
                       cv::Range(current_width, current_width + images[i].cols));
            // copy the current image to the ROI
            images[i++].copyTo(to);
            current_width += max_width + min_gap_size;
        }
        // next line - reset width and update height
        current_width = 0;
        current_height += max_height + min_gap_size;
    }
    return result;
}






namespace residual_functions {

    namespace best_fit {
        std::vector<int> best_grid_fit(const int N) {

            // The size variables
            int a, b;

            long double root_n = std::sqrt(N);

            if ( std::pow( static_cast<int>(root_n), 2) == N) {
                // The number is a perfect square (because int(root_n)**2 is N itself)
                a = root_n;
                b = root_n;

            } else {
                // The number is not a perfect square, calculate the next perfect square
                // We do this by the following: get the lowest near int of its root,
                // add one and then square it so for example, N is 2:
                // floor(1.41) = 1 --> 1 + 1 --> 2 -> 2^2 -> 4
                // But we actually want to get the square (a, b) length so we don't square it
                int best_square_side = std::floor(root_n) + 1;

                a = best_square_side;
                b = best_square_side;

                b -= ((a*b)-N)/b;
            }

            return std::vector<int> {a, b};
        }


        std::vector<int> square_fit(const int N) {

            // The size variables
            int a, b;

            long double root_n = std::sqrt(N);

            if ( std::pow( static_cast<int>(root_n), 2) == 0) {
                // The number is a perfect square (because int(root_n)**2 is N itself)
                a = root_n;
                b = root_n;

            } else {
                // The number is not a perfect square, calculate the next perfect square
                // We do this by the following: get the lowest near int of its root,
                // add one and then square it so for example, N is 2:
                // floor(1.41) = 1 --> 1 + 1 --> 2 -> 2^2 -> 4
                // But we actually want to get the square (a, b) length so we don't square it
                int best_square_side = std::floor(root_n) + 1;

                a = best_square_side;
                b = best_square_side;
            }

            return std::vector<int> {a, b};
        }
    }



    namespace make_residual {

        cv::Mat from_block_vectors(std::vector<cv::Mat> matlist, const int block_size, const int bleed) {

            // Get the block number
            int n_blocks = matlist.size();

            // Get the best fit dimentions, see residual_functions::best_fit for the functions
            std::vector<int> dimentions = residual_functions::best_fit::best_grid_fit(n_blocks);

            // Calculate the cv::Mat dimentions with bleed added for Width and Height
            // Bleed is applied between blocks and on the image borders

            //std::cout << "best fit dimentions: " << dimentions[0] << ", " << dimentions[1] << " with size: " << n_blocks << std::endl;

            int residual_width  = bleed + ( (bleed + block_size)*dimentions[0] );
            int residual_height = bleed + ( (bleed + block_size)*dimentions[1] );

            //std::cout << "residual size pixels: " << residual_width << ", " << residual_height << std::endl;

            cv::Mat residual(residual_height, residual_width, CV_8UC3, cv::Scalar(0, 0, 0));

            //for(std::size_t i=0; i < matlist.size(); ++i) {
            //    std::cout << matlist[i] << std::endl;
            //}

            cv::Mat current_block;
            int count = 0;

            for(int y=0; y < dimentions[1]; y++) {
                for(int x=0; x < dimentions[0]; x++) {

                    //std::cout << y << " - " << x << std::endl;

                    // If out of bounds, exit this loop
                    if (count >= n_blocks) {
                        goto exit_iteration;
                    }

                    current_block = matlist[count];

                    current_block.copyTo(
                        residual(
                            cv::Rect(
                                bleed + (bleed + block_size)*x,
                                bleed + (bleed + block_size)*y,
                                current_block.cols,
                                current_block.rows
                            )
                        )
                    );


                    count++;
                }
            }

exit_iteration:

            return residual;
        }
    }
}










//http://jepsonsblog.blogspot.com/2012/10/overlay-transparent-image-in-opencv.html
void overlayImage(const cv::Mat &background, const cv::Mat &foreground,
  cv::Mat &output, cv::Point2i location)
{
    background.copyTo(output);


    // start at the row indicated by location, or at row 0 if location.y is negative.
    for(int y = std::max(location.y , 0); y < background.rows; ++y)
    {
        int fY = y - location.y; // because of the translation

        // we are done of we have processed all rows of the foreground image.
        if(fY >= foreground.rows)
        break;

        // start at the column indicated by location,

        // or at column 0 if location.x is negative.
        for(int x = std::max(location.x, 0); x < background.cols; ++x)
        {
        int fX = x - location.x; // because of the translation.

        // we are done with this row if the column is outside of the foreground image.
        if(fX >= foreground.cols)
            break;

        // determine the opacity of the foregrond pixel, using its fourth (alpha) channel.
        double opacity =
            ((double)foreground.data[fY * foreground.step + fX * foreground.channels() + 3])

            / 255.;


        // and now combine the background and foreground pixel, using the opacity,

        // but only if opacity > 0.
        for(int c = 0; opacity > 0 && c < output.channels(); ++c)
        {
            unsigned char foregroundPx =
            foreground.data[fY * foreground.step + fX * foreground.channels() + c];
            unsigned char backgroundPx =
            background.data[y * background.step + x * background.channels() + c];
            output.data[y*output.step + output.channels()*x + c] =
            backgroundPx * (1.-opacity) + foregroundPx * opacity;
        }
        }
    }
}



// NOT USED, HERE FOR REFERENCE

double calculate_psnr(const cv::Mat& I1, const cv::Mat& I2)
{
    cv::Mat s1;
    absdiff(I1, I2, s1);       // |I1 - I2|
    s1.convertTo(s1, CV_32F);  // cannot make a square on 8 bits
    s1 = s1.mul(s1);           // |I1 - I2|^2

    cv::Scalar s = sum(s1);         // sum elements per channel

    double sse = s.val[0] + s.val[1] + s.val[2]; // sum channels

    if( sse <= 1e-10) // for small values return zero
        return 0;
    else
    {
        double mse = sse /(double)(I1.channels() * I1.total());
        double psnr = 10.0*log10((255*255)/mse);
        return psnr;
    }
}










// NOT USED DEFAULT, HERE FOR REFERENCE

cv::Scalar calculate_mssim( const cv::Mat& i1, const cv::Mat& i2)
{
    const double C1 = 6.5025, C2 = 58.5225;
    /***************************** INITS **********************************/
    int d     = CV_32F;

    cv::Mat I1, I2;
    i1.convertTo(I1, d);           // cannot calculate on one byte large values
    i2.convertTo(I2, d);

    cv::Mat I2_2   = I2.mul(I2);        // I2^2
    cv::Mat I1_2   = I1.mul(I1);        // I1^2
    cv::Mat I1_I2  = I1.mul(I2);        // I1 * I2

    /***********************PRELIMINARY COMPUTING ******************************/

    cv::Mat mu1, mu2;   //
    GaussianBlur(I1, mu1, cv::Size(11, 11), 1.5);
    GaussianBlur(I2, mu2, cv::Size(11, 11), 1.5);

    cv::Mat mu1_2   =   mu1.mul(mu1);
    cv::Mat mu2_2   =   mu2.mul(mu2);
    cv::Mat mu1_mu2 =   mu1.mul(mu2);

    cv::Mat sigma1_2, sigma2_2, sigma12;

    GaussianBlur(I1_2, sigma1_2, cv::Size(11, 11), 1.5);
    sigma1_2 -= mu1_2;

    GaussianBlur(I2_2, sigma2_2, cv::Size(11, 11), 1.5);
    sigma2_2 -= mu2_2;

    GaussianBlur(I1_I2, sigma12, cv::Size(11, 11), 1.5);
    sigma12 -= mu1_mu2;

    ///////////////////////////////// FORMULA ////////////////////////////////
    cv::Mat t1, t2, t3;

    t1 = 2 * mu1_mu2 + C1;
    t2 = 2 * sigma12 + C2;
    t3 = t1.mul(t2);              // t3 = ((2*mu1_mu2 + C1).*(2*sigma12 + C2))

    t1 = mu1_2 + mu2_2 + C1;
    t2 = sigma1_2 + sigma2_2 + C2;
    t1 = t1.mul(t2);               // t1 =((mu1_2 + mu2_2 + C1).*(sigma1_2 + sigma2_2 + C2))

    cv::Mat ssim_map;
    cv::divide(t3, t1, ssim_map);      // ssim_map =  t3./t1;

    cv::Scalar mssim = mean( ssim_map ); // mssim = average of ssim map
    return mssim;
}







// NOT USED, HERE FOR REFERENCE

// SSIM returns [0.815287, 0.785487, 0.776612, 0] for example so we gotta "average" the channels
double fit_ssim(const double red, const double green, const double blue, double alpha) {

    // We discart alpha as it's a video..

#if 1

    // Simple average
    return (red + green + blue)/3;

#endif

}











double calculate_mse(cv::Mat I1, cv::Mat I2)
{
    cv::Mat s1;

    //cv::Mat t1(5, 5, CV_8UC3, cv::Scalar(255, 200, 0));
    //cv::Mat t2(5, 5, CV_8UC3, cv::Scalar(4, 4, 4));

    //t1.convertTo(t1, CV_32S);
    //t2.convertTo(t2, CV_32S);

    I1.convertTo(I1, CV_32S);
    I2.convertTo(I2, CV_32S);

    //cv::Mat addition;

    //cv::add(t1, t2, addition);

    //std::cout << "\n " << addition << std::endl;

    //std::exit(0);

    //cv::cvtColor(I1, I1, cv::COLOR_RGBA2RGB);
    //cv::cvtColor(I2, I2, cv::COLOR_RGBA2RGB);


    // cv::Mat t(5, 5, CV_8UC3, cv::Scalar(0, 0, 0));

    cv::absdiff(I1, I2, s1);       // |I1 - I2|

#if VERBOSE_DEBUG

    std::cout << "\nI1\n" << I1 << std::endl;
    std::cout << "\nI2\n" << I2 << std::endl;

    std::cout << "\ns1 absdif\n" << s1 << std::endl;

#endif




    s1.convertTo(s1, CV_32S);  // cannot make a square on 8 bits

    //std::cout << "\ns1 conv\n" << s1 << std::endl;

    s1 = s1.mul(s1);           // |I1 - I2|^2


#if VERBOSE_DEBUG
    std::cout << "\ns1 mult\n" << s1 << std::endl;
#endif


    cv::Scalar s = sum(s1);        // sum elements per channel

    double sse = s.val[0] + s.val[1] + s.val[2]; // sum channels

    double mse  = sse / (double)(I1.channels() * I1.total());


#if VERBOSE_DEBUG
    std::cout << "\nsse: " << sse << " , " << (double)(I1.channels() * I1.total()) << ", sum: " << s << ", mse: " << mse << std::endl;


#endif
    //std::exit(0);

    return mse;
 }












int process_video(const std::string video_path, const int block_size,
                  const int width, const int height, const std::string output_d2x_file,
                  const std::string output_vectors_path, const int start_frame,
                  const int bleed, const std::string residuals_output) {


    std::string debug_prefix = "[main.cpp/process_video] ";



    // // Set up output file.d2x

    std::ofstream output_file;


    // Open file in append mode
    //output_file.open(output_d2x_file, std::ios_base::app);

    // TODO:
    output_file.open(output_d2x_file);


    //output_file << "Writing this to a file.\n";



    // // Get iteration info on how much to break the video into blocks

    int width_iterations = std::ceil(static_cast<double>(width) / block_size);
    int height_iterations = std::ceil(static_cast<double>(height) / block_size);


    // Create variables for the crop positions of blocks
    int start_x;
    int start_y;

    int end_x;
    int end_y;

    int total_blocks;


#if METHOD_USE_MSSIM
    cv::Scalar block_msee_scalar;
#endif



    // Generate and write block vectors to file
    {

    #if VERBOSE_DEBUG
        std::cout << debug_prefix << "Generating vector files.. " << std::endl;
    #endif

        std::ofstream output_vectors_file;

        output_vectors_file.open(output_vectors_path);

        int vector_id = 0;


        // Begin slice image into blocks
        for (int x=0; x < width_iterations; x++) {

            start_x = (x * block_size);
            end_x = start_x + block_size;

            // If x it surpasses the width
            end_x = std::min(width, end_x);


            for (int y=0; y < height_iterations; y++) {

                start_y = (y * block_size);
                end_y = start_y + block_size;

                // If y it surpasses the height
                end_y = std::min(height, end_y);

                output_vectors_file << vector_id << ";(" << start_x << "," << start_y << "," << end_x << "," << end_y << ")\n";
                vector_id++;
            }
        }

    #if VERBOSE_DEBUG
        std::cout << debug_prefix << "Generated vector files" << std::endl;
    #endif
        total_blocks = vector_id;
        output_vectors_file.flush();
        output_vectors_file.close();
    };


    // // Set up video

    cv::VideoCapture video(video_path);

    // Check if video opened successfully
    if(!video.isOpened()){
        std::cout << "Error opening video stream or file" << '\n';
        return -1;
    }

    // Subtract 2 as it starts on zero and can't compare frame LAST with LAST+1
    int total_frame_count = video.get(CV_CAP_PROP_FRAME_COUNT) - 2;

#if VERBOSE_DEBUG
    std::cout << "Total frame count is: " << total_frame_count << std::endl;
#endif


    // Initialize as black image
    cv::Mat frame_a(height, width, CV_8UC3, cv::Scalar(0, 0, 0));
    cv::Mat frame_b;

    cv::Mat block_a;
    cv::Mat block_b;

    cv::Mat compressed_block;
    cv::Mat black_block;

    cv::Size resolution;

    cv::Mat compressed;
    cv::Mat not_compressed;
    cv::Mat debug_frame;

    // The matched blocks for generating the input residual
    std::vector<cv::Mat> matched_blocks;




#if WRITE_DEBUG_FRAMES_VIDEO

    std::string debug_video_filename = "debug_video_start_" + std::to_string(start_frame) + "_block_size_" + std::to_string(block_size) + ".mkv";
    cv::VideoWriter debug_video(debug_video_filename, CV_FOURCC('M','J','P','G'), 24, cv::Size(width, height));

#endif


    // // Frame relevant vars
    double frame_psnr;
    int count_frame = 0;
    int block_id;
    int remaining_frames;

    double raw_block_mse;
    double compressed_mse;


    // // Compression

    // buffer for compressing, 50 MB
    std::vector<uchar> buff(1024*1024*50);
    std::vector<int> param(2);

    param[0] = cv::IMWRITE_JPEG_QUALITY;
    param[1] = 80; //default(95) 0-100



    // If start frame is not zero, we get to the start frame by reading and dumping the frames
    if (start_frame > 0) {
        std::cout << "Seeking to " << start_frame - 1 << std::endl;

        video.set(CV_CAP_PROP_POS_FRAMES, start_frame - 1);
        video >> frame_a;

        count_frame = start_frame;

    #if ONLY_FIRST_FRAME
        cv::imwrite("frame_start.jpg", frame_a);

        cv::imencode(".jpg", frame_a, buff, param);

        compressed = cv::imdecode(buff, CV_LOAD_IMAGE_COLOR);

        cv::imwrite("frame_compressed.jpg", compressed);
    #endif

    }







    // T-flip-flop mechanism
    bool this_or_that = true;

    // Main routine
    while (true) {

        // Invert next iteration
        this_or_that = !this_or_that;

        // Get next frame with a T flip flop mechanism
        if (this_or_that) {
            video >> frame_a;
            compressed = frame_a.clone();

        #if WRITE_DEBUG_FRAMES_VIDEO
            debug_frame = frame_a.clone();
        #endif

            //compressed = frame_a;
            //debug_frame = frame_a;
            //std::cout << "frame a" << std::endl;
        } else {
            video >> frame_b;
            compressed = frame_b.clone();

        #if WRITE_DEBUG_FRAMES_VIDEO
            debug_frame = frame_b.clone();
        #endif

            //compressed = frame_b;
            //debug_frame = frame_b;
            //std::cout << "frame b" << std::endl;
        }


    #if DEBUG_SAVE_FRAMES
        std::string previous_fresh_filename = "freshframes/frame_" + std::to_string(count_frame) + "-1-previous_full.jpg";
        std::string next_fresh_filename =     "freshframes/frame_" + std::to_string(count_frame) + "-2-next_full.jpg";

        cv::imwrite(previous_fresh_filename, frame_a);
        cv::imwrite(next_fresh_filename, frame_b);
    #endif





    #if ONLY_FIRST_FRAME
        cv::imwrite("frame_a.jpg", frame_a);
        cv::imwrite("frame_b.jpg", frame_b);
    #endif


        // Exit as frame_a or frame_b is empty and can't compare
        if ( frame_b.empty() || frame_a.empty()) {
            std::cout << debug_prefix << "Some frame is empty, exiting.." << std::endl;
            output_file.close();
            return 0;
        }



        // // Compress the frame

        // Encode into a buffer
        cv::imencode(".jpg", compressed, buff, param);

        // Decode the compressed block
        compressed = cv::imdecode(buff, CV_LOAD_IMAGE_COLOR);



        output_file << "pframe;" << count_frame << "-";

        remaining_frames = total_frame_count - count_frame;

    #if SHOW_STATS
        std::cout << "[" << count_frame << "/" << total_frame_count << "] [" << remaining_frames << "]" << std::endl;;
    #endif


        // Current block_id, matches the vectors
        block_id = 0;


        // Begin slice image into blocks
        for (int x=0; x < width_iterations; x++) {

            start_x = (x * block_size);

            // If x it surpasses the width
            end_x = std::min(width, start_x + block_size);



            for (int y=0; y < height_iterations; y++) {

                start_y = (y * block_size);

                // If y it surpasses the height
                end_y = std::min(height, start_y + block_size);



                // The resolution of our block
                resolution = cv::Size(end_x - start_x, end_y - start_y);


                // Region of Interest to crop the block
                cv::Rect crop = cv::Rect(start_x, start_y, (end_x - start_x), (end_y - start_y));


                block_a = cv::Mat(frame_a, crop);
                block_b = cv::Mat(frame_b, crop);

                compressed_block = cv::Mat(compressed, crop);






            #if METHOD_USE_MSSIM

                block_msee_scalar = calculate_mssim(block_a, block_b);

                raw_block_mse = fit_ssim(block_msee_scalar[0], block_msee_scalar[1], block_msee_scalar[2], block_msee_scalar[3]);

                if (true) {
                    output_file << ";" << block_id;
                }

            #endif



            #if METHOD_USE_MSE

                // Raw MSE between two blocks
                raw_block_mse = calculate_mse(block_a, block_b);


                // Calculate the MSE of compressed
                if (this_or_that) {
                    compressed_mse = calculate_mse(compressed_block, block_a);

                        #if VERBOSE_DEBUG
                            std::cout << "frame:[" << count_frame << "]-block_id:[" << block_id << "]-compressed_mse_a:[" << compressed_mse << "]-raw:[" << raw_block_mse << "],";
                        #endif

                } else {
                    compressed_mse = calculate_mse(compressed_block, block_b);

                        #if VERBOSE_DEBUG
                            std::cout << "frame:[" << count_frame << "]-block_id:[" << block_id << "]-compressed_mse_b:[" << compressed_mse << "]-raw:[" << raw_block_mse << "]-status:[";
                        #endif

                }


            #if VERBOSE_DEBUG
                std::cout << "frame: " << count_frame << ", block_id: " << block_id << std::endl;
                std::cout << "Compressed block mse: " << compressed_mse << " - Raw mse: " << raw_block_mse << std::endl;
            #endif


                //cv::imwrite("block_a_mse.jpg", block_a);
                //cv::imwrite("block_b_mse.jpg", block_b);
                //cv::imwrite("block_compressed.jpg", compressed_block);



            #if WRITE_COMPRESSED

                cv::imwrite("frame_compressed.jpg", compressed);

                cv::imwrite("compressed_block.jpg", compressed_block);

                return 0;

            #endif


                // Validate
                if (raw_block_mse > compressed_mse) {

                #if VERBOSE_DEBUG
                    std::cout << "accepted]" << std::endl;
                #endif

                    output_file << ";" << block_id; // << "," << raw_block_mse;

                    if (this_or_that) {
                        matched_blocks.push_back(block_a);
                    } else {
                        matched_blocks.push_back(block_b);
                    }

                    //std::cout << raw_block_mse << " > " << compressed_mse << " - " << matched_blocks.size() << std::endl;



                #if WRITE_DEBUG_FRAMES_VIDEO
                    //black_block.copyTo(debug_frame(cv::Rect(start_x, start_y, black_block.cols, black_block.rows)));

                    black_block = cv::Mat(resolution, CV_8UC4, cv::Scalar(0, 0, 0, 140));
                    overlayImage(debug_frame, black_block, debug_frame, cv::Point(start_x, start_y));
                #endif


                } else {

                #if VERBOSE_DEBUG
                    std::cout << "denied]" << std::endl;
                #endif
                }



            #endif


            #if DEBUG_SAVE_BLOCKS

                std::string savename = "blocks/block_frame_" + std::to_string(count_frame) + "_" + std::to_string(start_x) + "_" + std::to_string(start_y) + "-" + std::to_string(end_x) + "_" + std::to_string(end_y) + "-";

                std::string block_a_savepath = savename + "a-raw:" + std::to_string(raw_block_mse) + "_compressed-"  + std::to_string(compressed_mse) + ".jpg";
                std::string block_b_savepath = savename + "b.raw:" + std::to_string(raw_block_mse) + "_compressed-"  + std::to_string(compressed_mse) + ".jpg";;

                cv::imwrite(block_a_savepath, block_a);
                cv::imwrite(block_b_savepath, block_b);

            #endif


            #if VERBOSE_DEBUG
                std::cout << "Frame: " << count_frame
                          << " // "
                          << x << "-" << y << " // "
                          << "startx: " << start_x << " endx: " << end_x
                          << " // "
                          << "starty: " << start_y << " endy: " << end_y
                          << " // "
                          << "diff: " << raw_block_mse
                          << std::endl;
            #endif

                block_id++;

            #if VERBOSE_DEBUG
                std::cout << "\n\n#################\n\n" << std::endl;
            #endif

            }


        }

        // Press  ESC on keyboard to exit
        char c=(char)cv::waitKey(25);
        if(c==27)
            break;
        //cv::imshow( "Frame", debug_frame );

    #if WRITE_DEBUG_FRAMES_VIDEO
        debug_video.write(debug_frame);
    #endif

        output_file << '\n';

        output_file.flush();


        // // Make the input residual image



        int grid_colums = static_cast<int>( std::sqrt( matched_blocks.size() ));

        //std::cout << matched_blocks.size() << ", " << grid_colums << std::endl;


        if (matched_blocks.size() > 0) {

            cv::Mat residual = residual_functions::make_residual::from_block_vectors(matched_blocks, block_size, bleed);

            //cv::Mat residual = createOne(matched_blocks, grid_colums, 2);

            std::string residual_name = residuals_output + "residual_" + std::string(8 - std::to_string(count_frame).length(), '0') + std::to_string(count_frame) + ".jpg";

            cv::imwrite(residual_name, residual);

        }


        for (cv::Mat item : matched_blocks)
        {
            item.release();
        }

        matched_blocks.clear();

        // //



    #if DEBUG_SAVE_FRAMES
        std::string previous_filename = "frames/frame_" + std::to_string(count_frame) + "-1-previous_full.jpg";
        std::string next_filename =     "frames/frame_" + std::to_string(count_frame) + "-2-next_full.jpg";

        cv::imwrite(previous_filename, frame_a);
        cv::imwrite(next_filename, frame_b);
    #endif

        count_frame++;


    #if ONLY_FIRST_FRAME
        return 0; std::endl;
    #endif

    }

    output_file.close();
}






int main(int argc, char** argv) {


    /*
    std::vector<cv::Mat> ints;

    cv::Mat frame_a(10, 10, CV_8UC3, cv::Scalar(0, 255, 0));
    cv::Mat frame_b(20, 15, CV_8UC3, cv::Scalar(0, 0, 255));

    ints.push_back(frame_a);
    ints.push_back(frame_b);

    for(std::size_t i=0; i < ints.size(); ++i) {
      std::cout << ints[i] << std::endl;
    }

    return 0;

    */





    std::string debug_prefix = "[main.cpp/main] ";


    // Failsafe number of arguments

    const int expected_args = 10;


#if SHOW_MAIN_OPTIONS
    std::cout << debug_prefix << "You have entered the following arguments:" << "\n\n";

    for (int i = 0; i < argc; ++i) {
        std::cout << debug_prefix << "Argv [" << i << "]: " << argv[i] << '\n' ;
    }
#endif

    if (argc != expected_args) {
        std::cout << expected_args << " arguments expected, read " << argc << '\n';
        return -1;
    }




    /* The argument orders must be:
     *
     * - video path
     * - block_size
     * - width
     * - height
     * - output file.d2x
     * - output block_id and vectors
     * - start_frame
     * - bleed
     * - residuals_output
     */


    std::string video_path = argv[1];

    int block_size = atoi(argv[2]);
    int width = atoi(argv[3]);
    int height = atoi(argv[4]);

    std::string output_d2x_file = argv[5];
    std::string output_vectors_path = argv[6];

    int start_frame = atoi(argv[7]);
    int bleed = atoi(argv[8]);

    std::string residuals_output = argv[9];

#if SHOW_MAIN_OPTIONS
    // Show the info
    {
        std::cout << '\n' << debug_prefix << "The loaded input values are:" << '\n';
        std::cout << debug_prefix << "video_path: \"" << video_path << "\"\n";
        std::cout << debug_prefix << "block_size: " << block_size << '\n';
        std::cout << debug_prefix << "width: " << width << '\n';
        std::cout << debug_prefix << "height: " << height << '\n';
        std::cout << debug_prefix << "video_path: \"" << output_vectors_path << "\"\n";
        std::cout << debug_prefix << "start_frame: " << start_frame << '\n';
        std::cout << debug_prefix << "bleed: " << bleed << '\n';
        std::cout << debug_prefix << "residuals_output: " << residuals_output << '\n';
        std::cout << '\n' << debug_prefix << "Any zero value on int is invalid, cheking.. ";
    };



    // Check for invalid passed values
    if (block_size == 0) {
        std::cout << debug_prefix << "Failed [block_size]" << '\n';
        return -1;
    }

    if (width == 0) {
        std::cout << debug_prefix << "Failed [width]" << '\n';
        return -1;
    }

    if (height == 0) {
        std::cout << debug_prefix << "Failed [height]" << '\n';
        return -1;
    }

    std::cout << "Pass\n";
#endif

    process_video(video_path, block_size, width, height, output_d2x_file, output_vectors_path, start_frame, bleed, residuals_output);

    return 0;
}
