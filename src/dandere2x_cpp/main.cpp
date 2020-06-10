/*
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 3.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */


#include <opencv2/opencv.hpp>

#include <algorithm>
#include <iostream>
#include <string>
#include <fstream>

#include <cstdlib>
#include <cmath>
#include <math.h>
#include <chrono>
#include <thread>


// Namespace of utils we might end up needing to use
namespace utils {
    bool file_exists (const std::string& fname) {
        std::ifstream f(fname.c_str());
        return f.good();
    }

    double proportion(double a, double b, double c) {
        // ^ A is to B    ^
        // ^ C is to what ^
        // Left side go up / right side go up
        // C * B = A * what
        // what = B*C/A
        if (a == 0) { // This shouldn't happen but welp
            return 0;
        }
        return (b*c)/a;
    }

    double invproportion(double a, double b, double c) {
        // ^ A is to B    v
        // ^ C is to what v
        // Left side go up / right side go down
        // A * B = C * what
        // what = A*B/C
        if (c == 0) { // This shouldn't happen but welp
            return 0;
        }
        return (a*b)/c;
    }
}

// Where we make the residuals
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

            if (std::pow(static_cast<int>(root_n), 2) == 0) {
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

        cv::Mat from_block_vectors(std::vector<cv::Mat> matlist, const int block_size, const int bleed, cv::Scalar mean_color) {

            // Get the block number and the bleeded size
            int n_blocks = matlist.size();
            int bleeded_block_size = block_size + (2*bleed);

            // For cutting the black parts of the residual
            int max_x = 0;
            int max_y = 0;

            // Iteration of the block position on the residual
            int this_x_location = 0;
            int this_y_location = 0;
            int block_width = 0;
            int block_height = 0;

            // Get the best fit dimensions on a AxB grid according to the number of blocks
            std::vector<int> dimensions = residual_functions::best_fit::best_grid_fit(n_blocks);

            // Calculate the cv::Mat dimensions with bleed added for Width and Height
            // Bleed is a "overcrop", it's already applied on the matlist which are the blocks
            int residual_width  = bleeded_block_size * dimensions[0];
            int residual_height = bleeded_block_size * dimensions[1];

            // Create a blank frame for the residual
            cv::Mat residual(residual_height, residual_width, CV_8UC3, mean_color);

            // Crop related vars
            cv::Rect black_borders_crop;
            cv::Mat current_block;

            // Count the blocks for stopping the loop
            int count = 0;

            for(int y=0; y < dimensions[1]; y++) {
                for(int x=0; x < dimensions[0]; x++) {

                    // If out of bounds, exit this loop
                    if (count == n_blocks) {
                        goto exit_iteration;
                    }

                    // This block we're going to copy to
                    current_block = matlist[count];

                    // Where the X an Y start are
                    this_x_location = bleeded_block_size * x;
                    this_y_location = bleeded_block_size * y;

                    // DRY: resolution of the block
                    block_width = current_block.cols;
                    block_height = current_block.rows;

                    // Update the maximum coordinates we're copying blocks to
                    max_x = std::max(max_x, this_x_location + block_width);
                    max_y = std::max(max_y, this_y_location + block_height);

                    // Actually copy the block to the residual frame
                    current_block.copyTo(
                        residual(
                            cv::Rect(
                                this_x_location,
                                this_y_location,
                                block_width,
                                block_height
                            )
                        )
                    );

                    count++;
                }
            }

            // Region of Interest to crop only the parts we want
            black_borders_crop = cv::Rect(0, 0, max_x, max_y);

            // Crop the residual, remove parts we don't need
            residual = cv::Mat(residual, black_borders_crop);

exit_iteration:
            return residual;
        }
    }
}


// props to: http://jepsonsblog.blogspot.com/2012/10/overlay-transparent-image-in-opencv.html
void overlayImage(const cv::Mat &background, const cv::Mat &foreground, cv::Mat &output, cv::Point2i location) {

    background.copyTo(output);

    // start at the row indicated by location, or at row 0 if location.y is negative.
    for(int y = std::max(location.y , 0); y < background.rows; ++y) {
        int fY = y - location.y; // because of the translation

        // we are done of we have processed all rows of the foreground image.
        if(fY >= foreground.rows) break;

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

            // And now combine the background and foreground pixel, using the opacity,
            // But only if opacity > 0
            for(int c = 0; opacity > 0 && c < output.channels(); ++c) {
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


double calculate_mse(cv::Mat I1, cv::Mat I2)
{
    cv::Mat absdiff;

    // Convert to a number that can hold the squares
    I1.convertTo(I1, CV_32S);
    I2.convertTo(I2, CV_32S);

    // absolute_value(A - B)
    cv::absdiff(I1, I2, absdiff);

    // Convert to a number that can hold big values
    absdiff.convertTo(absdiff, CV_32S);

    // (A - B)^2
    absdiff = absdiff.mul(absdiff);

    // Sum elements per channel into their own channels
    cv::Scalar channels = sum(absdiff);

    // Sum all the channels
    double sse = channels.val[0] + channels.val[1] + channels.val[2];

    // Calculate the final mse
    double mse  = sse / (double)(I1.channels() * I1.total());

    return mse;
}

// C = (A*k + B*j) / (k + j), tries to avoid video compression
cv::Mat mean_image(cv::Mat I1, cv::Mat I2, const int proportion_a, const int proportion_b)
{
    cv::Mat A = I1.clone();
    cv::Mat B = I2.clone();

    A.convertTo(A, CV_32S);
    B.convertTo(B, CV_32S);

    cv::Mat mean = ((A*proportion_a) + (B*proportion_b))/(proportion_a + proportion_b);

    return mean;
}


// Main implementation of Dandere2x block matching
int process_video(const std::string video_path,
                  const int block_size,
                  const int width,
                  const int height,
                  const int start_frame,
                  const int bleed,
                  const std::string residuals_output,
                  const int mindisk,
                  const int zero_padding,
                  const int write_debug_video,
                  const std::string debug_video_output,
                  const double dark_mse_threshhold,
                  const double bright_mse_threshhold,
                  const int show_debug_video_realtime,
                  const int show_block_matching_stats,
                  const int only_run_dandere2x_cpp,
                  const double upscale_full_frame_threshold)
{

    std::string debug_prefix = "[main.cpp/process_video] ";

    // // Get iteration info on how much to break the video into blocks
    int width_iterations = std::ceil(static_cast<double>(width) / block_size);
    int height_iterations = std::ceil(static_cast<double>(height) / block_size);

    // Create variables for the crop positions of blocks
    int start_x = 0;
    int start_y = 0;

    int end_x = 0;
    int end_y = 0;

    int bleeded_start_x = 0;
    int bleeded_start_y = 0;

    int bleeded_end_x = 0;
    int bleeded_end_y = 0;

    int blocks_per_frame = 0;

    // Generate and write block vectors to file
    {
        int vector_id = 0;

        for (int y=0; y < height_iterations; y++) {

            start_y = (y * block_size);

            // If y it surpasses the height
            end_y = std::min(height, start_y + block_size);

            // Begin slice image into blocks
            for (int x=0; x < width_iterations; x++) {

                start_x = (x * block_size);
                end_x = std::min(width, start_x + block_size);

                std::cout << "|vector;" << vector_id << ";" << start_y << "," << start_x << "," << end_y << "," << end_x << std::endl;
                vector_id++;
            }
        }
        // Get the total blocks per frame based on how much vectors there is
        blocks_per_frame = vector_id;
    };

    // // Set up video
    std::cout << "video_path: " << video_path << std::endl;
    cv::VideoCapture video(video_path);

    // Check if video opened successfully
    if(video.isOpened() == false){
        std::cout << "Error opening video stream or file" << '\n';
        return -1;
    }

    // Subtract 2 as it starts on zero and can't compare frame LAST with LAST+1
    int total_frame_count = video.get(cv::CAP_PROP_FRAME_COUNT) - 2;

    // Initialize as black image
    cv::Mat frame(height, width, CV_8UC3, cv::Scalar(0, 0, 0));

    // Create all the cv::Mat in the world!!
    cv::Mat last_matched(height, width, CV_8UC3, cv::Scalar(0, 0, 0));
    cv::Mat bleeded_borders_frame(height + (2*bleed), width + (2*bleed), CV_8UC3, cv::Scalar(0, 0, 0));
    cv::Mat bleed_croppable_frame(height + bleed + block_size, width + bleed + block_size, CV_8UC3, cv::Scalar(0, 0, 0));
    cv::Mat noised_frame;
    cv::Mat debug_frame;
    cv::Mat block;
    cv::Mat last_matched_block;
    cv::Mat bleeded_block;
    cv::Mat noised_block;
    cv::Mat black_block;

    cv::Size resolution;
    
    cv::Scalar mean_color;

    // The matched blocks for generating the input residual
    std::vector<cv::Mat> matched_blocks;

    cv::VideoWriter debug_video;

    if (write_debug_video) {
        std::string debug_video_filename = debug_video_output;
        debug_video = cv::VideoWriter(debug_video_filename, cv::VideoWriter::fourcc('M','J','P','G'), 24, cv::Size(width, height));
    }

    // // Frame relevant vars
    int count_frame = 0;
    int block_id = 0;
    int remaining_frames = 0;

    // Division by zero if 0 on counting the blocks
    long int total_blocks = 1;
    long int dont_need_upscaling = 0;
    long int need_upscaling = 0;
    double this_frame_upscale_percentage = 0;
    double recycled_percentage = 0;

    double raw_block_mse = 0;

    double mean_pixels_value = 0;
    double mse_threshhold = 0;

    std::string next_output_newline;

    // If start frame is > 0, start with the last frame we were processing
    // ie. seek to video[start_frame]
    // And it's a good measure to start with a black last_matched
    // because we don't carry these errors over when resuming
    if (start_frame > 0) {
        std::cout << "Seeking to " << start_frame - 1 << std::endl;

        video.set(cv::CAP_PROP_POS_FRAMES, start_frame - 1);
        video >> frame;

        count_frame = start_frame;
    }

    // Main routine
    while (true) {

        // The string we're going to write the position of the block vectors we matched
        next_output_newline = "|blocks;" + std::to_string(count_frame) + ";";

        video >> frame;
        
        if (frame.empty()) {
            std::cout << debug_prefix << "Some frame is empty, exiting.." << std::endl;
            std::cout << "|end;" + std::to_string(count_frame) + ";" << std::endl;
            return 0;
        }  

        //std::cout << "mse_threshhold: " << mse_threshhold << " mean_pixels: " << mean_pixels_value << std::endl;

        // Instead of adding black border we set a background of the original frame resized to the
        // bleeded resolution plus block size and just overlay the original image so we avoid
        // black borders on right/bottom edge rectangular blocks
        cv::resize(frame, bleeded_borders_frame, cv::Size(width + (2*bleed), height + (2*bleed)));
        cv::resize(frame, bleed_croppable_frame, cv::Size(width + bleed + block_size, height + bleed + block_size));

        bleeded_borders_frame.copyTo(bleed_croppable_frame(cv::Rect(0, 0, bleeded_borders_frame.cols, bleeded_borders_frame.rows)));

        frame.copyTo(bleed_croppable_frame(cv::Rect(bleed, bleed, frame.cols, frame.rows)));

        if (write_debug_video || show_debug_video_realtime) {
            debug_frame = frame.clone();
        }

        remaining_frames = total_frame_count - count_frame;

        // Current block_id, matches the vectors
        block_id = 0;

        for (int y=0; y < height_iterations; y++) {

            start_y = (y * block_size);

            // If y it surpasses the height
            end_y = std::min(height, start_y + block_size);

            // Begin slice image into blocks
            for (int x=0; x < width_iterations; x++) {

                start_x = (x * block_size);

                // If x it surpasses the width
                end_x = std::min(width, start_x + block_size);

                // The resolution of our block
                resolution = cv::Size(end_x - start_x, end_y - start_y);

                // Region of Interest to crop the block
                cv::Rect crop = cv::Rect(start_x, start_y, (end_x - start_x), (end_y - start_y));

                // Calculate where both X and Y starts / ends on the bleeded crop
                bleeded_start_x = (x * block_size);
                bleeded_start_y = (y * block_size);

                // Generate the bleeded crop
                cv::Rect bleeded_crop = cv::Rect(
                    bleeded_start_x,
                    bleeded_start_y,
                    block_size + (2*bleed),
                    block_size + (2*bleed)
                );

                //std::cout << "bleeded_start_x: " << bleeded_start_x << ", bleeded_stary_y: " << bleeded_start_y
                //          << " bleeded_end_x: " << bleeded_end_x << ", bleeded_end_y: " << bleeded_end_y << std::endl;

                block = cv::Mat(frame, crop);
                last_matched_block = cv::Mat(last_matched, crop);

                // Raw MSE between two blocks
                raw_block_mse = calculate_mse(block, last_matched_block);
                raw_block_mse /= block.total();

                // The mean color of this frame will be the residual "blank" canvas to reduce black bleed
                // While the mean pixel values will determine the mse threshold based on dark/bright levels
                mean_color = cv::mean(last_matched_block);
                mean_pixels_value = (mean_color.val[0] + mean_color.val[1] + mean_color.val[2]) / 3;

                // f(x) = ax + b
                // x = 0, dark
                // x = 255, bright
                mse_threshhold = ((bright_mse_threshhold - dark_mse_threshhold)/255)*mean_pixels_value + dark_mse_threshhold;

                // The thresholds we pass to Dandere2x C++ are for a 20x20 block, so we have to apply an proportion
                mse_threshhold = utils::invproportion(400, mse_threshhold, block.total());
                
                total_blocks++;

                // Validate
                if (raw_block_mse > mse_threshhold) {

                    need_upscaling++;

                    // Copy the block into our last matched frame
                    block.copyTo(
                        last_matched(
                            crop
                        )
                    );

                    next_output_newline += "," + std::to_string(block_id);

                    // Create bleeded block and add it to the upscaling list
                    bleeded_block = cv::Mat(bleed_croppable_frame, bleeded_crop);
                    matched_blocks.push_back(bleeded_block);

                    //std::cout << raw_block_mse << " > " << compressed_mse << " - " << matched_blocks.size() << std::endl;

                    if (write_debug_video || show_debug_video_realtime) {
                        black_block = cv::Mat(resolution, CV_8UC4, cv::Scalar(255, 0, 0, 120));
                        overlayImage(debug_frame, black_block, debug_frame, cv::Point(start_x, start_y));
                    }

                } else {

                    // <++> EXPERIMENTAL
                    // Try to bypass some encoding compression / noises
                    mean_image(last_matched_block, block, 10, 1).copyTo(
                        last_matched(
                            crop
                        )
                    );

                    dont_need_upscaling++;
                }
                block_id++;
            }
        }

        if (write_debug_video) {
            debug_video.write(debug_frame);
        }

        if (show_debug_video_realtime) {
            // Press  ESC on keyboard to exit
            char c=(char)cv::waitKey(25);
            if(c==27)
                std::exit(0);
            cv::imshow("Frame", debug_frame);
        }

        // // Make the input residual image
        if ( !only_run_dandere2x_cpp ) {

            // Empty frame, copy previous one
            if (matched_blocks.size() == 0) {
                std::cout << "|empty;" + std::to_string(count_frame) << std::endl;

            } else {

                // Generate the paths we need
                int max_frames_ahead = 40;
                int max_frames_ahead_wait = count_frame - max_frames_ahead;

                std::string residual_name = residuals_output + "residual_" + std::string(zero_padding - std::to_string(count_frame).length(), '0') + std::to_string(count_frame) + ".jpg";
                std::string residual_name_mindisk = residuals_output + "residual_" + std::string(zero_padding - std::to_string(max_frames_ahead_wait).length(), '0') + std::to_string(max_frames_ahead_wait) + ".jpg";

                // If the percentage of blocks needing upscale compared to the total blocks is less than threshold, make residual
                // Otherwise the residual is the frame itself
                
                // Make an residual, we'll see its proportion based on the pixel count of it
                cv::Mat residual = residual_functions::make_residual::from_block_vectors(matched_blocks, block_size, bleed, mean_color);

                // Calculate the proportion of pixels that will be upscaled compared to the frame itself
                this_frame_upscale_percentage = utils::proportion(frame.total(), 100, residual.total());

                // Let the threshold be user selected for some interesting modes like a upscale all frames, no block matching mode
                if ( upscale_full_frame_threshold >= this_frame_upscale_percentage ) {

                    // Write the residual                
                    std::cout << next_output_newline << std::endl;
                    cv::imwrite(residual_name, residual);

                } else {

                    // The residual is the fullframe itself
                    std::cout << "|fullframe;" + std::to_string(count_frame) << std::endl;
                    cv::imwrite(residual_name, frame);

                    // The stats changes a bit as we upscale blocks we weren't going at first
                    int difference = blocks_per_frame - matched_blocks.size();
                    need_upscaling += difference;
                    dont_need_upscaling -= difference;
                }

                // Mindisk utility, wait for the file - max_frames_ahead to be deleted
                while (mindisk && utils::file_exists(residual_name_mindisk)) {
                    std::this_thread::sleep_for(std::chrono::milliseconds(50));
                }
            }
        }

        // Update our recycled stats
        recycled_percentage = static_cast<double>(100)*dont_need_upscaling / total_blocks;

        if (show_block_matching_stats) {
            std::cout << "Debug frame: [" << count_frame << "/" << total_frame_count << "]"
                      << ", (Need / Don't need) upscaling: [" << need_upscaling << "/" << dont_need_upscaling << "]"
                      << ", Total blocks: [" << total_blocks << "]" << ", Recylcled percentage: " << recycled_percentage << std::endl;
        }

        // Python get the status on recycled blocks
        std::cout << "|recycled;" << recycled_percentage << std::endl;

        // Empty the vector
        for (cv::Mat item : matched_blocks)
        {
            item.release();
        }
        matched_blocks.clear();

        // Next iteration
        count_frame++;
    }
}


int main(int argc, char** argv) {

    std::string debug_prefix = "[main.cpp/main] ";

    // Failsafe number of arguments
    const int expected_args = 18;

    std::cout << debug_prefix << "You have entered the following arguments:" << "\n\n";

    for (int i = 0; i < argc; ++i) {
        std::cout << debug_prefix << "Argv [" << i << "]: " << argv[i] << '\n' ;
    }

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
     * - start_frame
     * - bleed
     * - residuals_output
     * - mindisk mode on / off [1/0]
     * - zero padding (residuals files)
     * - write_debug_video
     * - debug_video_output
     * - dark mse threshold
     * - bright mse threshold
     * - show_debug_video_realtime
     * - show_block_matching_stats
     * - only_run_dandere2x_cpp
     * - upscale_full_frame_threshold
     */

    std::string video_path = argv[1];

    int block_size = atoi(argv[2]);
    int width = atoi(argv[3]);
    int height = atoi(argv[4]);

    int start_frame = atoi(argv[5]);
    int bleed = atoi(argv[6]);

    std::string residuals_output = argv[7];

    int mindisk = atoi(argv[8]);

    int zero_padding = atoi(argv[9]);
    int write_debug_video = atoi(argv[10]);

    std::string debug_video_output = argv[11];

    double dark_mse_threshhold = atof(argv[12]);
    double bright_mse_threshhold = atof(argv[13]);

    int show_debug_video_realtime = atoi(argv[14]);
    int show_block_matching_stats = atoi(argv[15]);

    int only_run_dandere2x_cpp = atoi(argv[16]);
    
    double upscale_full_frame_threshold = atof(argv[17]); 

    // Show the info
    {
        std::cout << '\n' << debug_prefix << "The loaded input values are:" << '\n';
        std::cout << debug_prefix << "video_path: \"" << video_path << "\"\n";
        std::cout << debug_prefix << "block_size: " << block_size << '\n';
        std::cout << debug_prefix << "width: " << width << '\n';
        std::cout << debug_prefix << "height: " << height << '\n';
        std::cout << debug_prefix << "start_frame: " << start_frame << '\n';
        std::cout << debug_prefix << "bleed: " << bleed << '\n';
        std::cout << debug_prefix << "residuals_output: " << residuals_output << '\n';
        std::cout << debug_prefix << "mindisk: " << mindisk << '\n';
        std::cout << debug_prefix << "zero_padding: " << zero_padding << '\n';
        std::cout << debug_prefix << "write_debug_video: " << write_debug_video << '\n';
        std::cout << debug_prefix << "debug_video_output: \"" << debug_video_output << "\"\n";
        std::cout << debug_prefix << "show_debug_video_realtime: \"" << show_debug_video_realtime << "\"\n";
        std::cout << debug_prefix << "show_block_matching_stats: \"" << show_block_matching_stats << "\"\n";
        std::cout << debug_prefix << "only_run_dandere2x_cpp: \"" << only_run_dandere2x_cpp << "\"\n";
        std::cout << debug_prefix << "upscale_full_frame_threshold: \"" << upscale_full_frame_threshold << "\"\n";
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


    process_video(
        video_path,
        block_size,
        width,
        height,
        start_frame,
        bleed,
        residuals_output,
        mindisk,
        zero_padding,
        write_debug_video,
        debug_video_output,
        dark_mse_threshhold,
        bright_mse_threshhold,
        show_debug_video_realtime,
        show_block_matching_stats,
        only_run_dandere2x_cpp,
        upscale_full_frame_threshold
    );

    return 0;
}
