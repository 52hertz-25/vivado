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

std::string join_path(const std::string& root, const std::string& name) {
    if (root.empty()) return name;
    const char last = root[root.size() - 1];
    return (last == '/' || last == '\\') ? root + name : root + "/" + name;
}

std::vector<unsigned char> read_binary(const std::string& path) {
    std::ifstream f(path.c_str(), std::ios::binary | std::ios::ate);
    if (!f) throw std::runtime_error("cannot open: " + path);
    const std::streamsize n = f.tellg();
    if (n < 0) throw std::runtime_error("cannot size: " + path);
    f.seekg(0, std::ios::beg);
    std::vector<unsigned char> data(static_cast<std::size_t>(n));
    if (n && !f.read(reinterpret_cast<char*>(data.data()), n))
        throw std::runtime_error("cannot read: " + path);
    return data;
}

std::vector<int> read_ints(const std::string& path, std::size_t expected) {
    std::ifstream f(path.c_str());
    if (!f) throw std::runtime_error("cannot open: " + path);
    std::vector<int> v; int x = 0;
    while (f >> x) v.push_back(x);
    if (v.size() != expected) throw std::runtime_error("element count mismatch: " + path);
    return v;
}

packed_t pack_pair(int lo, int hi) {
    return packed_t((static_cast<unsigned>(lo) & 15U) |
                    ((static_cast<unsigned>(hi) & 15U) << 4));
}

int quantize_pixel(unsigned char pixel) {
    const double mean = 0.1307, stddev = 0.3081;
    const double input_scale = 0.4030695302145822;
    const double normalized = (static_cast<double>(pixel) / 255.0 - mean) / stddev;
    long q = static_cast<long>(std::nearbyint(normalized / input_scale));
    q = std::max(-7L, std::min(7L, q));
    return static_cast<int>(q);
}

std::vector<packed_t> load_weights(const std::string& root) {
    using namespace lenet_w4a4;
    const char* names[] = {"conv1", "conv2", "conv3", "fc1", "fc2"};
    const int counts[] = {CONV1_WEIGHT_ELEMS, CONV2_WEIGHT_ELEMS,
                          CONV3_WEIGHT_ELEMS, FC1_WEIGHT_ELEMS, FC2_WEIGHT_ELEMS};
    std::vector<int> unpacked; unpacked.reserve(TOTAL_WEIGHT_ELEMS);
    for (int layer = 0; layer < 5; ++layer) {
        std::vector<int> v = read_ints(
            join_path(root, std::string(names[layer]) + ".weight.int4.txt"), counts[layer]);
        for (std::size_t i = 0; i < v.size(); ++i) {
            if (v[i] < -7 || v[i] > 7) throw std::runtime_error("INT4 range violation");
            unpacked.push_back(v[i]);
        }
    }
    std::vector<packed_t> packed(TOTAL_WEIGHT_PACKED_ELEMS);
    for (int i = 0; i < TOTAL_WEIGHT_PACKED_ELEMS; ++i)
        packed[i] = pack_pair(unpacked[2*i], unpacked[2*i+1]);
    return packed;
}

std::vector<int> select_balanced20(const std::vector<unsigned char>& labels) {
    int count[10] = {};
    std::vector<int> selected;
    for (std::size_t i = 0; i < labels.size() && selected.size() < 20; ++i) {
        const int label = labels[i];
        if (label >= 0 && label < 10 && count[label] < 2) {
            selected.push_back(static_cast<int>(i));
            ++count[label];
        }
    }
    for (int c = 0; c < 10; ++c)
        if (count[c] != 2) throw std::runtime_error("dataset does not contain two samples per class");
    return selected;
}
}

int main(int argc, char** argv) {
    try {
        if (argc != 4) {
            std::cerr << "usage: tb_g_balanced20 <dataset_root> <weight_root> <result_csv>\n";
            return 2;
        }
        using namespace lenet_w4a4;
        const std::string data_root = argv[1], weight_root = argv[2], csv_path = argv[3];
        const std::vector<unsigned char> images = read_binary(join_path(data_root,"mnist_test_32x32.bin"));
        const std::vector<unsigned char> labels = read_binary(join_path(data_root,"mnist_test_labels.bin"));
        if (images.size() != labels.size() * INPUT_ELEMS)
            throw std::runtime_error("image and label sizes do not match");
        const std::vector<int> selected = select_balanced20(labels);
        const std::vector<packed_t> weights = load_weights(weight_root);
        std::vector<packed_t> input(INPUT_PACKED_ELEMS);
        std::vector<accum_t> logits(FC2_OUT_ELEMS);
        std::ofstream csv(csv_path.c_str());
        if (!csv) throw std::runtime_error("cannot create: " + csv_path);
        csv << "order,dataset_index,expected,predicted,correct";
        for (int j=0;j<10;++j) csv << ",logit" << j;
        csv << "\n";
        int correct = 0;
        for (std::size_t order=0; order<selected.size(); ++order) {
            const int sample=selected[order];
            const std::size_t base=static_cast<std::size_t>(sample)*INPUT_ELEMS;
            for (int i=0;i<INPUT_PACKED_ELEMS;++i)
                input[i]=pack_pair(quantize_pixel(images[base+2*i]),quantize_pixel(images[base+2*i+1]));
            lenet_w4a4_top(input.data(),weights.data(),logits.data());
            int pred=0;
            for (int j=1;j<FC2_OUT_ELEMS;++j) if (logits[j]>logits[pred]) pred=j;
            const int expected=labels[sample]; const bool ok=pred==expected;
            if (ok) ++correct;
            csv << order << ',' << sample << ',' << expected << ',' << pred << ',' << (ok?1:0);
            for (int j=0;j<10;++j) csv << ',' << logits[j].to_int();
            csv << '\n';
            std::cout << "G_SAMPLE order=" << order << " index=" << sample
                      << " expected=" << expected << " predicted=" << pred
                      << (ok?" PASS":" FAIL") << '\n';
        }
        csv << "SUMMARY,,," << correct << "," << (correct==20?1:0) << "\n";
        std::cout << "G_BALANCED20_SUMMARY samples=20 correct=" << correct << "\n";
        // Accuracy is reported, but functional C/RTL equivalence is checked by exact CSV comparison.
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "G_BALANCED20_ERROR: " << e.what() << '\n'; return 2;
    }
}

