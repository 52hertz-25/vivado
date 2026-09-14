#include "lenet_w6a6.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

std::string join_path(const std::string &root, const std::string &name) {
    if (root.empty()) return name;
    const char last = root[root.size() - 1];
    return (last == '/' || last == '\\') ? root + name : root + "/" + name;
}

std::vector<unsigned char> read_binary(const std::string &path) {
    std::ifstream stream(path.c_str(), std::ios::binary | std::ios::ate);
    if (!stream) throw std::runtime_error("Cannot open: " + path);
    const std::streamsize size = stream.tellg();
    if (size < 0) throw std::runtime_error("Cannot determine size: " + path);
    stream.seekg(0, std::ios::beg);
    std::vector<unsigned char> data(static_cast<std::size_t>(size));
    if (size > 0 && !stream.read(reinterpret_cast<char *>(data.data()), size)) {
        throw std::runtime_error("Cannot read: " + path);
    }
    return data;
}

std::vector<int> load_ints(const std::string &path, std::size_t expected) {
    std::ifstream stream(path.c_str());
    if (!stream) throw std::runtime_error("Cannot open: " + path);
    std::vector<int> values;
    int value = 0;
    while (stream >> value) values.push_back(value);
    if (values.size() != expected) {
        throw std::runtime_error("Wrong element count in " + path);
    }
    return values;
}

void append_weight(const std::string &root, const std::string &layer,
                   std::size_t count, std::size_t offset,
                   std::vector<lenet_w6a6::weight_t> *weights) {
    const std::vector<int> values =
        load_ints(join_path(root, layer + ".weight.int6.txt"), count);
    for (std::size_t i = 0; i < count; ++i) {
        if (values[i] < -31 || values[i] > 31) {
            throw std::runtime_error("INT6 range violation in " + layer);
        }
        (*weights)[offset + i] = values[i];
    }
}

std::vector<lenet_w6a6::weight_t> load_all_weights(const std::string &root) {
    using namespace lenet_w6a6;
    std::vector<weight_t> result(TOTAL_WEIGHT_ELEMS);
    append_weight(root, "conv1", CONV1_WEIGHT_ELEMS, CONV1_WEIGHT_OFFSET, &result);
    append_weight(root, "conv2", CONV2_WEIGHT_ELEMS, CONV2_WEIGHT_OFFSET, &result);
    append_weight(root, "conv3", CONV3_WEIGHT_ELEMS, CONV3_WEIGHT_OFFSET, &result);
    append_weight(root, "fc1", FC1_WEIGHT_ELEMS, FC1_WEIGHT_OFFSET, &result);
    append_weight(root, "fc2", FC2_WEIGHT_ELEMS, FC2_WEIGHT_OFFSET, &result);
    return result;
}

lenet_w6a6::act_t quantize_pixel(unsigned char pixel) {
    const double mean = 0.1307;
    const double stddev = 0.3081;
    const double input_scale = 2.821486711502075 / 31.0;
    const double normalized = (static_cast<double>(pixel) / 255.0 - mean) / stddev;
    long value = static_cast<long>(std::nearbyint(normalized / input_scale));
    value = std::max(-31L, std::min(31L, value));
    return static_cast<int>(value);
}

}  // namespace

int main(int argc, char **argv) {
    try {
        if (argc < 5) {
            std::cerr << "Usage: tb_lenet_w6a6_mnist <dataset_root> "
                         "<weight_root> <sample_limit> <result_csv>\n";
            return 2;
        }

        using namespace lenet_w6a6;
        const std::string dataset_root = argv[1];
        const std::string weight_root = argv[2];
        int limit = std::stoi(argv[3]);
        const std::string result_csv = argv[4];

        const std::vector<unsigned char> images =
            read_binary(join_path(dataset_root, "mnist_test_32x32.bin"));
        const std::vector<unsigned char> labels =
            read_binary(join_path(dataset_root, "mnist_test_labels.bin"));
        const std::vector<weight_t> weights = load_all_weights(weight_root);

        if (images.size() % INPUT_ELEMS != 0) {
            throw std::runtime_error("Image file size is not a multiple of 1024");
        }
        const std::size_t available = images.size() / INPUT_ELEMS;
        if (labels.size() != available) {
            throw std::runtime_error("Image and label counts do not match");
        }
        if (limit <= 0 || static_cast<std::size_t>(limit) > available) {
            limit = static_cast<int>(available);
        }

        std::vector<act_t> input(INPUT_ELEMS);
        std::vector<accum_t> logits(FC2_OUT_ELEMS);
        unsigned long confusion[10][10] = {};
        int correct = 0;

        std::cout << "W6A6_MNIST_BEGIN samples=" << limit << "\n";
        for (int sample = 0; sample < limit; ++sample) {
            const std::size_t base = static_cast<std::size_t>(sample) * INPUT_ELEMS;
            for (int i = 0; i < INPUT_ELEMS; ++i) {
                input[i] = quantize_pixel(images[base + i]);
            }

            lenet_w6a6_top(input.data(), weights.data(), logits.data());
            int predicted = 0;
            for (int i = 1; i < FC2_OUT_ELEMS; ++i) {
                if (logits[i] > logits[predicted]) predicted = i;
            }
            const int expected = static_cast<int>(labels[sample]);
            if (expected < 0 || expected > 9) {
                throw std::runtime_error("Label outside 0..9");
            }
            ++confusion[expected][predicted];
            if (predicted == expected) ++correct;

            if ((sample + 1) % 100 == 0 || sample + 1 == limit) {
                const double running = 100.0 * correct / (sample + 1);
                std::cout << "PROGRESS " << (sample + 1) << "/" << limit
                          << " correct=" << correct
                          << " accuracy=" << std::fixed << std::setprecision(2)
                          << running << "%\n";
            }
        }

        const double accuracy = 100.0 * correct / limit;
        const bool threshold_pass = accuracy >= 90.0;
        std::ofstream csv(result_csv.c_str());
        if (!csv) throw std::runtime_error("Cannot create: " + result_csv);
        csv << "metric,value\n";
        csv << "samples," << limit << "\n";
        csv << "correct," << correct << "\n";
        csv << "accuracy_percent," << std::fixed << std::setprecision(4)
            << accuracy << "\n";
        csv << "threshold_percent,90.0000\n";
        csv << "threshold_result," << (threshold_pass ? "PASS" : "FAIL") << "\n\n";
        csv << "expected\\predicted,0,1,2,3,4,5,6,7,8,9\n";
        for (int expected = 0; expected < 10; ++expected) {
            csv << expected;
            for (int predicted = 0; predicted < 10; ++predicted) {
                csv << ',' << confusion[expected][predicted];
            }
            csv << '\n';
        }

        std::cout << "W6A6_MNIST_SUMMARY samples=" << limit
                  << " correct=" << correct
                  << " accuracy=" << std::fixed << std::setprecision(4)
                  << accuracy << "% threshold=90.0000% ["
                  << (threshold_pass ? "PASS" : "FAIL") << "]\n";
        std::cout << "W6A6_MNIST_RESULT_FILE=" << result_csv << "\n";
        return threshold_pass ? 0 : 1;
    } catch (const std::exception &error) {
        std::cerr << "W6A6_MNIST_ERROR: " << error.what() << "\n";
        return 2;
    }
}
