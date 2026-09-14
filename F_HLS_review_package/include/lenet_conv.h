#ifndef LENET_CONV_H_
#define LENET_CONV_H_

namespace lenet {

typedef float data_t;
typedef float weight_t;

constexpr int KERNEL_SIZE = 5;
constexpr int KERNEL_ELEMS = KERNEL_SIZE * KERNEL_SIZE;

constexpr int INPUT_C = 1;
constexpr int INPUT_H = 32;
constexpr int INPUT_W = 32;
constexpr int INPUT_ELEMS = INPUT_C * INPUT_H * INPUT_W;

constexpr int CONV1_OUT_C = 6;
constexpr int CONV1_OUT_H = 28;
constexpr int CONV1_OUT_W = 28;
constexpr int CONV1_OUT_ELEMS = CONV1_OUT_C * CONV1_OUT_H * CONV1_OUT_W;
constexpr int CONV1_WEIGHT_ELEMS = CONV1_OUT_C * INPUT_C * KERNEL_ELEMS;
constexpr int CONV1_BIAS_ELEMS = CONV1_OUT_C;

constexpr int POOL1_OUT_C = 6;
constexpr int POOL1_OUT_H = 14;
constexpr int POOL1_OUT_W = 14;
constexpr int POOL1_OUT_ELEMS = POOL1_OUT_C * POOL1_OUT_H * POOL1_OUT_W;

constexpr int CONV2_OUT_C = 16;
constexpr int CONV2_OUT_H = 10;
constexpr int CONV2_OUT_W = 10;
constexpr int CONV2_OUT_ELEMS = CONV2_OUT_C * CONV2_OUT_H * CONV2_OUT_W;
constexpr int CONV2_WEIGHT_ELEMS =
    CONV2_OUT_C * POOL1_OUT_C * KERNEL_ELEMS;
constexpr int CONV2_BIAS_ELEMS = CONV2_OUT_C;

constexpr int POOL2_OUT_C = 16;
constexpr int POOL2_OUT_H = 5;
constexpr int POOL2_OUT_W = 5;
constexpr int POOL2_OUT_ELEMS = POOL2_OUT_C * POOL2_OUT_H * POOL2_OUT_W;

constexpr int CONV3_OUT_C = 120;
constexpr int CONV3_OUT_H = 1;
constexpr int CONV3_OUT_W = 1;
constexpr int CONV3_OUT_ELEMS = CONV3_OUT_C;
constexpr int CONV3_WEIGHT_ELEMS =
    CONV3_OUT_C * POOL2_OUT_C * KERNEL_ELEMS;
constexpr int CONV3_BIAS_ELEMS = CONV3_OUT_C;

constexpr int FC1_IN_ELEMS = CONV3_OUT_ELEMS;
constexpr int FC1_OUT_ELEMS = 84;
constexpr int FC1_WEIGHT_ELEMS = FC1_OUT_ELEMS * FC1_IN_ELEMS;
constexpr int FC1_BIAS_ELEMS = FC1_OUT_ELEMS;

constexpr int FC2_IN_ELEMS = FC1_OUT_ELEMS;
constexpr int FC2_OUT_ELEMS = 10;
constexpr int FC2_WEIGHT_ELEMS = FC2_OUT_ELEMS * FC2_IN_ELEMS;
constexpr int FC2_BIAS_ELEMS = FC2_OUT_ELEMS;

constexpr int CONV1_WEIGHT_OFFSET = 0;
constexpr int CONV2_WEIGHT_OFFSET = CONV1_WEIGHT_OFFSET + CONV1_WEIGHT_ELEMS;
constexpr int CONV3_WEIGHT_OFFSET = CONV2_WEIGHT_OFFSET + CONV2_WEIGHT_ELEMS;
constexpr int FC1_WEIGHT_OFFSET = CONV3_WEIGHT_OFFSET + CONV3_WEIGHT_ELEMS;
constexpr int FC2_WEIGHT_OFFSET = FC1_WEIGHT_OFFSET + FC1_WEIGHT_ELEMS;
constexpr int TOTAL_WEIGHT_ELEMS = FC2_WEIGHT_OFFSET + FC2_WEIGHT_ELEMS;

constexpr int CONV1_BIAS_OFFSET = 0;
constexpr int CONV2_BIAS_OFFSET = CONV1_BIAS_OFFSET + CONV1_BIAS_ELEMS;
constexpr int CONV3_BIAS_OFFSET = CONV2_BIAS_OFFSET + CONV2_BIAS_ELEMS;
constexpr int FC1_BIAS_OFFSET = CONV3_BIAS_OFFSET + CONV3_BIAS_ELEMS;
constexpr int FC2_BIAS_OFFSET = FC1_BIAS_OFFSET + FC1_BIAS_ELEMS;
constexpr int TOTAL_BIAS_ELEMS = FC2_BIAS_OFFSET + FC2_BIAS_ELEMS;

// Golden convolution and FC maps are compared before ReLU.
void lenet_relu_pool1(
    const data_t feature_in[CONV1_OUT_ELEMS],
    data_t feature_out[POOL1_OUT_ELEMS]);

void lenet_relu_pool2(
    const data_t feature_in[CONV2_OUT_ELEMS],
    data_t feature_out[POOL2_OUT_ELEMS]);

void lenet_relu_conv3(
    const data_t feature_in[CONV3_OUT_ELEMS],
    data_t feature_out[CONV3_OUT_ELEMS]);

void lenet_relu_fc1(
    const data_t feature_in[FC1_OUT_ELEMS],
    data_t feature_out[FC1_OUT_ELEMS]);

}  // namespace lenet

// Uniform interface: feature_in, weight, bias, feature_out.
// The current model has bias=False; testbenches therefore pass zero arrays.
extern "C" void lenet_conv1_top(
    const lenet::data_t feature_in[lenet::INPUT_ELEMS],
    const lenet::weight_t weight[lenet::CONV1_WEIGHT_ELEMS],
    const lenet::weight_t bias[lenet::CONV1_BIAS_ELEMS],
    lenet::data_t feature_out[lenet::CONV1_OUT_ELEMS]);

extern "C" void lenet_conv2_top(
    const lenet::data_t feature_in[lenet::POOL1_OUT_ELEMS],
    const lenet::weight_t weight[lenet::CONV2_WEIGHT_ELEMS],
    const lenet::weight_t bias[lenet::CONV2_BIAS_ELEMS],
    lenet::data_t feature_out[lenet::CONV2_OUT_ELEMS]);

extern "C" void lenet_conv3_top(
    const lenet::data_t feature_in[lenet::POOL2_OUT_ELEMS],
    const lenet::weight_t weight[lenet::CONV3_WEIGHT_ELEMS],
    const lenet::weight_t bias[lenet::CONV3_BIAS_ELEMS],
    lenet::data_t feature_out[lenet::CONV3_OUT_ELEMS]);

extern "C" void lenet_fc1_top(
    const lenet::data_t feature_in[lenet::FC1_IN_ELEMS],
    const lenet::weight_t weight[lenet::FC1_WEIGHT_ELEMS],
    const lenet::weight_t bias[lenet::FC1_BIAS_ELEMS],
    lenet::data_t feature_out[lenet::FC1_OUT_ELEMS]);

extern "C" void lenet_fc2_top(
    const lenet::data_t feature_in[lenet::FC2_IN_ELEMS],
    const lenet::weight_t weight[lenet::FC2_WEIGHT_ELEMS],
    const lenet::weight_t bias[lenet::FC2_BIAS_ELEMS],
    lenet::data_t feature_out[lenet::FC2_OUT_ELEMS]);

extern "C" void lenet_full_top(
    const lenet::data_t feature_in[lenet::INPUT_ELEMS],
    const lenet::weight_t weight[lenet::TOTAL_WEIGHT_ELEMS],
    const lenet::weight_t bias[lenet::TOTAL_BIAS_ELEMS],
    lenet::data_t feature_out[lenet::FC2_OUT_ELEMS]);

#endif  // LENET_CONV_H_
