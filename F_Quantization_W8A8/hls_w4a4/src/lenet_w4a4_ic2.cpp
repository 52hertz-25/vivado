#include "lenet_w4a4.h"

namespace lenet_w4a4 {
namespace {

act_t unpack_int4(const packed_t data[], int index) {
#pragma HLS INLINE
    const packed_t byte = data[index >> 1];

    ap_uint<4> nibble;

    if (index & 1) {
        nibble = byte.range(7, 4);
    } else {
        nibble = byte.range(3, 0);
    }

    return act_t(nibble);
}


act_t round_scale_and_saturate(
    accum_t value,
    unsigned long long multiplier_q40,
    bool relu
) {
#pragma HLS INLINE

    if (relu && value <= 0) {
        return act_t(0);
    }

    const bool negative = value < 0;

    ap_uint<32> magnitude;

    if (negative) {
        ap_int<33> extended_value = value;
        magnitude = ap_uint<32>(-extended_value);
    } else {
        magnitude = ap_uint<32>(value);
    }

    ap_uint<80> product =
        ap_uint<80>(magnitude) *
        ap_uint<48>(multiplier_q40);

    ap_uint<40> quotient =
        ap_uint<40>(product >> REQUANT_SHIFT);

    const ap_uint<80> mask =
        (ap_uint<80>(1) << REQUANT_SHIFT) - 1;

    const ap_uint<80> remainder =
        product & mask;

    const ap_uint<80> half =
        ap_uint<80>(1) << (REQUANT_SHIFT - 1);

    // Round to nearest, ties to even.
    // This matches torch.round().
    if (
        remainder > half ||
        (remainder == half && quotient[0] == 1)
    ) {
        quotient++;
    }

    // Do not use a ternary expression here.
    // Vitis HLS 2022.2 widens unary minus from
    // ap_int<42> to ap_int<43>.
    ap_int<42> rounded =
        ap_int<42>(quotient);

    if (negative) {
        rounded = -rounded;
    }

    if (relu && rounded < 0) {
        rounded = 0;
    }

    if (rounded > QMAX) {
        rounded = QMAX;
    }

    if (rounded < QMIN) {
        rounded = QMIN;
    }

    return act_t(rounded);
}


template <
    int IN_C,
    int IN_H,
    int IN_W,
    int OUT_C
>
void conv5x5_accumulate(
    const act_t feature_in[
        IN_C * IN_H * IN_W
    ],

    const packed_t packed_weight[
        TOTAL_WEIGHT_PACKED_ELEMS
    ],

    int weight_offset,

    accum_t feature_out[
        OUT_C *
        (IN_H - 4) *
        (IN_W - 4)
    ]
) {
    const int out_h =
        IN_H - KERNEL_SIZE + 1;

    const int out_w =
        IN_W - KERNEL_SIZE + 1;

OUT_CHANNEL:
    for (int oc = 0; oc < OUT_C; ++oc) {

    OUT_ROW:
        for (int oh = 0; oh < out_h; ++oh) {

        OUT_COL:
            for (int ow = 0; ow < out_w; ++ow) {

                accum_t accumulator = 0;

            IN_CHANNEL:
                #pragma HLS UNROLL factor=2
                for (int ic = 0; ic < IN_C; ++ic) {

                KERNEL_ROW:
                    for (
                        int kh = 0;
                        kh < KERNEL_SIZE;
                        ++kh
                    ) {

                    KERNEL_COL:
                        for (
                            int kw = 0;
                            kw < KERNEL_SIZE;
                            ++kw
                        ) {
                            const int input_index =
                                (
                                    ic * IN_H +
                                    oh + kh
                                ) * IN_W +
                                ow + kw;

                            const int local_weight_index =
                                (
                                    (
                                        oc * IN_C +
                                        ic
                                    ) * KERNEL_SIZE +
                                    kh
                                ) * KERNEL_SIZE +
                                kw;

                            const weight_t weight_value =
                                unpack_int4(
                                    packed_weight,
                                    weight_offset +
                                    local_weight_index
                                );

                            accumulator +=
                                accum_t(
                                    feature_in[input_index]
                                ) *
                                accum_t(weight_value);
                        }
                    }
                }

                const int output_index =
                    (
                        oc * out_h +
                        oh
                    ) * out_w +
                    ow;

                feature_out[output_index] =
                    accumulator;
            }
        }
    }
}


template <
    int CHANNELS,
    int H,
    int W
>
void requant_relu_pool2x2(
    const accum_t feature_in[
        CHANNELS * H * W
    ],

    act_t feature_out[
        CHANNELS *
        (H / 2) *
        (W / 2)
    ],

    unsigned long long multiplier_q40
) {
    const int out_h = H / 2;
    const int out_w = W / 2;

POOL_CHANNEL:
    for (int channel = 0;
         channel < CHANNELS;
         ++channel) {

    POOL_ROW:
        for (int output_row = 0;
             output_row < out_h;
             ++output_row) {

        POOL_COL:
            for (int output_col = 0;
                 output_col < out_w;
                 ++output_col) {

                act_t maximum = 0;

            POOL_KERNEL_ROW:
                for (int kernel_row = 0;
                     kernel_row < 2;
                     ++kernel_row) {

                POOL_KERNEL_COL:
                    for (int kernel_col = 0;
                         kernel_col < 2;
                         ++kernel_col) {

                        const int input_row =
                            output_row * 2 +
                            kernel_row;

                        const int input_col =
                            output_col * 2 +
                            kernel_col;

                        const int input_index =
                            (
                                channel * H +
                                input_row
                            ) * W +
                            input_col;

                        const act_t value =
                            round_scale_and_saturate(
                                feature_in[input_index],
                                multiplier_q40,
                                true
                            );

                        if (value > maximum) {
                            maximum = value;
                        }
                    }
                }

                const int output_index =
                    (
                        channel * out_h +
                        output_row
                    ) * out_w +
                    output_col;

                feature_out[output_index] =
                    maximum;
            }
        }
    }
}


template <int ELEMENTS>
void requant_vector(
    const accum_t feature_in[ELEMENTS],
    act_t feature_out[ELEMENTS],
    unsigned long long multiplier_q40,
    bool relu
) {

REQUANT_VECTOR:
    for (int index = 0;
         index < ELEMENTS;
         ++index) {

        feature_out[index] =
            round_scale_and_saturate(
                feature_in[index],
                multiplier_q40,
                relu
            );
    }
}


template <
    int IN_ELEMS,
    int OUT_ELEMS
>
void dense_accumulate(
    const act_t feature_in[IN_ELEMS],

    const packed_t packed_weight[
        TOTAL_WEIGHT_PACKED_ELEMS
    ],

    int weight_offset,

    accum_t feature_out[OUT_ELEMS]
) {

DENSE_OUTPUT:
    for (
        int output_index = 0;
        output_index < OUT_ELEMS;
        ++output_index
    ) {
        accum_t accumulator = 0;

    DENSE_INPUT:
        for (
            int input_index = 0;
            input_index < IN_ELEMS;
            ++input_index
        ) {
            const int local_weight_index =
                output_index *
                IN_ELEMS +
                input_index;

            const weight_t weight_value =
                unpack_int4(
                    packed_weight,
                    weight_offset +
                    local_weight_index
                );

            accumulator +=
                accum_t(feature_in[input_index]) *
                accum_t(weight_value);
        }

        feature_out[output_index] =
            accumulator;
    }
}

}  // namespace
}  // namespace lenet_w4a4


extern "C" void lenet_w4a4_top(
    const lenet_w4a4::packed_t feature_in[
        lenet_w4a4::INPUT_PACKED_ELEMS
    ],

    const lenet_w4a4::packed_t weight[
        lenet_w4a4::TOTAL_WEIGHT_PACKED_ELEMS
    ],

    lenet_w4a4::accum_t logits[
        lenet_w4a4::FC2_OUT_ELEMS
    ]
) {
#pragma HLS INTERFACE m_axi port=feature_in offset=slave bundle=gmem0 depth=512
#pragma HLS INTERFACE m_axi port=weight offset=slave bundle=gmem1 depth=30735
#pragma HLS INTERFACE m_axi port=logits offset=slave bundle=gmem2 depth=10

#pragma HLS INTERFACE s_axilite port=feature_in bundle=control
#pragma HLS INTERFACE s_axilite port=weight bundle=control
#pragma HLS INTERFACE s_axilite port=logits bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

    using namespace lenet_w4a4;

    act_t input[INPUT_ELEMS];

    accum_t conv1_acc[
        CONV1_OUT_ELEMS
    ];

    act_t pool1[
        POOL1_OUT_ELEMS
    ];

    accum_t conv2_acc[
        CONV2_OUT_ELEMS
    ];

    act_t pool2[
        POOL2_OUT_ELEMS
    ];

    accum_t conv3_acc[
        CONV3_OUT_ELEMS
    ];

    act_t conv3_relu[
        CONV3_OUT_ELEMS
    ];

    accum_t fc1_acc[
        FC1_OUT_ELEMS
    ];

    act_t fc1_relu[
        FC1_OUT_ELEMS
    ];

    accum_t fc2_acc[
        FC2_OUT_ELEMS
    ];

    act_t fc2_quant[
        FC2_OUT_ELEMS
    ];


UNPACK_INPUT:
    for (
        int index = 0;
        index < INPUT_ELEMS;
        ++index
    ) {
        input[index] =
            unpack_int4(
                feature_in,
                index
            );
    }


    conv5x5_accumulate<
        INPUT_C,
        INPUT_H,
        INPUT_W,
        CONV1_OUT_C
    >(
        input,
        weight,
        CONV1_WEIGHT_OFFSET,
        conv1_acc
    );


    requant_relu_pool2x2<
        CONV1_OUT_C,
        CONV1_OUT_H,
        CONV1_OUT_W
    >(
        conv1_acc,
        pool1,
        CONV1_REQUANT_Q40
    );


    conv5x5_accumulate<
        POOL1_OUT_C,
        POOL1_OUT_H,
        POOL1_OUT_W,
        CONV2_OUT_C
    >(
        pool1,
        weight,
        CONV2_WEIGHT_OFFSET,
        conv2_acc
    );


    requant_relu_pool2x2<
        CONV2_OUT_C,
        CONV2_OUT_H,
        CONV2_OUT_W
    >(
        conv2_acc,
        pool2,
        CONV2_REQUANT_Q40
    );


    conv5x5_accumulate<
        POOL2_OUT_C,
        POOL2_OUT_H,
        POOL2_OUT_W,
        CONV3_OUT_C
    >(
        pool2,
        weight,
        CONV3_WEIGHT_OFFSET,
        conv3_acc
    );


    requant_vector<
        CONV3_OUT_ELEMS
    >(
        conv3_acc,
        conv3_relu,
        CONV3_REQUANT_Q40,
        true
    );


    dense_accumulate<
        FC1_IN_ELEMS,
        FC1_OUT_ELEMS
    >(
        conv3_relu,
        weight,
        FC1_WEIGHT_OFFSET,
        fc1_acc
    );


    requant_vector<
        FC1_OUT_ELEMS
    >(
        fc1_acc,
        fc1_relu,
        FC1_REQUANT_Q40,
        true
    );


    dense_accumulate<
        FC2_IN_ELEMS,
        FC2_OUT_ELEMS
    >(
        fc1_relu,
        weight,
        FC2_WEIGHT_OFFSET,
        fc2_acc
    );


    requant_vector<
        FC2_OUT_ELEMS
    >(
        fc2_acc,
        fc2_quant,
        FC2_REQUANT_Q40,
        false
    );


WRITE_LOGITS:
    for (
        int index = 0;
        index < FC2_OUT_ELEMS;
        ++index
    ) {
        logits[index] =
            accum_t(fc2_quant[index]);
    }
}