<project xmlns="com.autoesl.autopilot.project" top="lenet_full_top" name="lenet_full_hls">
    <includePaths/>
    <libraryPaths/>
    <Simulation argv="D:/lenet_project/model">
        <SimFlow name="csim" clean="true" csimMode="0" lastCsimMode="0"/>
    </Simulation>
    <files xmlns="">
        <file name="../../../member_c_conv_hls/tb/tb_lenet_conv.cpp" sc="0" tb="1" cflags=" -ID:/lenet_project/member_c_conv_hls/include  -ID:/lenet_project/member_c_conv_hls/tb  -DLENET_HLS_TOP_FULL -std=c++11 -Wno-unknown-pragmas" csimflags=" -Wno-unknown-pragmas" blackbox="false"/>
        <file name="../../../member_c_conv_hls/tb/npy_reader.h" sc="0" tb="1" cflags=" -Wno-unknown-pragmas" csimflags=" -Wno-unknown-pragmas" blackbox="false"/>
        <file name="../member_c_conv_hls/include/lenet_conv.h" sc="0" tb="false" cflags="" csimflags="" blackbox="false"/>
        <file name="../member_c_conv_hls/src/lenet_conv.cpp" sc="0" tb="false" cflags="-ID:/lenet_project/member_c_conv_hls/include" csimflags="" blackbox="false"/>
    </files>
    <solutions xmlns="">
        <solution name="solution1" status="active"/>
    </solutions>
</project>

