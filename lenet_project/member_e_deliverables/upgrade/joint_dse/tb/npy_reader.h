#ifndef NPY_READER_H_
#define NPY_READER_H_

#include <cctype>
#include <cstdint>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

struct NpyFloatArray {
    std::vector<std::size_t> shape;
    std::vector<float> data;
};

inline std::vector<std::size_t> parse_npy_shape(const std::string &header) {
    const std::size_t shape_key = header.find("shape");
    const std::size_t open = header.find('(', shape_key);
    const std::size_t close = header.find(')', open);
    if (shape_key == std::string::npos || open == std::string::npos ||
        close == std::string::npos) {
        throw std::runtime_error("NPY header has no valid shape tuple");
    }

    std::vector<std::size_t> shape;
    std::size_t value = 0;
    bool reading_number = false;
    for (std::size_t index = open + 1; index < close; ++index) {
        const unsigned char character =
            static_cast<unsigned char>(header[index]);
        if (std::isdigit(character)) {
            value = value * 10 + static_cast<std::size_t>(character - '0');
            reading_number = true;
        } else if (reading_number) {
            shape.push_back(value);
            value = 0;
            reading_number = false;
        }
    }
    if (reading_number) {
        shape.push_back(value);
    }
    if (shape.empty()) {
        throw std::runtime_error("NPY shape is empty");
    }
    return shape;
}

inline NpyFloatArray load_npy_float32(const std::string &path) {
    std::ifstream stream(path.c_str(), std::ios::binary);
    if (!stream) {
        throw std::runtime_error("Cannot open NPY file: " + path);
    }

    unsigned char magic[6] = {};
    stream.read(reinterpret_cast<char *>(magic), 6);
    if (!stream || magic[0] != 0x93 || magic[1] != 'N' || magic[2] != 'U' ||
        magic[3] != 'M' || magic[4] != 'P' || magic[5] != 'Y') {
        throw std::runtime_error("Invalid NPY magic: " + path);
    }

    unsigned char version[2] = {};
    stream.read(reinterpret_cast<char *>(version), 2);

    std::uint32_t header_length = 0;
    if (version[0] == 1) {
        unsigned char length_bytes[2] = {};
        stream.read(reinterpret_cast<char *>(length_bytes), 2);
        header_length = static_cast<std::uint32_t>(length_bytes[0]) |
                        (static_cast<std::uint32_t>(length_bytes[1]) << 8);
    } else if (version[0] == 2 || version[0] == 3) {
        unsigned char length_bytes[4] = {};
        stream.read(reinterpret_cast<char *>(length_bytes), 4);
        header_length = static_cast<std::uint32_t>(length_bytes[0]) |
                        (static_cast<std::uint32_t>(length_bytes[1]) << 8) |
                        (static_cast<std::uint32_t>(length_bytes[2]) << 16) |
                        (static_cast<std::uint32_t>(length_bytes[3]) << 24);
    } else {
        throw std::runtime_error("Unsupported NPY version: " + path);
    }

    std::string header(header_length, '\0');
    stream.read(&header[0], static_cast<std::streamsize>(header_length));
    if (!stream) {
        throw std::runtime_error("Truncated NPY header: " + path);
    }
    if (header.find("<f4") == std::string::npos &&
        header.find("|f4") == std::string::npos) {
        throw std::runtime_error("Only little-endian float32 NPY is supported: " + path);
    }
    if (header.find("fortran_order") == std::string::npos ||
        header.find("False") == std::string::npos) {
        throw std::runtime_error("Fortran-order NPY is not supported: " + path);
    }

    NpyFloatArray array;
    array.shape = parse_npy_shape(header);
    std::size_t element_count = 1;
    for (std::size_t dimension : array.shape) {
        element_count *= dimension;
    }
    array.data.resize(element_count);
    stream.read(
        reinterpret_cast<char *>(array.data.data()),
        static_cast<std::streamsize>(element_count * sizeof(float)));
    if (!stream) {
        throw std::runtime_error("Truncated NPY data: " + path);
    }
    return array;
}

#endif  // NPY_READER_H_
