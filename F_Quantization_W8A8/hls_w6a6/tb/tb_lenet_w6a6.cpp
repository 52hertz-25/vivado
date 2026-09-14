#include "lenet_w6a6.h"

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

std::string join_path(const std::string &root, const std::string &relative) {
    if (root.empty()) return relative;
    const char last = root[root.size() - 1];
    return (last == '/' || last == '\\') ? root + relative : root + "/" + relative;
}

std::vector<int> load_ints(
    const std::string &path, std::size_t expected_count) {
    std::ifstream stream(path.c_str());
    if (!stream) throw std::runtime_error("Cannot open: " + path);
    std::vector<int> values;
    int value = 0;
    while (stream >> value) values.push_back(value);
    if (values.size() != expected_count) {
        throw std::runtime_error(
            "Wrong element count in " + path + ": got " +
            std::to_string(values.size()) + ", expected " +
            std::to_string(expected_count));
    }
    return values;
}

std::vector<float> load_floats(
    const std::string &path, std::size_t expected_count) {
    std::ifstream stream(path.c_str());
    if (!stream) throw std::runtime_error("Cannot open: " + path);
    std::vector<float> values;
    float value = 0.0f;
    while (stream >> value) values.push_back(value);
    if (values.size() != expected_count) {
        throw std::runtime_error(
            "Wrong element count in " + path + ": got " +
            std::to_string(values.size()) + ", expected " +
            std::to_string(expected_count));
    }
    return values;
}

std::vector<lenet_w6a6::act_t> load_quantized_input(const std::string &path) {
    const double mean = 0.1307;
    const double stddev = 0.3081;
    const double input_scale = 2.821486711502075 / 31.0;
    const std::vector<float> raw =
        load_floats(path, lenet_w6a6::INPUT_ELEMS);
    std::vector<lenet_w6a6::act_t> result(raw.size());
    for (std::size_t i = 0; i < raw.size(); ++i) {
        const double normalized = (raw[i] / 255.0 - mean) / stddev;
        long quantized = static_cast<long>(std::nearbyint(normalized / input_scale));
        quantized = std::max(-31L, std::min(31L, quantized));
        result[i] = static_cast<int>(quantized);
    }
    return result;
}

void append_weight(
    const std::string &weight_root,
    const std::string &name,
    std::size_t count,
    std::size_t offset,
    std::vector<lenet_w6a6::weight_t> *all_weight) {
    const std::vector<int> values = load_ints(
        join_path(weight_root, name + ".weight.int6.txt"), count);
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (values[i] < -31 || values[i] > 31) {
            throw std::runtime_error("INT6 range violation in " + name);
        }
        (*all_weight)[offset + i] = values[i];
    }
}

std::vector<lenet_w6a6::weight_t> load_all_weights(
    const std::string &weight_root) {
    using namespace lenet_w6a6;
    std::vector<weight_t> result(TOTAL_WEIGHT_ELEMS);
    append_weight(weight_root, "conv1", CONV1_WEIGHT_ELEMS,
                  CONV1_WEIGHT_OFFSET, &result);
    append_weight(weight_root, "conv2", CONV2_WEIGHT_ELEMS,
                  CONV2_WEIGHT_OFFSET, &result);
    append_weight(weight_root, "conv3", CONV3_WEIGHT_ELEMS,
                  CONV3_WEIGHT_OFFSET, &result);
    append_weight(weight_root, "fc1", FC1_WEIGHT_ELEMS,
                  FC1_WEIGHT_OFFSET, &result);
    append_weight(weight_root, "fc2", FC2_WEIGHT_ELEMS,
                  FC2_WEIGHT_OFFSET, &result);
    return result;
}

int run_sample(
    const std::string &input_path,
    int expected_label,
    const std::vector<lenet_w6a6::weight_t> &weight,
    const std::string &name) {
    using namespace lenet_w6a6;
    const std::vector<act_t> input = load_quantized_input(input_path);
    std::vector<accum_t> logits(FC2_OUT_ELEMS);
    lenet_w6a6_top(input.data(), weight.data(), logits.data());

    int predicted = 0;
    for (int i = 1; i < FC2_OUT_ELEMS; ++i) {
        if (logits[i] > logits[predicted]) predicted = i;
    }

    // Final dequantization scale = fc1_relu scale * fc2 weight scale.
    const double output_scale = 0.007349259080958317;
    std::cout << name << " logits (INT32 / dequantized):\n";
    for (int i = 0; i < FC2_OUT_ELEMS; ++i) {
        std::cout << "  [" << i << "] " << logits[i].to_int()
                  << " / " << std::fixed << std::setprecision(6)
                  << logits[i].to_int() * output_scale << "\n";
    }
    const bool passed = predicted == expected_label;
    std::cout << name << " predicted=" << predicted
              << " expected=" << expected_label
              << " [" << (passed ? "PASS" : "FAIL") << "]\n";
    return passed ? 0 : 1;
}

}  // namespace

int main(int argc, char **argv) {
    try {
        if (argc < 3) {
            std::cerr << "Usage: tb_lenet_w6a6 <model_root> <int6_weight_root> [--multi]\n";
            return 2;
        }
        const std::string model_root = argv[1];
        const std::string weight_root = argv[2];
        const bool multi = argc >= 4 && std::string(argv[3]) == "--multi";
        const std::vector<lenet_w6a6::weight_t> weight =
            load_all_weights(weight_root);

        int failures = run_sample(
            join_path(model_root, "input_raw.txt"), 7, weight, "sample_00");

        if (multi) {
            const int labels[10] = {7, 2, 1, 0, 4, 1, 4, 9, 5, 9};
            for (int sample = 0; sample < 10; ++sample) {
                std::ostringstream filename;
                filename << "benchmark_samples/input_" << std::setfill('0')
                         << std::setw(2) << sample << "_label_"
                         << labels[sample] << ".txt";
                std::ostringstream name;
                name << "sample_" << std::setfill('0') << std::setw(2) << sample;
                failures += run_sample(
                    join_path(model_root, filename.str()),
                    labels[sample], weight, name.str());
            }
        }

        std::cout << "\nW6A6 C-simulation result: "
                  << (failures == 0 ? "PASS" : "FAIL") << "\n";
        return failures == 0 ? 0 : 1;
    } catch (const std::exception &error) {
        std::cerr << "Testbench error: " << error.what() << "\n";
        return 2;
    }
}
