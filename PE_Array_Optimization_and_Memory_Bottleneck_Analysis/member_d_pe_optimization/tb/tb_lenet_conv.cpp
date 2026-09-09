#include "lenet_conv.h"
#include "npy_reader.h"

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
    if (root.empty()) {
        return relative;
    }
    const char last = root[root.size() - 1];
    if (last == '/' || last == '\\') {
        return root + relative;
    }
    return root + "/" + relative;
}

std::vector<float> load_text_floats(
    const std::string &path,
    std::size_t expected_count) {
    std::ifstream stream(path.c_str());
    if (!stream) {
        throw std::runtime_error("Cannot open text data: " + path);
    }

    std::vector<float> values;
    float value = 0.0f;
    while (stream >> value) {
        values.push_back(value);
    }
    if (values.size() != expected_count) {
        throw std::runtime_error(
            "Unexpected element count in " + path + ": got " +
            std::to_string(values.size()) + ", expected " +
            std::to_string(expected_count));
    }
    return values;
}

std::vector<float> load_preprocessed_input(const std::string &path) {
    std::vector<float> input = load_text_floats(path, lenet::INPUT_ELEMS);
    for (std::size_t index = 0; index < input.size(); ++index) {
        input[index] = (input[index] / 255.0f - 0.1307f) / 0.3081f;
    }
    return input;
}

std::vector<float> zero_bias(std::size_t count) {
    return std::vector<float>(count, 0.0f);
}

std::vector<float> relu_copy(const std::vector<float> &input) {
    std::vector<float> output(input.size());
    for (std::size_t index = 0; index < input.size(); ++index) {
        output[index] = input[index] > 0.0f ? input[index] : 0.0f;
    }
    return output;
}

int argmax(const std::vector<float> &values) {
    if (values.empty()) {
        throw std::runtime_error("Cannot calculate argmax of empty vector");
    }
    return static_cast<int>(
        std::max_element(values.begin(), values.end()) - values.begin());
}

struct ErrorMetrics {
    double max_abs_error;
    double mean_abs_error;
    double rmse;
    std::size_t max_error_index;
    bool passed;
};

ErrorMetrics compare_values(
    const std::string &name,
    const std::vector<float> &actual,
    const std::vector<float> &expected,
    double max_abs_tolerance) {
    if (actual.size() != expected.size()) {
        throw std::runtime_error("Size mismatch while comparing " + name);
    }

    double max_abs_error = 0.0;
    double absolute_error_sum = 0.0;
    double squared_error_sum = 0.0;
    std::size_t max_error_index = 0;
    for (std::size_t index = 0; index < actual.size(); ++index) {
        const double error =
            static_cast<double>(actual[index]) - static_cast<double>(expected[index]);
        const double absolute_error = std::fabs(error);
        absolute_error_sum += absolute_error;
        squared_error_sum += error * error;
        if (absolute_error > max_abs_error) {
            max_abs_error = absolute_error;
            max_error_index = index;
        }
    }

    ErrorMetrics metrics;
    metrics.max_abs_error = max_abs_error;
    metrics.mean_abs_error = absolute_error_sum / actual.size();
    metrics.rmse = std::sqrt(squared_error_sum / actual.size());
    metrics.max_error_index = max_error_index;
    metrics.passed = max_abs_error <= max_abs_tolerance;

    std::cout << std::left << std::setw(24) << name
              << " max_abs=" << std::scientific << std::setprecision(8)
              << metrics.max_abs_error
              << " mean_abs=" << metrics.mean_abs_error
              << " rmse=" << metrics.rmse
              << " tolerance=" << max_abs_tolerance
              << " max_index=" << metrics.max_error_index
              << " [" << (metrics.passed ? "PASS" : "FAIL") << "]\n";
    return metrics;
}

void require_shape(
    const std::string &name,
    const NpyFloatArray &array,
    const std::vector<std::size_t> &expected_shape) {
    if (array.shape != expected_shape) {
        throw std::runtime_error("Unexpected shape for " + name);
    }
}

std::vector<float> load_weight(
    const std::string &model_root,
    const std::string &name,
    std::size_t count) {
    return load_text_floats(
        join_path(model_root, "hw_weights/" + name + ".weight.txt"), count);
}

NpyFloatArray load_feature_map(
    const std::string &model_root,
    const std::string &name) {
    return load_npy_float32(
        join_path(model_root, "hw_feature_maps/" + name + ".npy"));
}

bool run_conv1_checks(
    const std::string &model_root,
    std::vector<float> *pool1_for_downstream) {
    const std::vector<float> input = load_preprocessed_input(
        join_path(model_root, "input_raw.txt"));
    const std::vector<float> weight = load_weight(
        model_root, "conv1", lenet::CONV1_WEIGHT_ELEMS);
    const std::vector<float> bias = zero_bias(lenet::CONV1_BIAS_ELEMS);
    const NpyFloatArray golden_conv1 = load_feature_map(model_root, "conv1");
    const NpyFloatArray golden_pool1 = load_feature_map(model_root, "pool1");

    require_shape("conv1", golden_conv1, {1, 6, 28, 28});
    require_shape("pool1", golden_pool1, {1, 6, 14, 14});

    std::vector<float> conv1_output(lenet::CONV1_OUT_ELEMS);
    std::vector<float> pool1_output(lenet::POOL1_OUT_ELEMS);
    lenet_conv1_top(
        input.data(), weight.data(), bias.data(), conv1_output.data());
    lenet::lenet_relu_pool1(conv1_output.data(), pool1_output.data());

    bool passed = true;
    passed &= compare_values(
        "Conv1 raw", conv1_output, golden_conv1.data, 2.0e-5).passed;
    passed &= compare_values(
        "ReLU+Pool1", pool1_output, golden_pool1.data, 2.0e-5).passed;
    if (pool1_for_downstream != 0) {
        *pool1_for_downstream = pool1_output;
    }
    return passed;
}

bool run_conv2_checks(
    const std::string &model_root,
    const std::vector<float> *pool1_from_conv1,
    std::vector<float> *pool2_for_downstream) {
    const std::vector<float> weight = load_weight(
        model_root, "conv2", lenet::CONV2_WEIGHT_ELEMS);
    const std::vector<float> bias = zero_bias(lenet::CONV2_BIAS_ELEMS);
    const NpyFloatArray golden_pool1 = load_feature_map(model_root, "pool1");
    const NpyFloatArray golden_conv2 = load_feature_map(model_root, "conv2");
    const NpyFloatArray golden_pool2 = load_feature_map(model_root, "pool2");

    require_shape("pool1", golden_pool1, {1, 6, 14, 14});
    require_shape("conv2", golden_conv2, {1, 16, 10, 10});
    require_shape("pool2", golden_pool2, {1, 16, 5, 5});

    std::vector<float> isolated_output(lenet::CONV2_OUT_ELEMS);
    lenet_conv2_top(
        golden_pool1.data.data(), weight.data(), bias.data(), isolated_output.data());

    bool passed = compare_values(
        "Conv2 isolated", isolated_output, golden_conv2.data, 5.0e-3).passed;

    const std::vector<float> *raw_for_pool = &isolated_output;
    std::vector<float> end_to_end_output;
    if (pool1_from_conv1 != 0) {
        end_to_end_output.resize(lenet::CONV2_OUT_ELEMS);
        lenet_conv2_top(
            pool1_from_conv1->data(),
            weight.data(),
            bias.data(),
            end_to_end_output.data());
        passed &= compare_values(
            "Conv2 chained", end_to_end_output, golden_conv2.data, 5.0e-3).passed;
        raw_for_pool = &end_to_end_output;
    }

    std::vector<float> pool2_output(lenet::POOL2_OUT_ELEMS);
    lenet::lenet_relu_pool2(raw_for_pool->data(), pool2_output.data());
    passed &= compare_values(
        "ReLU+Pool2", pool2_output, golden_pool2.data, 5.0e-3).passed;
    if (pool2_for_downstream != 0) {
        *pool2_for_downstream = pool2_output;
    }
    return passed;
}

bool run_conv3_checks(
    const std::string &model_root,
    const std::vector<float> *pool2_from_conv2,
    std::vector<float> *relu_for_downstream) {
    const std::vector<float> weight = load_weight(
        model_root, "conv3", lenet::CONV3_WEIGHT_ELEMS);
    const std::vector<float> bias = zero_bias(lenet::CONV3_BIAS_ELEMS);
    const NpyFloatArray golden_pool2 = load_feature_map(model_root, "pool2");
    const NpyFloatArray golden_conv3 = load_feature_map(model_root, "conv3");

    require_shape("pool2", golden_pool2, {1, 16, 5, 5});
    require_shape("conv3", golden_conv3, {1, 120, 1, 1});

    std::vector<float> isolated_output(lenet::CONV3_OUT_ELEMS);
    lenet_conv3_top(
        golden_pool2.data.data(), weight.data(), bias.data(), isolated_output.data());
    bool passed = compare_values(
        "Conv3 isolated", isolated_output, golden_conv3.data, 1.0e-2).passed;

    const std::vector<float> *raw_for_relu = &isolated_output;
    std::vector<float> chained_output;
    if (pool2_from_conv2 != 0) {
        chained_output.resize(lenet::CONV3_OUT_ELEMS);
        lenet_conv3_top(
            pool2_from_conv2->data(),
            weight.data(),
            bias.data(),
            chained_output.data());
        passed &= compare_values(
            "Conv3 chained", chained_output, golden_conv3.data, 1.0e-2).passed;
        raw_for_relu = &chained_output;
    }

    std::vector<float> relu_output(lenet::CONV3_OUT_ELEMS);
    lenet::lenet_relu_conv3(raw_for_relu->data(), relu_output.data());
    if (relu_for_downstream != 0) {
        *relu_for_downstream = relu_output;
    }
    return passed;
}

bool run_fc1_checks(
    const std::string &model_root,
    const std::vector<float> *conv3_relu_from_chain,
    std::vector<float> *relu_for_downstream) {
    const std::vector<float> weight = load_weight(
        model_root, "fc1", lenet::FC1_WEIGHT_ELEMS);
    const std::vector<float> bias = zero_bias(lenet::FC1_BIAS_ELEMS);
    const NpyFloatArray golden_conv3 = load_feature_map(model_root, "conv3");
    const NpyFloatArray golden_fc1 = load_feature_map(model_root, "fc1");
    require_shape("conv3", golden_conv3, {1, 120, 1, 1});
    require_shape("fc1", golden_fc1, {1, 84});

    const std::vector<float> golden_conv3_relu = relu_copy(golden_conv3.data);
    std::vector<float> isolated_output(lenet::FC1_OUT_ELEMS);
    lenet_fc1_top(
        golden_conv3_relu.data(), weight.data(), bias.data(), isolated_output.data());
    bool passed = compare_values(
        "FC1 isolated", isolated_output, golden_fc1.data, 1.0e-2).passed;

    const std::vector<float> *raw_for_relu = &isolated_output;
    std::vector<float> chained_output;
    if (conv3_relu_from_chain != 0) {
        chained_output.resize(lenet::FC1_OUT_ELEMS);
        lenet_fc1_top(
            conv3_relu_from_chain->data(),
            weight.data(),
            bias.data(),
            chained_output.data());
        passed &= compare_values(
            "FC1 chained", chained_output, golden_fc1.data, 1.0e-2).passed;
        raw_for_relu = &chained_output;
    }

    std::vector<float> relu_output = relu_copy(*raw_for_relu);
    if (relu_for_downstream != 0) {
        *relu_for_downstream = relu_output;
    }
    return passed;
}

bool run_fc2_checks(
    const std::string &model_root,
    const std::vector<float> *fc1_relu_from_chain,
    std::vector<float> *logits_for_downstream) {
    const std::vector<float> weight = load_weight(
        model_root, "fc2", lenet::FC2_WEIGHT_ELEMS);
    const std::vector<float> bias = zero_bias(lenet::FC2_BIAS_ELEMS);
    const NpyFloatArray golden_fc1 = load_feature_map(model_root, "fc1");
    const NpyFloatArray golden_fc2 = load_feature_map(model_root, "fc2");
    require_shape("fc1", golden_fc1, {1, 84});
    require_shape("fc2", golden_fc2, {1, 10});

    const std::vector<float> golden_fc1_relu = relu_copy(golden_fc1.data);
    std::vector<float> isolated_output(lenet::FC2_OUT_ELEMS);
    lenet_fc2_top(
        golden_fc1_relu.data(), weight.data(), bias.data(), isolated_output.data());
    bool passed = compare_values(
        "FC2 isolated", isolated_output, golden_fc2.data, 1.0e-2).passed;

    const std::vector<float> *logits = &isolated_output;
    std::vector<float> chained_output;
    if (fc1_relu_from_chain != 0) {
        chained_output.resize(lenet::FC2_OUT_ELEMS);
        lenet_fc2_top(
            fc1_relu_from_chain->data(),
            weight.data(),
            bias.data(),
            chained_output.data());
        passed &= compare_values(
            "FC2 chained", chained_output, golden_fc2.data, 1.0e-2).passed;
        logits = &chained_output;
    }

    if (logits_for_downstream != 0) {
        *logits_for_downstream = *logits;
    }
    return passed;
}

std::vector<float> load_all_weights(const std::string &model_root) {
    std::vector<float> all_weight(lenet::TOTAL_WEIGHT_ELEMS);
    const std::vector<float> conv1 = load_weight(
        model_root, "conv1", lenet::CONV1_WEIGHT_ELEMS);
    const std::vector<float> conv2 = load_weight(
        model_root, "conv2", lenet::CONV2_WEIGHT_ELEMS);
    const std::vector<float> conv3 = load_weight(
        model_root, "conv3", lenet::CONV3_WEIGHT_ELEMS);
    const std::vector<float> fc1 = load_weight(
        model_root, "fc1", lenet::FC1_WEIGHT_ELEMS);
    const std::vector<float> fc2 = load_weight(
        model_root, "fc2", lenet::FC2_WEIGHT_ELEMS);
    std::copy(conv1.begin(), conv1.end(), all_weight.begin() + lenet::CONV1_WEIGHT_OFFSET);
    std::copy(conv2.begin(), conv2.end(), all_weight.begin() + lenet::CONV2_WEIGHT_OFFSET);
    std::copy(conv3.begin(), conv3.end(), all_weight.begin() + lenet::CONV3_WEIGHT_OFFSET);
    std::copy(fc1.begin(), fc1.end(), all_weight.begin() + lenet::FC1_WEIGHT_OFFSET);
    std::copy(fc2.begin(), fc2.end(), all_weight.begin() + lenet::FC2_WEIGHT_OFFSET);
    return all_weight;
}

bool run_full_single(
    const std::string &name,
    const std::string &input_path,
    const std::vector<float> &expected_logits,
    int expected_label,
    const std::vector<float> &all_weight,
    const std::vector<float> &all_bias) {
    const std::vector<float> input = load_preprocessed_input(input_path);
    std::vector<float> actual_logits(lenet::FC2_OUT_ELEMS);
    lenet_full_top(
        input.data(), all_weight.data(), all_bias.data(), actual_logits.data());
    bool passed = compare_values(
        name, actual_logits, expected_logits, 1.0e-2).passed;
    const int predicted = argmax(actual_logits);
    const bool label_passed = predicted == expected_label;
    std::cout << std::defaultfloat
              << "  predicted=" << predicted
              << " expected=" << expected_label
              << " [" << (label_passed ? "PASS" : "FAIL") << "]\n";
    return passed && label_passed;
}

bool run_full_checks(const std::string &model_root, bool run_multi_sample) {
    const std::vector<float> all_weight = load_all_weights(model_root);
    const std::vector<float> all_bias = zero_bias(lenet::TOTAL_BIAS_ELEMS);
    const NpyFloatArray golden_fc2 = load_feature_map(model_root, "fc2");
    require_shape("fc2", golden_fc2, {1, 10});

    bool passed = run_full_single(
        "Full single sample",
        join_path(model_root, "input_raw.txt"),
        golden_fc2.data,
        7,
        all_weight,
        all_bias);

    if (!run_multi_sample) {
        return passed;
    }

    const int labels[10] = {7, 2, 1, 0, 4, 1, 4, 9, 5, 9};
    std::cout << "\nTen-sample end-to-end regression\n";
    for (int sample = 0; sample < 10; ++sample) {
        std::ostringstream input_name;
        std::ostringstream output_name;
        input_name << "benchmark_samples/input_" << std::setfill('0')
                   << std::setw(2) << sample << "_label_" << labels[sample] << ".txt";
        output_name << "benchmark_samples/output_" << std::setfill('0')
                    << std::setw(2) << sample << "_label_" << labels[sample] << ".txt";
        const std::vector<float> expected_logits = load_text_floats(
            join_path(model_root, output_name.str()), lenet::FC2_OUT_ELEMS);
        std::ostringstream check_name;
        check_name << "Full sample " << std::setfill('0') << std::setw(2) << sample;
        passed &= run_full_single(
            check_name.str(),
            join_path(model_root, input_name.str()),
            expected_logits,
            labels[sample],
            all_weight,
            all_bias);
    }
    return passed;
}

}  // namespace

int main(int argc, char **argv) {
    try {
        const std::string model_root = argc >= 2 ? argv[1] : "../model";
        const bool run_multi_sample = argc >= 3 && std::string(argv[2]) == "--multi";

        std::cout << "LeNet-5 model-V2 HLS verification\n";
        std::cout << "Data layout: CHW feature maps, OIHW weights\n";
        std::cout << "Input preprocessing: (pixel/255 - 0.1307) / 0.3081\n";
        std::cout << "Golden Conv/FC maps are before ReLU; all biases are zero.\n\n";

        bool all_passed = true;
#if defined(LENET_HLS_TOP_CONV1)
        std::cout << "Vivado HLS testbench mode: Conv1\n\n";
        all_passed = run_conv1_checks(model_root, 0);
#elif defined(LENET_HLS_TOP_CONV2)
        std::cout << "Vivado HLS testbench mode: Conv2\n\n";
        all_passed = run_conv2_checks(model_root, 0, 0);
#elif defined(LENET_HLS_TOP_CONV3)
        std::cout << "Vivado HLS testbench mode: Conv3\n\n";
        all_passed = run_conv3_checks(model_root, 0, 0);
#elif defined(LENET_HLS_TOP_FC1)
        std::cout << "Vivado HLS testbench mode: FC1\n\n";
        all_passed = run_fc1_checks(model_root, 0, 0);
#elif defined(LENET_HLS_TOP_FC2)
        std::cout << "Vivado HLS testbench mode: FC2\n\n";
        all_passed = run_fc2_checks(model_root, 0, 0);
#elif defined(LENET_HLS_TOP_FULL)
        std::cout << "Vivado HLS testbench mode: full network\n\n";
        all_passed = run_full_checks(model_root, false);
#else
        std::vector<float> pool1_output;
        std::vector<float> pool2_output;
        std::vector<float> conv3_relu;
        std::vector<float> fc1_relu;
        std::vector<float> logits;
        all_passed = run_conv1_checks(model_root, &pool1_output);
        all_passed &= run_conv2_checks(
            model_root, &pool1_output, &pool2_output);
        all_passed &= run_conv3_checks(
            model_root, &pool2_output, &conv3_relu);
        all_passed &= run_fc1_checks(
            model_root, &conv3_relu, &fc1_relu);
        all_passed &= run_fc2_checks(
            model_root, &fc1_relu, &logits);
        all_passed &= run_full_checks(model_root, run_multi_sample);
#endif

        std::cout << "\nOverall result: "
                  << (all_passed ? "PASS" : "FAIL") << "\n";
        return all_passed ? 0 : 1;
    } catch (const std::exception &error) {
        std::cerr << "Testbench error: " << error.what() << "\n";
        return 2;
    }
}
