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
#include <chrono>
#include <thread>





#define ONLY_FIRST_FRAME 0

#define DEBUG_SAVE_BLOCKS 0
#define DEBUG_SAVE_FRAMES 0

#define SHOW_MAIN_OPTIONS 0

#define VERBOSE_DEBUG 0
#define SHOW_STATS 0


#define METHOD_USE_MSSIM 0
#define METHOD_USE_MSE 1








namespace utils {
    bool file_exists (const std::string& fname) {
        std::ifstream f(fname.c_str());
        return f.good();
    }
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

        cv::Mat from_block_vectors(std::vector<cv::Mat> matlist, const int block_size, const int bleed) {

            // Get the block number
            int n_blocks = matlist.size();

            int bleeded_block_size = block_size + (2*bleed);

            // For cutting the black parts of the residual
            int max_x = 0;
            int max_y = 0;

            int this_x_location = 0;
            int this_y_location = 0;

            int block_rows = 0;
            int block_cols = 0;

            cv::Rect crop;

            // Get the best fit dimensions, see residual_functions::best_fit for the functions
            std::vector<int> dimensions = residual_functions::best_fit::best_grid_fit(n_blocks);

            // Calculate the cv::Mat dimensions with bleed added for Width and Height
            // Bleed is applied between blocks and on the image borders

            //std::cout << "best fit dimensions: " << dimensions[0] << ", " << dimensions[1] << " with size: " << n_blocks << std::endl;

            int residual_width  = bleeded_block_size * dimensions[0];
            int residual_height = bleeded_block_size * dimensions[1];

            //std::cout << "residual size pixels: " << residual_width << ", " << residual_height << std::endl;

            cv::Mat residual(residual_height, residual_width, CV_8UC3, cv::Scalar(0, 0, 0));

            //for(std::size_t i=0; i < matlist.size(); ++i) {
            //    std::cout << matlist[i] << std::endl;
            //}

            cv::Mat current_block;
            int count = 0;

            for(int y=0; y < dimensions[1]; y++) {
                for(int x=0; x < dimensions[0]; x++) {

                    //std::cout << y << " - " << x << std::endl;

                    // If out of bounds, exit this loop
                    if (count >= n_blocks) {
                        goto exit_iteration;
                    }

                    current_block = matlist[count];

                    this_x_location = bleeded_block_size * x;
                    this_y_location = bleeded_block_size * y;

                    block_cols = current_block.cols;
                    block_rows = current_block.rows;

                    max_x = std::max(max_x, this_x_location + block_cols);
                    max_y = std::max(max_y, this_y_location + block_rows);


                    //std::cout << "this x: " << this_x_location << " this y: " << this_y_location
                    //          << "cols: " << block_cols << " rows: " << block_rows << std::endl;


                    current_block.copyTo(
                        residual(
                            cv::Rect(
                                this_x_location,
                                this_y_location,
                                block_cols,
                                block_rows
                            )
                        )
                    );


                    count++;
                }
            }

            //max_x += bleed;
            //max_y += bleed;

            // Region of Interest to crop only the parts we want
            crop = cv::Rect(0, 0, max_x, max_y);

            residual = cv::Mat(residual, crop);

exit_iteration:
            return residual;
        }
    }
}










//http://jepsonsblog.blogspot.com/2012/10/overlay-transparent-image-in-opencv.html
void overlayImage(const cv::Mat &background, const cv::Mat &foreground, cv::Mat &output, cv::Point2i location)
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

    I1.convertTo(I1, CV_32S);
    I2.convertTo(I2, CV_32S);

    cv::absdiff(I1, I2, s1); // |I1 - I2|

    s1.convertTo(s1, CV_32S); // cannot make a square on 8 bits

    s1 = s1.mul(s1); // |I1 - I2|^2

    cv::Scalar s = sum(s1); // sum elements per channel

    double sse = s.val[0] + s.val[1] + s.val[2]; // sum channels

    double mse  = sse / (double)(I1.channels() * I1.total());

    return mse;
 }





int process_video(const std::string video_path,
                  const int block_size,
                  const int width,
                  const int height,
                  const std::string output_d2x_file,
                  const std::string output_vectors_path,
                  const int start_frame,
                  const int bleed,
                  const std::string residuals_output,
                  const bool mindisk,
                  const int zero_padding,
                  const bool write_only_debug_video,
                  const std::string debug_video_output)
{

    std::string debug_prefix = "[main.cpp/process_video] ";


    // // Set up output file.d2x
    std::ofstream output_file;

    // Open file in append mode
    output_file.open(output_d2x_file, std::ios_base::app);

    // Open file in overwrite mode
    // output_file.open(output_d2x_file);


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


        for (int y=0; y < height_iterations; y++) {

            start_y = (y * block_size)*2;
            end_y = start_y + (block_size*2);

            // If y it surpasses the height
            end_y = std::min((height*2), end_y);

            // Begin slice image into blocks
            for (int x=0; x < width_iterations; x++) {

                start_x = (x * block_size)*2;
                end_x = start_x + (block_size*2);

                // If x it surpasses the width
                end_x = std::min((width*2), end_x);


                output_vectors_file << vector_id << ";(" << start_y << "," << start_x << "," << end_y-1 << "," << end_x-1 << ")\n";
                vector_id++;
            }
        }

    #if VERBOSE_DEBUG
        std::cout << debug_prefix << "Generated vector files" << std::endl;
    #endif
        output_vectors_file << "END"; // signal python we ended
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
    int total_frame_count = video.get(cv::CAP_PROP_FRAME_COUNT) - 2;

#if VERBOSE_DEBUG
    std::cout << "Total frame count is: " << total_frame_count << std::endl;
#endif


    // Initialize as black image
    cv::Mat frame_a(height, width, CV_8UC3, cv::Scalar(0, 0, 0));
    cv::Mat frame_b;

    cv::Mat bleed_croppable_frame(height + (2*bleed), width + (2*bleed), CV_8UC3, cv::Scalar(0, 0, 0));

    cv::Mat noised_frame_a;
    cv::Mat noised_frame_b;

    cv::Mat block_a;
    cv::Mat block_b;

    cv::Mat bleeded_block_a;
    cv::Mat bleeded_block_b;

    cv::Mat noised_block_a;
    cv::Mat noised_block_b;

    cv::Mat compressed_block;
    cv::Mat black_block;

    cv::Size resolution;

    cv::Mat compressed;
    cv::Mat not_compressed;
    cv::Mat debug_frame;

    // The matched blocks for generating the input residual
    std::vector<cv::Mat> matched_blocks;



    cv::VideoWriter debug_video;

    if (write_only_debug_video) {

        std::string debug_video_filename = debug_video_output;
        debug_video = cv::VideoWriter(debug_video_filename, cv::VideoWriter::fourcc('M','J','P','G'), 24, cv::Size(width, height));

    }



    // // Frame relevant vars
    double frame_psnr = 0;
    int count_frame = 0;
    int block_id = 0;
    int remaining_frames = 0;

    // Division by zero if 0 on counting the blocks
    int total_blocks = 1;
    int dont_need_upscaling = 0;
    int need_upscaling = 0;

    double raw_block_mse = 0;
    double compressed_mse = 0;

    std::string next_output_newline;


    // // Compression

    // buffer for compressing, 50 MB
    std::vector<uchar> buff(1024*1024*50);
    std::vector<int> param(2);

    param[0] = cv::IMWRITE_JPEG_QUALITY;
    param[1] = 80; //default(95) 0-100



    // If start frame is not zero, we get to the start frame by reading and dumping the frames
    if (start_frame > 0) {
        std::cout << "Seeking to " << start_frame - 1 << std::endl;

        video.set(cv::CAP_PROP_POS_FRAMES, start_frame - 1);
        video >> frame_a;

        count_frame = start_frame;

    #if ONLY_FIRST_FRAME
        cv::imwrite("frame_start.jpg", frame_a);

        cv::imencode("jpg", frame_a, buff, param);

        compressed = cv::imdecode(buff, cv::IMREAD_COLOR);

        cv::imwrite("frame_compressed.jpg", compressed);
    #endif

    }




    cv::Mat uniform_noise = cv::Mat::zeros(height, width, CV_8UC3);

    cv::randu(uniform_noise, 0, 255);

    uniform_noise *= 0.08;

    noised_frame_a = frame_a.clone();
    noised_frame_a += uniform_noise;

    //std::cout << uniform_noise << std::endl;
    //return 0;




    // T-flip-flop mechanism
    bool this_or_that = true;

    // Main routine
    while (true) {

        next_output_newline = "";

        // Invert next iteration
        this_or_that = !this_or_that;

        // Get next frame with a T flip flop mechanism
        if (this_or_that) {

            video >> frame_a;

            if (frame_a.empty()) {
                std::cout << debug_prefix << "Some frame is empty, exiting.." << std::endl;
                output_file.close();
                return 0;
            }

            // Instead of adding black border we set a background of the original frame resized to the
            // bleeded resolution and just overlay the original image
            cv::resize(frame_a, bleed_croppable_frame, cv::Size(width + (2*bleed), height + (2*bleed)));
            frame_a.copyTo(bleed_croppable_frame(cv::Rect(bleed, bleed, frame_a.cols, frame_a.rows)));

            // bleed_croppable_frame[bleed:bleed+frame_a.shape[0], bleed:bleed+frame_a.shape[1]] = frame_a;



            //cv::copyMakeBorder(frame_a, bleed_croppable_frame, bleed, bleed, bleed, bleed, cv::BORDER_CONSTANT, cv::Scalar(0));

            noised_frame_a = frame_a.clone();
            noised_frame_a += uniform_noise;

            compressed = noised_frame_a.clone();


            if (write_only_debug_video) {
                debug_frame = frame_a.clone();
            }


        } else {

            video >> frame_b;

            if (frame_b.empty()) {
                std::cout << debug_prefix << "Some frame is empty, exiting.." << std::endl;
                output_file.close();
                return 0;
            }

            // Instead of adding black border we set a background of the original frame resized to the
            // bleeded resolution and just overlay the original image
            cv::resize(frame_b, bleed_croppable_frame, cv::Size(width + (2*bleed), height + (2*bleed)));
            frame_b.copyTo(bleed_croppable_frame(cv::Rect(bleed, bleed, frame_b.cols, frame_b.rows)));

            // bleed_croppable_frame[bleed:bleed+frame_b.shape[0], bleed:bleed+frame_b.shape[1]] = frame_b;

            //cv::copyMakeBorder(frame_b, bleed_croppable_frame, bleed, bleed, bleed, bleed, cv::BORDER_CONSTANT, cv::Scalar(0));

            noised_frame_b = frame_b.clone();
            noised_frame_b += uniform_noise;

            compressed = noised_frame_b.clone();


            if (write_only_debug_video) {
                debug_frame = frame_b.clone();
            }

        }

        // // Compress the frame

        // Encode into a buffer
        cv::imencode(".jpg", compressed, buff, param);

        // Decode the compressed block
        compressed = cv::imdecode(buff, cv::IMREAD_COLOR);

        cv::imwrite("frame_compressed.jpg", compressed);

        next_output_newline += "pframe;" + std::to_string(count_frame) + "-";

        remaining_frames = total_frame_count - count_frame;

    #if SHOW_STATS
        std::cout << "[" << count_frame << "/" << total_frame_count << "] [" << remaining_frames << "]" << std::endl;;
    #endif


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


                /*
                bleeded_start_x = std::max(0, start_x - bleed);
                bleeded_start_y = std::max(0, start_y - bleed);

                bleeded_end_x = std::min(width, start_x + block_size + bleed);
                bleeded_end_y = std::min(height, start_y + block_size + bleed);
                */

                bleeded_start_x = (x * block_size);
                bleeded_start_y = (y * block_size);

                bleeded_end_x = std::min(width + (2*bleed),  bleeded_start_x + (2*bleed) + block_size);
                bleeded_end_y = std::min(height + (2*bleed), bleeded_start_y + (2*bleed) + block_size);


                //std::cout << "bleeded_start_x: " << bleeded_start_x << ", bleeded_stary_y: " << bleeded_start_y
                //          << " bleeded_end_x: " << bleeded_end_x << ", bleeded_end_y: " << bleeded_end_y << std::endl;


                cv::Rect bleeded_crop = cv::Rect(
                    bleeded_start_x,
                    bleeded_start_y,
                    (bleeded_end_x - bleeded_start_x),
                    (bleeded_end_y - bleeded_start_y)
                );

                //cv::Rect bleeded_crop = cv::Rect(
                //    std::max(0, start_x - bleed),
                //    std::max(0, start_y - bleed),
                //    std::min(width, end_x + bleed) - start_x,
                //    std::min(height, end_y + bleed) - start_y
                //);


                block_a = cv::Mat(frame_a, crop);
                block_b = cv::Mat(frame_b, crop);

                noised_block_a = cv::Mat(noised_frame_a, crop);
                noised_block_b = cv::Mat(noised_frame_b, crop);

                compressed_block = cv::Mat(compressed, crop);


                //std::cout << "start_x: " << start_x << ", stary_y: " << start_y
                //          << "end_x: " << end_x << ", end_y: " << end_y << std::endl;


            /*
            #if METHOD_USE_MSSIM

                block_msee_scalar = calculate_mssim(block_a, block_b);

                raw_block_mse = fit_ssim(block_msee_scalar[0], block_msee_scalar[1], block_msee_scalar[2], block_msee_scalar[3]);

                if (true) {
                    next_output_newline += ";" + std::to_string(block_id);
                }

            #endif
            */


            #if METHOD_USE_MSE

                // Raw MSE between two blocks
                raw_block_mse = calculate_mse(noised_block_a, noised_block_b);


                // Calculate the MSE of compressed
                if (this_or_that) {
                    compressed_mse = calculate_mse(compressed_block, noised_block_a);

                        #if VERBOSE_DEBUG
                            std::cout << "frame:[" << count_frame << "]-block_id:[" << block_id << "]-compressed_mse_a:[" << compressed_mse << "]-raw:[" << raw_block_mse << "],";
                        #endif

                } else {
                    compressed_mse = calculate_mse(compressed_block, noised_block_b);

                        #if VERBOSE_DEBUG
                            std::cout << "frame:[" << count_frame << "]-block_id:[" << block_id << "]-compressed_mse_b:[" << compressed_mse << "]-raw:[" << raw_block_mse << "]-status:[";
                        #endif

                }


            #if VERBOSE_DEBUG
                std::cout << "frame: " << count_frame << ", block_id: " << block_id << std::endl;
                std::cout << "Compressed block mse: " << compressed_mse << " - Raw mse: " << raw_block_mse << std::endl;
            #endif

            #if WRITE_COMPRESSED

                cv::imwrite("frame_compressed.jpg", compressed);

                cv::imwrite("compressed_block.jpg", compressed_block);

                return 0;

            #endif


                total_blocks++;

                // Validate
                if (raw_block_mse > compressed_mse) {

                #if VERBOSE_DEBUG
                    std::cout << "accepted]" << std::endl;
                #endif

                    need_upscaling++;

                    next_output_newline += ";" + std::to_string(block_id); // << "," << raw_block_mse;

                    //cv::imwrite("bleeded.jpg", bleeded_block_a);


                    if (this_or_that) {
                        //overlayImage(bleed_croppable_frame, frame_a, bleed_croppable_frame, cv::Point(start_x, start_y));

                        //cv::imwrite("a.jpg", bleed_croppable_frame);

                        bleeded_block_a = cv::Mat(bleed_croppable_frame, bleeded_crop);
                        matched_blocks.push_back(bleeded_block_a);

                    } else {
                        //overlayImage(bleed_croppable_frame, frame_b, bleed_croppable_frame, cv::Point(bleed, bleed));

                        //cv::imwrite("b.jpg", bleed_croppable_frame);

                        bleeded_block_b = cv::Mat(bleed_croppable_frame, bleeded_crop);
                        matched_blocks.push_back(bleeded_block_b);

                    }

                    //std::cout << raw_block_mse << " > " << compressed_mse << " - " << matched_blocks.size() << std::endl;



                    if (write_only_debug_video) {

                        //black_block.copyTo(debug_frame(cv::Rect(start_x, start_y, black_block.cols, black_block.rows)));

                        black_block = cv::Mat(resolution, CV_8UC4, cv::Scalar(0, 0, 0, 120));
                        overlayImage(debug_frame, black_block, debug_frame, cv::Point(start_x, start_y));
                    }


                } else {

                    dont_need_upscaling++;

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

        if (write_only_debug_video) {
            debug_video.write(debug_frame);
            std::cout << "Writing debug frame: [" << count_frame << "/" << total_frame_count << "]"
                      << ", (Need / Don't need) upscaling: [" << need_upscaling << "/" << dont_need_upscaling << "]"
                      << ", Total blocks: [" << total_blocks << "]" << ", Recylcled percentage: " << static_cast<double>(100)*dont_need_upscaling / total_blocks << std::endl;
        }

        next_output_newline += '\n';

        output_file << next_output_newline;

        output_file.flush();


        // // Make the input residual image



        if (matched_blocks.size() > 0) {

            cv::Mat residual = residual_functions::make_residual::from_block_vectors(matched_blocks, block_size, bleed);

            int max_frames_ahead = 10;
            int max_frames_ahead_wait = count_frame - max_frames_ahead;

            std::string residual_name = residuals_output + "residual_" + std::string(zero_padding - std::to_string(count_frame).length(), '0') + std::to_string(count_frame) + ".jpg";

            std::string residual_name_mindisk = residuals_output + "residual_" + std::string(zero_padding - std::to_string(max_frames_ahead_wait).length(), '0') + std::to_string(max_frames_ahead_wait) + ".jpg";

            // Mindisk utility, wait for the file - max_frames_ahead to be deleted
            while (mindisk && utils::file_exists(residual_name_mindisk)) {
                std::this_thread::sleep_for(std::chrono::milliseconds(50));

                #if VERBOSE_DEBUG
                    std::cout << "Waiting for residual [" << residual_name_mindisk << "] to be deleted" << std::endl;
                #endif

            }

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
    cv::Mat image = cv::imread("frame_a.jpg");

    cv::Mat uniform_noise = cv::Mat::zeros (image.rows, image.cols, CV_8UC1);

    cv::randu(uniform_noise, 0, 255);
    //cv::imshow("Uniform random noise", uniform_noise );
    //cv::waitKey();

    cv::imwrite("uniform1.jpg", uniform_noise);
    cv::imwrite("uniform0.5.jpg", uniform_noise*0.5);
    cv::imwrite("uniform0.2.jpg", uniform_noise*0.2);
    cv::imwrite("uniform0.1.jpg", uniform_noise*0.1);
    */

    // Another way to generate the random values form the same distribution is to use
    // functions randu and randn

    //cv::Mat image = cv::imread("frame_a.jpg");

    // Let's first create a zero image with the same dimensions of the loaded image

    //cv::Mat gaussian_noise = cv::Mat::zeros (image.rows, image.cols, CV_8UC1);

    //cv::imshow("All zero values", gaussian_noise);
    //cv::waitKey();

    // now, we can set the pixel values as a Gaussian noise
    // we have set a mean value to 128 and a standard deviation to 20
    //cv::randn(gaussian_noise, 50, 20);

    // Let's plot this image and see how it looks like
    //cv::imshow("Gaussian noise", gaussian_noise);
    //cv::waitKey();

    //cv::imwrite("Gaussian random noise.jpg", gaussian_noise);



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

    const int expected_args = 14;


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
     * - mindisk mode on / off [1/0]
     * - zero padding (residuals files)
     * - write_only_debug_video
     * - debug_video_output
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

    int mindisk_argv = atoi(argv[10]);

    int zero_padding = atoi(argv[11]);
    int write_only_debug_video_argv = atoi(argv[12]);

    std::string debug_video_output = argv[13];

    bool write_only_debug_video;
    bool mindisk;



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
        std::cout << debug_prefix << "mindisk_argv: " << mindisk_argv << '\n';
        std::cout << debug_prefix << "zero_padding: " << zero_padding << '\n';
        std::cout << debug_prefix << "write_only_debug_video: " << write_only_debug_video << '\n';
        std::cout << debug_prefix << "debug_video_output: " << debug_video_output << '\n';
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


    if (mindisk_argv == 1) {
        mindisk = true;
    } else if (mindisk_argv == 0) {
        mindisk = false;
    } else {
        std::cout << debug_prefix << "Mindisk mode not 0 or 1 recieved from argv" << std::endl;
        std::exit(-1);
    }

    if (write_only_debug_video_argv == 1) {
        write_only_debug_video = true;
    } else if (write_only_debug_video_argv == 0) {
        write_only_debug_video = false;
    } else {
        std::cout << debug_prefix << "Only debug video not 0 or 1 recieved from argv" << std::endl;
        std::exit(-1);
    }

    process_video(
        video_path,
        block_size,
        width,
        height,
        output_d2x_file,
        output_vectors_path,
        start_frame,
        bleed,
        residuals_output,
        mindisk,
        zero_padding,
        write_only_debug_video,
        debug_video_output
    );

    return 0;
}
