#ifndef LENET_W6A6_H_
#define LENET_W6A6_H_

#include <ap_int.h>

namespace lenet_w6a6 {

typedef ap_int<6> act_t;
typedef ap_int<6> weight_t;
typedef ap_int<32> accum_t;

constexpr int KERNEL_SIZE = 5;
constexpr int KERNEL_ELEMS = 25;

constexpr int INPUT_C = 1;
constexpr int INPUT_H = 32;
constexpr int INPUT_W = 32;
constexpr int INPUT_ELEMS = 1024;

constexpr int CONV1_OUT_C = 6;
constexpr int CONV1_OUT_H = 28;
constexpr int CONV1_OUT_W = 28;
constexpr int CONV1_OUT_ELEMS = 4704;
constexpr int CONV1_WEIGHT_ELEMS = 150;

constexpr int POOL1_OUT_C = 6;
constexpr int POOL1_OUT_H = 14;
constexpr int POOL1_OUT_W = 14;
constexpr int POOL1_OUT_ELEMS = 1176;

constexpr int CONV2_OUT_C = 16;
constexpr int CONV2_OUT_H = 10;
constexpr int CONV2_OUT_W = 10;
constexpr int CONV2_OUT_ELEMS = 1600;
constexpr int CONV2_WEIGHT_ELEMS = 2400;

constexpr int POOL2_OUT_C = 16;
constexpr int POOL2_OUT_H = 5;
constexpr int POOL2_OUT_W = 5;
constexpr int POOL2_OUT_ELEMS = 400;

constexpr int CONV3_OUT_C = 120;
constexpr int CONV3_OUT_ELEMS = 120;
constexpr int CONV3_WEIGHT_ELEMS = 48000;

constexpr int FC1_IN_ELEMS = 120;
constexpr int FC1_OUT_ELEMS = 84;
constexpr int FC1_WEIGHT_ELEMS = 10080;

constexpr int FC2_IN_ELEMS = 84;
constexpr int FC2_OUT_ELEMS = 10;
constexpr int FC2_WEIGHT_ELEMS = 840;

constexpr int CONV1_WEIGHT_OFFSET = 0;
constexpr int CONV2_WEIGHT_OFFSET = 150;
constexpr int CONV3_WEIGHT_OFFSET = 2550;
constexpr int FC1_WEIGHT_OFFSET = 50550;
constexpr int FC2_WEIGHT_OFFSET = 60630;
constexpr int TOTAL_WEIGHT_ELEMS = 61470;

// Q40 approximations of:
// input_scale * weight_scale / output_activation_scale.
constexpr long long CONV1_REQUANT_Q40 = 7251449029LL;
constexpr long long CONV2_REQUANT_Q40 = 9328280821LL;
constexpr long long CONV3_REQUANT_Q40 = 9958945039LL;
constexpr long long FC1_REQUANT_Q40 = 17656797338LL;
constexpr int REQUANT_SHIFT = 40;

}  // namespace lenet_w6a6

extern "C" void lenet_w6a6_top(
    const lenet_w6a6::act_t feature_in[lenet_w6a6::INPUT_ELEMS],
    const lenet_w6a6::weight_t weight[lenet_w6a6::TOTAL_WEIGHT_ELEMS],
    lenet_w6a6::accum_t logits[lenet_w6a6::FC2_OUT_ELEMS]);

#endif
