<AutoPilot:project xmlns:AutoPilot="com.autoesl.autopilot.project" projectType="C/C++" top="lenet_w4a4_top" name="g_w4a4_lc2_validation">
    <includePaths/>
    <libraryFlag/>
    <files>
        <file name="D:/GitHub/vivado/vivado/F_Quantization_W8A8/G_Verification_Patch/tb_g_balanced20.cpp" sc="0" tb="1" cflags=" -ID:/GitHub/vivado/vivado/F_Quantization_W8A8/hls_w4a4/include  -std=c++11 -Wno-unknown-pragmas" csimflags=" -Wno-unknown-pragmas" blackbox="false"/>
        <file name="D:/GitHub/vivado/vivado/F_Quantization_W8A8/hls_w4a4/src/lenet_w4a4_lc2.cpp" sc="0" tb="false" cflags="-ID:/GitHub/vivado/vivado/F_Quantization_W8A8/hls_w4a4/include -std=c++11" csimflags="" blackbox="false"/>
    </files>
    <solutions>
        <solution name="solution1" status=""/>
    </solutions>
    <Simulation argv="D:/GitHub/vivado/vivado/F_Quantization_W8A8/hls_w8a8/data/mnist_w8a8 D:/GitHub/vivado/vivado/F_Quantization_W8A8/hls_w4a4/model/int4_weights D:/GitHub/vivado/vivado/F_Quantization_W8A8/G_Verification_Patch/results/g_balanced20_csim.csv">
        <SimFlow name="csim" setup="false" optimizeCompile="false" clean="false" ldflags="" mflags=""/>
    </Simulation>
</AutoPilot:project>

