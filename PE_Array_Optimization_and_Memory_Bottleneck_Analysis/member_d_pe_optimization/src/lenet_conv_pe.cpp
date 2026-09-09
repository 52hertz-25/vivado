#include "lenet_conv.h"
#include "pe_config.h"

namespace lenet {
namespace {

template <int IN_H, int IN_W>
void generate_window_5x5(
    const data_t *feature_in,
    int input_channel,
    int output_row,
    int output_col,
    data_t window[KERNEL_ELEMS]) {
#pragma HLS INLINE

WINDOW_ROW:
    for (int kernel_row = 0; kernel_row < KERNEL_SIZE; ++kernel_row) {
    WINDOW_COL:
        for (int kernel_col = 0; kernel_col < KERNEL_SIZE; ++kernel_col) {
            const int input_index =
                (input_channel * IN_H + output_row + kernel_row) * IN_W +
                output_col + kernel_col;
            window[kernel_row * KERNEL_SIZE + kernel_col] =
                feature_in[input_index];
        }
    }
}

data_t mac_5x5(
    const data_t window[KERNEL_ELEMS],
    const weight_t kernel[KERNEL_ELEMS],
    data_t accumulator) {
#pragma HLS INLINE

MAC_LOOP:
    for (int index = 0; index < KERNEL_ELEMS; ++index) {
        accumulator += window[index] * kernel[index];
    }
    return accumulator;
}

// PE_MAC / PE_OC 由 pe_config.h 统一控制（默认 PE_OC=4, PE_MAC=5）

data_t mac_5x5_pe(
    const data_t window[KERNEL_ELEMS],
    const weight_t kernel[KERNEL_ELEMS],
    data_t accumulator) {
#pragma HLS INLINE
#pragma HLS ARRAY_PARTITION variable=window cyclic factor=5 dim=1
#pragma HLS ARRAY_PARTITION variable=kernel cyclic factor=5 dim=1

    data_t partial[PE_MAC];
#pragma HLS ARRAY_PARTITION variable=partial complete dim=1

INIT_PARTIAL:
    for (int p = 0; p < PE_MAC; ++p) {
#pragma HLS UNROLL
        partial[p] = 0.0f;
    }

MAC_GROUP:
    for (int base = 0; base < KERNEL_ELEMS; base += PE_MAC) {
#pragma HLS PIPELINE
    MAC_PE:
        for (int p = 0; p < PE_MAC; ++p) {
#pragma HLS UNROLL
            if (base + p < KERNEL_ELEMS)
                partial[p] += window[base + p] * kernel[base + p];
        }
    }

REDUCE:
    for (int p = 0; p < PE_MAC; ++p)
        accumulator += partial[p];

    return accumulator;
}


// PE_OC / PE_MAC 直接取自 pe_config.h 宏（默认 PE_OC=4, PE_MAC=5）
template <int IN_C, int IN_H, int IN_W, int OUT_C>
void conv5x5_valid(
    const data_t feature_in[IN_C * IN_H * IN_W],
    const weight_t weight[OUT_C * IN_C * KERNEL_ELEMS],
    const weight_t bias[OUT_C],
    data_t feature_out[OUT_C * (IN_H - 4) * (IN_W - 4)]) {
    const int out_h = IN_H - KERNEL_SIZE + 1;
    const int out_w = IN_W - KERNEL_SIZE + 1;

    // ------------------------------------------------------------
    // D5 优化：把 AXI 输入一次性搬进局部数组，解除内层流水线对
    // gmem0/gmem1/gmem2 总线端口带宽的依赖（手册第 9 章“内存端口不够”）。
    // - local_weight 按 cyclic 5 切分：与 PE_MAC=5 的乘加组一一对应；
    // - local_bias 完全展开为寄存器；
    // - local_feature 保持块内 BRAM（生成窗口时多周期顺序读取），
    //   避免过度分区带来的综合调度压力。
    // ------------------------------------------------------------
    data_t local_feature[IN_C * IN_H * IN_W];
    weight_t local_weight[OUT_C * IN_C * KERNEL_ELEMS];
    weight_t local_bias[OUT_C];
#pragma HLS ARRAY_PARTITION variable=local_weight cyclic factor=5 dim=1
#pragma HLS ARRAY_PARTITION variable=local_bias complete dim=1

LOAD_FEATURE:
    for (int i = 0; i < IN_C * IN_H * IN_W; ++i) {
#pragma HLS PIPELINE
        local_feature[i] = feature_in[i];
    }
LOAD_WEIGHT:
    for (int i = 0; i < OUT_C * IN_C * KERNEL_ELEMS; ++i) {
#pragma HLS PIPELINE
        local_weight[i] = weight[i];
    }
LOAD_BIAS:
    for (int i = 0; i < OUT_C; ++i) {
#pragma HLS PIPELINE
        local_bias[i] = bias[i];
    }

OUTPUT_CHANNEL_BLOCK:
    for (int oc_base = 0; oc_base < OUT_C; oc_base += PE_OC) {
    OUTPUT_ROW:
        for (int output_row = 0; output_row < out_h; ++output_row) {
        OUTPUT_COL:
            for (int output_col = 0; output_col < out_w; ++output_col) {
            	// II=32：显式限制流水线吞吐，防止 HLS 全展开导致资源爆炸
            	#pragma HLS PIPELINE II=32
                data_t accumulator[PE_OC];
#pragma HLS ARRAY_PARTITION variable=accumulator complete dim=1
            PE_INIT:
                for (int pe = 0; pe < PE_OC; ++pe) {
#pragma HLS UNROLL
                    accumulator[pe] = (oc_base + pe < OUT_C) ? local_bias[oc_base + pe] : 0.0f;
                }
            INPUT_CHANNEL:
                for (int input_channel = 0; input_channel < IN_C;
                     ++input_channel) {
                    data_t window[KERNEL_ELEMS];
                    generate_window_5x5<IN_H, IN_W>(
                        local_feature,
                        input_channel,
                        output_row,
                        output_col,
                        window);
                    const int kernel_base =
                        (oc_base * IN_C + input_channel) * KERNEL_ELEMS;
                PE_MAC_LOOP:
                    for (int pe = 0; pe < PE_OC; ++pe) {
#pragma HLS UNROLL
                        if (oc_base + pe < OUT_C) {
                            accumulator[pe] = mac_5x5_pe(
                                window,
                                &local_weight[kernel_base +
                                        pe * IN_C * KERNEL_ELEMS],
                                accumulator[pe]);
                        }
                    }
                }
            PE_WRITE:
                for (int pe = 0; pe < PE_OC; ++pe) {
#pragma HLS UNROLL
                    if (oc_base + pe < OUT_C) {
                        const int output_index =
                            ((oc_base + pe) * out_h + output_row) * out_w +
                            output_col;
                        feature_out[output_index] = accumulator[pe];
                    }
                }
            }
        }
    }
}


template <int CHANNELS, int IN_H, int IN_W>
void relu_maxpool_2x2(
    const data_t feature_in[CHANNELS * IN_H * IN_W],
    data_t feature_out[CHANNELS * (IN_H / 2) * (IN_W / 2)]) {
    const int out_h = IN_H / 2;
    const int out_w = IN_W / 2;

POOL_CHANNEL:
    for (int channel = 0; channel < CHANNELS; ++channel) {
    POOL_ROW:
        for (int output_row = 0; output_row < out_h; ++output_row) {
        POOL_COL:
            for (int output_col = 0; output_col < out_w; ++output_col) {
                data_t maximum = 0.0f;

            POOL_KERNEL_ROW:
                for (int kernel_row = 0; kernel_row < 2; ++kernel_row) {
                POOL_KERNEL_COL:
                    for (int kernel_col = 0; kernel_col < 2; ++kernel_col) {
                        const int input_row = output_row * 2 + kernel_row;
                        const int input_col = output_col * 2 + kernel_col;
                        const int input_index =
                            (channel * IN_H + input_row) * IN_W + input_col;
                        const data_t value = feature_in[input_index];
                        if (value > maximum) {
                            maximum = value;
                        }
                    }
                }

                const int output_index =
                    (channel * out_h + output_row) * out_w + output_col;
                feature_out[output_index] = maximum;
            }
        }
    }
}

template <int ELEMENTS>
void relu_vector(
    const data_t feature_in[ELEMENTS],
    data_t feature_out[ELEMENTS]) {
RELU_LOOP:
    for (int index = 0; index < ELEMENTS; ++index) {
        const data_t value = feature_in[index];
        feature_out[index] = value > 0.0f ? value : 0.0f;
    }
}

template <int IN_ELEMS, int OUT_ELEMS>
void dense(
    const data_t feature_in[IN_ELEMS],
    const weight_t weight[OUT_ELEMS * IN_ELEMS],
    const weight_t bias[OUT_ELEMS],
    data_t feature_out[OUT_ELEMS]) {
DENSE_OUTPUT:
    for (int output_index = 0; output_index < OUT_ELEMS; ++output_index) {
        data_t accumulator = bias[output_index];

    DENSE_INPUT:
        for (int input_index = 0; input_index < IN_ELEMS; ++input_index) {
            accumulator +=
                feature_in[input_index] *
                weight[output_index * IN_ELEMS + input_index];
        }
        feature_out[output_index] = accumulator;
    }
}

}  // namespace

void lenet_relu_pool1(
    const data_t feature_in[CONV1_OUT_ELEMS],
    data_t feature_out[POOL1_OUT_ELEMS]) {
    relu_maxpool_2x2<CONV1_OUT_C, CONV1_OUT_H, CONV1_OUT_W>(
        feature_in, feature_out);
}

void lenet_relu_pool2(
    const data_t feature_in[CONV2_OUT_ELEMS],
    data_t feature_out[POOL2_OUT_ELEMS]) {
    relu_maxpool_2x2<CONV2_OUT_C, CONV2_OUT_H, CONV2_OUT_W>(
        feature_in, feature_out);
}

void lenet_relu_conv3(
    const data_t feature_in[CONV3_OUT_ELEMS],
    data_t feature_out[CONV3_OUT_ELEMS]) {
    relu_vector<CONV3_OUT_ELEMS>(feature_in, feature_out);
}

void lenet_relu_fc1(
    const data_t feature_in[FC1_OUT_ELEMS],
    data_t feature_out[FC1_OUT_ELEMS]) {
    relu_vector<FC1_OUT_ELEMS>(feature_in, feature_out);
}

}  // namespace lenet

extern "C" void lenet_conv1_top(
    const lenet::data_t feature_in[lenet::INPUT_ELEMS],
    const lenet::weight_t weight[lenet::CONV1_WEIGHT_ELEMS],
    const lenet::weight_t bias[lenet::CONV1_BIAS_ELEMS],
    lenet::data_t feature_out[lenet::CONV1_OUT_ELEMS]) {
#pragma HLS INTERFACE m_axi port=feature_in offset=direct bundle=gmem0 depth=1024
#pragma HLS INTERFACE m_axi port=weight offset=direct bundle=gmem1 depth=150
#pragma HLS INTERFACE m_axi port=bias offset=direct bundle=gmem2 depth=6
#pragma HLS INTERFACE m_axi port=feature_out offset=direct bundle=gmem3 depth=4704
#pragma HLS INTERFACE ap_ctrl_hs port=return

    lenet::conv5x5_valid<
        lenet::INPUT_C, lenet::INPUT_H, lenet::INPUT_W, lenet::CONV1_OUT_C>(
        feature_in, weight, bias, feature_out);
}

extern "C" void lenet_conv2_top(
    const lenet::data_t feature_in[lenet::POOL1_OUT_ELEMS],
    const lenet::weight_t weight[lenet::CONV2_WEIGHT_ELEMS],
    const lenet::weight_t bias[lenet::CONV2_BIAS_ELEMS],
    lenet::data_t feature_out[lenet::CONV2_OUT_ELEMS]) {
#pragma HLS INTERFACE m_axi port=feature_in offset=direct bundle=gmem0 depth=1176
#pragma HLS INTERFACE m_axi port=weight offset=direct bundle=gmem1 depth=2400
#pragma HLS INTERFACE m_axi port=bias offset=direct bundle=gmem2 depth=16
#pragma HLS INTERFACE m_axi port=feature_out offset=direct bundle=gmem3 depth=1600
#pragma HLS INTERFACE ap_ctrl_hs port=return

    lenet::conv5x5_valid<
        lenet::POOL1_OUT_C,
        lenet::POOL1_OUT_H,
        lenet::POOL1_OUT_W,
        lenet::CONV2_OUT_C>(feature_in, weight, bias, feature_out);
}

extern "C" void lenet_conv3_top(
    const lenet::data_t feature_in[lenet::POOL2_OUT_ELEMS],
    const lenet::weight_t weight[lenet::CONV3_WEIGHT_ELEMS],
    const lenet::weight_t bias[lenet::CONV3_BIAS_ELEMS],
    lenet::data_t feature_out[lenet::CONV3_OUT_ELEMS]) {
#pragma HLS INTERFACE m_axi port=feature_in offset=direct bundle=gmem0 depth=400
#pragma HLS INTERFACE m_axi port=weight offset=direct bundle=gmem1 depth=48000
#pragma HLS INTERFACE m_axi port=bias offset=direct bundle=gmem2 depth=120
#pragma HLS INTERFACE m_axi port=feature_out offset=direct bundle=gmem3 depth=120
#pragma HLS INTERFACE ap_ctrl_hs port=return

    lenet::conv5x5_valid<
        lenet::POOL2_OUT_C,
        lenet::POOL2_OUT_H,
        lenet::POOL2_OUT_W,
        lenet::CONV3_OUT_C>(feature_in, weight, bias, feature_out);
}

extern "C" void lenet_fc1_top(
    const lenet::data_t feature_in[lenet::FC1_IN_ELEMS],
    const lenet::weight_t weight[lenet::FC1_WEIGHT_ELEMS],
    const lenet::weight_t bias[lenet::FC1_BIAS_ELEMS],
    lenet::data_t feature_out[lenet::FC1_OUT_ELEMS]) {
#pragma HLS INTERFACE m_axi port=feature_in offset=direct bundle=gmem0 depth=120
#pragma HLS INTERFACE m_axi port=weight offset=direct bundle=gmem1 depth=10080
#pragma HLS INTERFACE m_axi port=bias offset=direct bundle=gmem2 depth=84
#pragma HLS INTERFACE m_axi port=feature_out offset=direct bundle=gmem3 depth=84
#pragma HLS INTERFACE ap_ctrl_hs port=return

    lenet::dense<lenet::FC1_IN_ELEMS, lenet::FC1_OUT_ELEMS>(
        feature_in, weight, bias, feature_out);
}

extern "C" void lenet_fc2_top(
    const lenet::data_t feature_in[lenet::FC2_IN_ELEMS],
    const lenet::weight_t weight[lenet::FC2_WEIGHT_ELEMS],
    const lenet::weight_t bias[lenet::FC2_BIAS_ELEMS],
    lenet::data_t feature_out[lenet::FC2_OUT_ELEMS]) {
#pragma HLS INTERFACE m_axi port=feature_in offset=direct bundle=gmem0 depth=84
#pragma HLS INTERFACE m_axi port=weight offset=direct bundle=gmem1 depth=840
#pragma HLS INTERFACE m_axi port=bias offset=direct bundle=gmem2 depth=10
#pragma HLS INTERFACE m_axi port=feature_out offset=direct bundle=gmem3 depth=10
#pragma HLS INTERFACE ap_ctrl_hs port=return

    lenet::dense<lenet::FC2_IN_ELEMS, lenet::FC2_OUT_ELEMS>(
        feature_in, weight, bias, feature_out);
}

extern "C" void lenet_full_top(
    const lenet::data_t feature_in[lenet::INPUT_ELEMS],
    const lenet::weight_t weight[lenet::TOTAL_WEIGHT_ELEMS],
    const lenet::weight_t bias[lenet::TOTAL_BIAS_ELEMS],
    lenet::data_t feature_out[lenet::FC2_OUT_ELEMS]) {
#pragma HLS INTERFACE m_axi port=feature_in offset=direct bundle=gmem0 depth=1024
#pragma HLS INTERFACE m_axi port=weight offset=direct bundle=gmem1 depth=61470
#pragma HLS INTERFACE m_axi port=bias offset=direct bundle=gmem2 depth=236
#pragma HLS INTERFACE m_axi port=feature_out offset=direct bundle=gmem3 depth=10
#pragma HLS INTERFACE ap_ctrl_hs port=return

    lenet::data_t conv1_output[lenet::CONV1_OUT_ELEMS];
    lenet::data_t pool1_output[lenet::POOL1_OUT_ELEMS];
    lenet::data_t conv2_output[lenet::CONV2_OUT_ELEMS];
    lenet::data_t pool2_output[lenet::POOL2_OUT_ELEMS];
    lenet::data_t conv3_output[lenet::CONV3_OUT_ELEMS];
    lenet::data_t conv3_relu[lenet::CONV3_OUT_ELEMS];
    lenet::data_t fc1_output[lenet::FC1_OUT_ELEMS];
    lenet::data_t fc1_relu[lenet::FC1_OUT_ELEMS];

    lenet::conv5x5_valid<
        lenet::INPUT_C, lenet::INPUT_H, lenet::INPUT_W, lenet::CONV1_OUT_C>(
        feature_in,
        &weight[lenet::CONV1_WEIGHT_OFFSET],
        &bias[lenet::CONV1_BIAS_OFFSET],
        conv1_output);
    lenet::relu_maxpool_2x2<
        lenet::CONV1_OUT_C, lenet::CONV1_OUT_H, lenet::CONV1_OUT_W>(
        conv1_output, pool1_output);

    lenet::conv5x5_valid<
        lenet::POOL1_OUT_C,
        lenet::POOL1_OUT_H,
        lenet::POOL1_OUT_W,
        lenet::CONV2_OUT_C>(
        pool1_output,
        &weight[lenet::CONV2_WEIGHT_OFFSET],
        &bias[lenet::CONV2_BIAS_OFFSET],
        conv2_output);
    lenet::relu_maxpool_2x2<
        lenet::CONV2_OUT_C, lenet::CONV2_OUT_H, lenet::CONV2_OUT_W>(
        conv2_output, pool2_output);

    lenet::conv5x5_valid<
        lenet::POOL2_OUT_C,
        lenet::POOL2_OUT_H,
        lenet::POOL2_OUT_W,
        lenet::CONV3_OUT_C>(
        pool2_output,
        &weight[lenet::CONV3_WEIGHT_OFFSET],
        &bias[lenet::CONV3_BIAS_OFFSET],
        conv3_output);
    lenet::relu_vector<lenet::CONV3_OUT_ELEMS>(conv3_output, conv3_relu);

    lenet::dense<lenet::FC1_IN_ELEMS, lenet::FC1_OUT_ELEMS>(
        conv3_relu,
        &weight[lenet::FC1_WEIGHT_OFFSET],
        &bias[lenet::FC1_BIAS_OFFSET],
        fc1_output);
    lenet::relu_vector<lenet::FC1_OUT_ELEMS>(fc1_output, fc1_relu);

    lenet::dense<lenet::FC2_IN_ELEMS, lenet::FC2_OUT_ELEMS>(
        fc1_relu,
        &weight[lenet::FC2_WEIGHT_OFFSET],
        &bias[lenet::FC2_BIAS_OFFSET],
        feature_out);
}
