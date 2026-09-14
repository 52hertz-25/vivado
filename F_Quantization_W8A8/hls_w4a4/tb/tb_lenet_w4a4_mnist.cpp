#include "lenet_w4a4.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

using lenet_w4a4::accum_t;
using lenet_w4a4::packed_t;

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

packed_t pack_pair(int low, int high) {
    const unsigned low_nibble = static_cast<unsigned>(low) & 0x0fU;
    const unsigned high_nibble = static_cast<unsigned>(high) & 0x0fU;
    return packed_t(low_nibble | (high_nibble << 4));
}

std::vector<packed_t> load_all_weights(const std::string &root) {
    using namespace lenet_w4a4;
    const char *layers[] = {"conv1", "conv2", "conv3", "fc1", "fc2"};
    const int counts[] = {CONV1_WEIGHT_ELEMS, CONV2_WEIGHT_ELEMS,
                          CONV3_WEIGHT_ELEMS, FC1_WEIGHT_ELEMS,
                          FC2_WEIGHT_ELEMS};
    std::vector<int> unpacked;
    unpacked.reserve(TOTAL_WEIGHT_ELEMS);
    for (int layer = 0; layer < 5; ++layer) {
        const std::vector<int> values = load_ints(
            join_path(root, std::string(layers[layer]) + ".weight.int4.txt"),
            counts[layer]);
        for (std::size_t i = 0; i < values.size(); ++i) {
            if (values[i] < -7 || values[i] > 7) {
                throw std::runtime_error("INT4 range violation");
            }
            unpacked.push_back(values[i]);
        }
    }
    std::vector<packed_t> packed(TOTAL_WEIGHT_PACKED_ELEMS);
    for (int i = 0; i < TOTAL_WEIGHT_PACKED_ELEMS; ++i) {
        packed[i] = pack_pair(unpacked[2 * i], unpacked[2 * i + 1]);
    }
    return packed;
}

int quantize_pixel(unsigned char pixel) {
    const double mean = 0.1307;
    const double stddev = 0.3081;
    const double input_scale = 0.4030695302145822;
    const double normalized = (static_cast<double>(pixel) / 255.0 - mean) / stddev;
    long value = static_cast<long>(std::nearbyint(normalized / input_scale));
    value = std::max(-7L, std::min(7L, value));
    return static_cast<int>(value);
}

}  // namespace

int main(int argc, char **argv) {
    try {
        if (argc < 5) {
            std::cerr << "Usage: tb_lenet_w4a4_mnist <dataset_root> "
                         "<weight_root> <sample_limit> <result_csv>\n";
            return 2;
        }

        using namespace lenet_w4a4;
        const std::string dataset_root = argv[1];
        const std::string weight_root = argv[2];
        int limit = std::stoi(argv[3]);
        const std::string result_csv = argv[4];
        const std::vector<unsigned char> images =
            read_binary(join_path(dataset_root, "mnist_test_32x32.bin"));
        const std::vector<unsigned char> labels =
            read_binary(join_path(dataset_root, "mnist_test_labels.bin"));
        const std::vector<packed_t> weights = load_all_weights(weight_root);

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

        std::vector<packed_t> input(INPUT_PACKED_ELEMS);
        std::vector<accum_t> logits(FC2_OUT_ELEMS);
        unsigned long confusion[10][10] = {};
        int correct = 0;

        std::cout << "W4A4_MNIST_BEGIN samples=" << limit << "\n";
        for (int sample = 0; sample < limit; ++sample) {
            const std::size_t base = static_cast<std::size_t>(sample) * INPUT_ELEMS;
            for (int i = 0; i < INPUT_PACKED_ELEMS; ++i) {
                input[i] = pack_pair(quantize_pixel(images[base + 2 * i]),
                                     quantize_pixel(images[base + 2 * i + 1]));
            }

            lenet_w4a4_top(input.data(), weights.data(), logits.data());
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

        std::cout << "W4A4_MNIST_SUMMARY samples=" << limit
                  << " correct=" << correct
                  << " accuracy=" << std::fixed << std::setprecision(4)
                  << accuracy << "% threshold=90.0000% ["
                  << (threshold_pass ? "PASS" : "FAIL") << "]\n";
        std::cout << "W4A4_MNIST_RESULT_FILE=" << result_csv << "\n";
        return threshold_pass ? 0 : 1;
    } catch (const std::exception &error) {
        std::cerr << "W4A4_MNIST_ERROR: " << error.what() << "\n";
        return 2;
    }
}
