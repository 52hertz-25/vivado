# Source variants

Put each experimental source in its own subfolder, for example:

`variants/fixed16/lenet_conv.cpp`

Then copy a configuration entry in `configs/configs.tcl`, point `source_cpp` to that file, and set `enabled 1`. Never overwrite the verified baseline in `src/lenet_conv.cpp`.
