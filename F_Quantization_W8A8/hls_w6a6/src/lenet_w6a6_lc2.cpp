#include "lenet_w6a6.h"

namespace lenet_w6a6 {
namespace {

act_t requantize_relu(accum_t value, long long multiplier_q40) {
#pragma HLS INLINE
    if (value <= 0) {
        return act_t(0);
    }

    ap_uint<64> product =
        ap_uint<64>(value) * ap_uint<64>(multiplier_q40);
    ap_uint<64> quotient = product >> REQUANT_SHIFT;
    const ap_uint<64> mask = (ap_uint<64>(1) << REQUANT_SHIFT) - 1;
    const ap_uint<64> remainder = product & mask;
    const ap_uint<64> half = ap_uint<64>(1) << (REQUANT_SHIFT - 1);

    // Round to nearest, ties to even, matching torch.round for nonnegative ReLU data.
    if (remainder > half || (remainder == half && quotient[0] == 1)) {
        ++quotient;
    }
    if (quotient > 31) {
        quotient = 31;
    }
    return act_t(quotient.range(5, 0));
}

template <int IN_C, int IN_H, int IN_W, int OUT_C>
void conv5x5_accumulate(
    const act_t feature_in[IN_C * IN_H * IN_W],
    const weight_t weight[OUT_C * IN_C * KERNEL_ELEMS],
    accum_t feature_out[OUT_C * (IN_H - 4) * (IN_W - 4)]) {
    const int out_h = IN_H - KERNEL_SIZE + 1;
    const int out_w = IN_W - KERNEL_SIZE + 1;

OUT_CHANNEL:
    for (int oc = 0; oc < OUT_C; ++oc) {
        weight_t local_weight[IN_C * KERNEL_ELEMS];
#pragma HLS ARRAY_PARTITION variable=local_weight cyclic factor=2 dim=1
    LOAD_LOCAL_WEIGHT:
        for (int wi = 0; wi < IN_C * KERNEL_ELEMS; ++wi) {
#pragma HLS PIPELINE II=1
            local_weight[wi] =
                weight[oc * IN_C * KERNEL_ELEMS + wi];
        }
    OUT_ROW:
        for (int oh = 0; oh < out_h; ++oh) {
        OUT_COL:
            for (int ow = 0; ow < out_w; ++ow) {
                accum_t accumulator = 0;
            IN_CHANNEL:
#pragma HLS UNROLL factor=2
                for (int ic = 0; ic < IN_C; ++ic) {
                KERNEL_ROW:
                    for (int kh = 0; kh < KERNEL_SIZE; ++kh) {
                    KERNEL_COL:
                        for (int kw = 0; kw < KERNEL_SIZE; ++kw) {
                            const int input_index =
                                (ic * IN_H + oh + kh) * IN_W + ow + kw;
                            const int weight_index =
                                (ic * KERNEL_SIZE + kh) * KERNEL_SIZE + kw;
                            accumulator +=
                                accum_t(feature_in[input_index]) *
                                accum_t(local_weight[weight_index]);
                        }
                    }
                }
                const int output_index = (oc * out_h + oh) * out_w + ow;
                feature_out[output_index] = accumulator;
            }
        }
    }
}

template <int CHANNELS, int H, int W>
void requant_relu_pool2x2(
    const accum_t feature_in[CHANNELS * H * W],
    act_t feature_out[CHANNELS * (H / 2) * (W / 2)],
    long long multiplier_q40) {
    const int out_h = H / 2;
    const int out_w = W / 2;

POOL_CHANNEL:
    for (int c = 0; c < CHANNELS; ++c) {
    POOL_ROW:
        for (int oh = 0; oh < out_h; ++oh) {
        POOL_COL:
            for (int ow = 0; ow < out_w; ++ow) {
                act_t maximum = 0;
            POOL_KH:
                for (int kh = 0; kh < 2; ++kh) {
                POOL_KW:
                    for (int kw = 0; kw < 2; ++kw) {
                        const int ih = oh * 2 + kh;
                        const int iw = ow * 2 + kw;
                        const int index = (c * H + ih) * W + iw;
                        const act_t value =
                            requantize_relu(feature_in[index], multiplier_q40);
                        if (value > maximum) {
                            maximum = value;
                        }
                    }
                }
                feature_out[(c * out_h + oh) * out_w + ow] = maximum;
            }
        }
    }
}

template <int ELEMENTS>
void requant_relu_vector(
    const accum_t feature_in[ELEMENTS],
    act_t feature_out[ELEMENTS],
    long long multiplier_q40) {
REQUANT_VECTOR:
    for (int i = 0; i < ELEMENTS; ++i) {
        feature_out[i] = requantize_relu(feature_in[i], multiplier_q40);
    }
}

template <int IN_ELEMS, int OUT_ELEMS>
void dense_accumulate(
    const act_t feature_in[IN_ELEMS],
    const weight_t weight[OUT_ELEMS * IN_ELEMS],
    accum_t feature_out[OUT_ELEMS]) {
DENSE_OUTPUT:
    for (int output_index = 0; output_index < OUT_ELEMS; ++output_index) {
        accum_t accumulator = 0;
    DENSE_INPUT:
        for (int input_index = 0; input_index < IN_ELEMS; ++input_index) {
            accumulator +=
                accum_t(feature_in[input_index]) *
                accum_t(weight[output_index * IN_ELEMS + input_index]);
        }
        feature_out[output_index] = accumulator;
    }
}

}  // namespace
}  // namespace lenet_w6a6

extern "C" void lenet_w6a6_top(
    const lenet_w6a6::act_t feature_in[lenet_w6a6::INPUT_ELEMS],
    const lenet_w6a6::weight_t weight[lenet_w6a6::TOTAL_WEIGHT_ELEMS],
    lenet_w6a6::accum_t logits[lenet_w6a6::FC2_OUT_ELEMS]) {
#pragma HLS INTERFACE m_axi port=feature_in offset=slave bundle=gmem0 depth=1024
#pragma HLS INTERFACE m_axi port=weight offset=slave bundle=gmem1 depth=61470
#pragma HLS INTERFACE m_axi port=logits offset=slave bundle=gmem2 depth=10
#pragma HLS INTERFACE s_axilite port=feature_in bundle=control
#pragma HLS INTERFACE s_axilite port=weight bundle=control
#pragma HLS INTERFACE s_axilite port=logits bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

    using namespace lenet_w6a6;

    accum_t conv1_acc[CONV1_OUT_ELEMS];
    act_t pool1[POOL1_OUT_ELEMS];
    accum_t conv2_acc[CONV2_OUT_ELEMS];
    act_t pool2[POOL2_OUT_ELEMS];
    accum_t conv3_acc[CONV3_OUT_ELEMS];
    act_t conv3_relu[CONV3_OUT_ELEMS];
    accum_t fc1_acc[FC1_OUT_ELEMS];
    act_t fc1_relu[FC1_OUT_ELEMS];

    conv5x5_accumulate<INPUT_C, INPUT_H, INPUT_W, CONV1_OUT_C>(
        feature_in, &weight[CONV1_WEIGHT_OFFSET], conv1_acc);
    requant_relu_pool2x2<CONV1_OUT_C, CONV1_OUT_H, CONV1_OUT_W>(
        conv1_acc, pool1, CONV1_REQUANT_Q40);

    conv5x5_accumulate<POOL1_OUT_C, POOL1_OUT_H, POOL1_OUT_W, CONV2_OUT_C>(
        pool1, &weight[CONV2_WEIGHT_OFFSET], conv2_acc);
    requant_relu_pool2x2<CONV2_OUT_C, CONV2_OUT_H, CONV2_OUT_W>(
        conv2_acc, pool2, CONV2_REQUANT_Q40);

    conv5x5_accumulate<POOL2_OUT_C, POOL2_OUT_H, POOL2_OUT_W, CONV3_OUT_C>(
        pool2, &weight[CONV3_WEIGHT_OFFSET], conv3_acc);
    requant_relu_vector<CONV3_OUT_ELEMS>(
        conv3_acc, conv3_relu, CONV3_REQUANT_Q40);

    dense_accumulate<FC1_IN_ELEMS, FC1_OUT_ELEMS>(
        conv3_relu, &weight[FC1_WEIGHT_OFFSET], fc1_acc);
    requant_relu_vector<FC1_OUT_ELEMS>(
        fc1_acc, fc1_relu, FC1_REQUANT_Q40);

    dense_accumulate<FC2_IN_ELEMS, FC2_OUT_ELEMS>(
        fc1_relu, &weight[FC2_WEIGHT_OFFSET], logits);
}
