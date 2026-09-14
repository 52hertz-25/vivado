#ifndef LENET_W8A8_H_
#define LENET_W8A8_H_

#include <ap_int.h>

namespace lenet_w8a8 {

typedef ap_int<8> act_t;
typedef ap_int<8> weight_t;
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
constexpr long long CONV1_REQUANT_Q40 = 1770038739LL;
constexpr long long CONV2_REQUANT_Q40 = 2276981933LL;
constexpr long long CONV3_REQUANT_Q40 = 2430923592LL;
constexpr long long FC1_REQUANT_Q40 = 4309926909LL;
constexpr int REQUANT_SHIFT = 40;

}  // namespace lenet_w8a8

extern "C" void lenet_w8a8_top(
    const lenet_w8a8::act_t feature_in[lenet_w8a8::INPUT_ELEMS],
    const lenet_w8a8::weight_t weight[lenet_w8a8::TOTAL_WEIGHT_ELEMS],
    lenet_w8a8::accum_t logits[lenet_w8a8::FC2_OUT_ELEMS]);

#endif
