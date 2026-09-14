#include "lenet_w4a4.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

using lenet_w4a4::accum_t;
using lenet_w4a4::packed_t;

const double kInputScale = 0.4030695302145822;
const double kMnistMean = 0.1307;
const double kMnistStd = 0.3081;

std::vector<double> read_numbers(const std::string& path) {
    std::ifstream input(path.c_str());
    if (!input) throw std::runtime_error("cannot open: " + path);
    std::vector<double> values;
    double value = 0.0;
    while (input >> value) values.push_back(value);
    if (!input.eof()) throw std::runtime_error("invalid number in: " + path);
    return values;
}

int quantize_int4(double value) {
    long result = std::lrint(value);
    return static_cast<int>(std::max(-7L, std::min(7L, result)));
}

packed_t pack_pair(int low, int high) {
    unsigned low_nibble = static_cast<unsigned>(low) & 0x0fU;
    unsigned high_nibble = static_cast<unsigned>(high) & 0x0fU;
    return packed_t(low_nibble | (high_nibble << 4));
}

void load_input(const std::string& path,
                packed_t output[lenet_w4a4::INPUT_PACKED_ELEMS]) {
    std::vector<double> raw = read_numbers(path);
    if (raw.size() != lenet_w4a4::INPUT_ELEMS) {
        std::ostringstream message;
        message << "input count mismatch in " << path << ": expected "
                << lenet_w4a4::INPUT_ELEMS << ", got " << raw.size();
        throw std::runtime_error(message.str());
    }
    for (int byte = 0; byte < lenet_w4a4::INPUT_PACKED_ELEMS; ++byte) {
        int i = byte * 2;
        int q0 = quantize_int4(((raw[i] / 255.0) - kMnistMean) /
                               kMnistStd / kInputScale);
        int q1 = quantize_int4(((raw[i + 1] / 255.0) - kMnistMean) /
                               kMnistStd / kInputScale);
        output[byte] = pack_pair(q0, q1);
    }
}

void load_weights(const std::string& root,
                  packed_t output[lenet_w4a4::TOTAL_WEIGHT_PACKED_ELEMS]) {
    const char* names[] = {"conv1", "conv2", "conv3", "fc1", "fc2"};
    const int expected[] = {150, 2400, 48000, 10080, 840};
    std::vector<int> all;
    all.reserve(lenet_w4a4::TOTAL_WEIGHT_ELEMS);
    for (int layer = 0; layer < 5; ++layer) {
        std::string path = root + "/" + names[layer] + ".weight.int4.txt";
        std::vector<double> values = read_numbers(path);
        if (static_cast<int>(values.size()) != expected[layer]) {
            throw std::runtime_error("weight count mismatch in: " + path);
        }
        for (std::size_t i = 0; i < values.size(); ++i) {
            int q = static_cast<int>(values[i]);
            if (values[i] != q || q < -7 || q > 7) {
                throw std::runtime_error("invalid INT4 weight in: " + path);
            }
            all.push_back(q);
        }
    }
    for (int byte = 0; byte < lenet_w4a4::TOTAL_WEIGHT_PACKED_ELEMS; ++byte) {
        output[byte] = pack_pair(all[byte * 2], all[byte * 2 + 1]);
    }
}

int run_one(const std::string& input_path, const packed_t weights[], int expected) {
    packed_t input[lenet_w4a4::INPUT_PACKED_ELEMS];
    accum_t logits[lenet_w4a4::FC2_OUT_ELEMS];
    load_input(input_path, input);
    lenet_w4a4_top(input, weights, logits);

    int prediction = 0;
    std::cout << input_path << " logits:";
    for (int i = 0; i < lenet_w4a4::FC2_OUT_ELEMS; ++i) {
        std::cout << ' ' << logits[i].to_int();
        if (logits[i] > logits[prediction]) prediction = i;
    }
    std::cout << " | prediction=" << prediction << " expected=" << expected;
    bool pass = prediction == expected;
    std::cout << (pass ? " [PASS]" : " [FAIL]") << std::endl;
    return pass ? 0 : 1;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc < 3) {
            std::cerr << "usage: tb_lenet_w4a4 <model_root> <weight_root> [--multi]"
                      << std::endl;
            return 2;
        }
        const std::string model_root = argv[1];
        const std::string weight_root = argv[2];
        packed_t weights[lenet_w4a4::TOTAL_WEIGHT_PACKED_ELEMS];
        load_weights(weight_root, weights);

        int failures = 0;
        if (argc >= 4 && std::string(argv[3]) == "--multi") {
            const int labels[10] = {7, 2, 1, 0, 4, 1, 4, 9, 5, 9};
            failures += run_one(model_root + "/input_raw.txt", weights, 7);
            for (int i = 0; i < 10; ++i) {
                std::ostringstream path;
                path << model_root << "/benchmark_samples/input_"
                     << std::setfill('0') << std::setw(2) << i
                     << "_label_" << labels[i] << ".txt";
                failures += run_one(path.str(), weights, labels[i]);
            }
        } else {
            failures += run_one(model_root + "/input_raw.txt", weights, 7);
        }
        std::cout << "W4A4_CSIM_SUMMARY: " << (failures == 0 ? "PASS" : "FAIL")
                  << " failures=" << failures << std::endl;
        return failures == 0 ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "W4A4_CSIM_ERROR: " << error.what() << std::endl;
        return 2;
    }
}
