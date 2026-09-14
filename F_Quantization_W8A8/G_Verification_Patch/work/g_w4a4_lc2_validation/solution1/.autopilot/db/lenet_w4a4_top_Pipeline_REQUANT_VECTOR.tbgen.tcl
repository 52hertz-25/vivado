set moduleName lenet_w4a4_top_Pipeline_REQUANT_VECTOR
set isTopModule 0
set isCombinational 0
set isDatapathOnly 0
set isPipelined 1
set pipeline_type none
set FunctionProtocol ap_ctrl_hs
set isOneStateSeq 0
set ProfileFlag 0
set StallSigGenFlag 0
set isEnableWaveformDebug 1
set hasInterrupt 0
set C_modelName {lenet_w4a4_top_Pipeline_REQUANT_VECTOR}
set C_modelType { void 0 }
set C_modelArgList {
	{ conv3_acc_V int 16 regular {array 120 { 1 3 } 1 1 }  }
	{ conv3_relu_V int 3 regular {array 120 { 0 3 } 0 1 }  }
}
set C_modelArgMapList {[ 
	{ "Name" : "conv3_acc_V", "interface" : "memory", "bitwidth" : 16, "direction" : "READONLY"} , 
 	{ "Name" : "conv3_relu_V", "interface" : "memory", "bitwidth" : 3, "direction" : "WRITEONLY"} ]}
# RTL Port declarations: 
set portNum 17
set portList { 
	{ ap_clk sc_in sc_logic 1 clock -1 } 
	{ ap_rst sc_in sc_logic 1 reset -1 active_high_sync } 
	{ ap_start sc_in sc_logic 1 start -1 } 
	{ ap_done sc_out sc_logic 1 predone -1 } 
	{ ap_idle sc_out sc_logic 1 done -1 } 
	{ ap_ready sc_out sc_logic 1 ready -1 } 
	{ conv3_acc_V_address0 sc_out sc_lv 7 signal 0 } 
	{ conv3_acc_V_ce0 sc_out sc_logic 1 signal 0 } 
	{ conv3_acc_V_q0 sc_in sc_lv 16 signal 0 } 
	{ conv3_relu_V_address0 sc_out sc_lv 7 signal 1 } 
	{ conv3_relu_V_ce0 sc_out sc_logic 1 signal 1 } 
	{ conv3_relu_V_we0 sc_out sc_logic 1 signal 1 } 
	{ conv3_relu_V_d0 sc_out sc_lv 3 signal 1 } 
	{ grp_fu_1456_p_din0 sc_out sc_lv 32 signal -1 } 
	{ grp_fu_1456_p_din1 sc_out sc_lv 37 signal -1 } 
	{ grp_fu_1456_p_dout0 sc_in sc_lv 68 signal -1 } 
	{ grp_fu_1456_p_ce sc_out sc_logic 1 signal -1 } 
}
set NewPortList {[ 
	{ "name": "ap_clk", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "clock", "bundle":{"name": "ap_clk", "role": "default" }} , 
 	{ "name": "ap_rst", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "reset", "bundle":{"name": "ap_rst", "role": "default" }} , 
 	{ "name": "ap_start", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "start", "bundle":{"name": "ap_start", "role": "default" }} , 
 	{ "name": "ap_done", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "predone", "bundle":{"name": "ap_done", "role": "default" }} , 
 	{ "name": "ap_idle", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "done", "bundle":{"name": "ap_idle", "role": "default" }} , 
 	{ "name": "ap_ready", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "ready", "bundle":{"name": "ap_ready", "role": "default" }} , 
 	{ "name": "conv3_acc_V_address0", "direction": "out", "datatype": "sc_lv", "bitwidth":7, "type": "signal", "bundle":{"name": "conv3_acc_V", "role": "address0" }} , 
 	{ "name": "conv3_acc_V_ce0", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "conv3_acc_V", "role": "ce0" }} , 
 	{ "name": "conv3_acc_V_q0", "direction": "in", "datatype": "sc_lv", "bitwidth":16, "type": "signal", "bundle":{"name": "conv3_acc_V", "role": "q0" }} , 
 	{ "name": "conv3_relu_V_address0", "direction": "out", "datatype": "sc_lv", "bitwidth":7, "type": "signal", "bundle":{"name": "conv3_relu_V", "role": "address0" }} , 
 	{ "name": "conv3_relu_V_ce0", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "conv3_relu_V", "role": "ce0" }} , 
 	{ "name": "conv3_relu_V_we0", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "conv3_relu_V", "role": "we0" }} , 
 	{ "name": "conv3_relu_V_d0", "direction": "out", "datatype": "sc_lv", "bitwidth":3, "type": "signal", "bundle":{"name": "conv3_relu_V", "role": "d0" }} , 
 	{ "name": "grp_fu_1456_p_din0", "direction": "out", "datatype": "sc_lv", "bitwidth":32, "type": "signal", "bundle":{"name": "grp_fu_1456_p_din0", "role": "default" }} , 
 	{ "name": "grp_fu_1456_p_din1", "direction": "out", "datatype": "sc_lv", "bitwidth":37, "type": "signal", "bundle":{"name": "grp_fu_1456_p_din1", "role": "default" }} , 
 	{ "name": "grp_fu_1456_p_dout0", "direction": "in", "datatype": "sc_lv", "bitwidth":68, "type": "signal", "bundle":{"name": "grp_fu_1456_p_dout0", "role": "default" }} , 
 	{ "name": "grp_fu_1456_p_ce", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "grp_fu_1456_p_ce", "role": "default" }}  ]}

set RtlHierarchyInfo {[
	{"ID" : "0", "Level" : "0", "Path" : "`AUTOTB_DUT_INST", "Parent" : "", "Child" : ["1"],
		"CDFG" : "lenet_w4a4_top_Pipeline_REQUANT_VECTOR",
		"Protocol" : "ap_ctrl_hs",
		"ControlExist" : "1", "ap_start" : "1", "ap_ready" : "1", "ap_done" : "1", "ap_continue" : "0", "ap_idle" : "1", "real_start" : "0",
		"Pipeline" : "None", "UnalignedPipeline" : "0", "RewindPipeline" : "0", "ProcessNetwork" : "0",
		"II" : "0",
		"VariableLatency" : "1", "ExactLatency" : "-1", "EstimateLatencyMin" : "126", "EstimateLatencyMax" : "126",
		"Combinational" : "0",
		"Datapath" : "0",
		"ClockEnable" : "0",
		"HasSubDataflow" : "0",
		"InDataflowNetwork" : "0",
		"HasNonBlockingOperation" : "0",
		"IsBlackBox" : "0",
		"Port" : [
			{"Name" : "conv3_acc_V", "Type" : "Memory", "Direction" : "I"},
			{"Name" : "conv3_relu_V", "Type" : "Memory", "Direction" : "O"}],
		"Loop" : [
			{"Name" : "REQUANT_VECTOR", "PipelineType" : "UPC",
				"LoopDec" : {"FSMBitwidth" : "1", "FirstState" : "ap_ST_fsm_pp0_stage0", "FirstStateIter" : "ap_enable_reg_pp0_iter0", "FirstStateBlock" : "ap_block_pp0_stage0_subdone", "LastState" : "ap_ST_fsm_pp0_stage0", "LastStateIter" : "ap_enable_reg_pp0_iter5", "LastStateBlock" : "ap_block_pp0_stage0_subdone", "QuitState" : "ap_ST_fsm_pp0_stage0", "QuitStateIter" : "ap_enable_reg_pp0_iter5", "QuitStateBlock" : "ap_block_pp0_stage0_subdone", "OneDepthLoop" : "0", "has_ap_ctrl" : "1", "has_continue" : "0"}}]},
	{"ID" : "1", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.flow_control_loop_pipe_sequential_init_U", "Parent" : "0"}]}


set ArgLastReadFirstWriteLatency {
	lenet_w4a4_top_Pipeline_REQUANT_VECTOR {
		conv3_acc_V {Type I LastRead 0 FirstWrite -1}
		conv3_relu_V {Type O LastRead -1 FirstWrite 5}}}

set hasDtUnsupportedChannel 0

set PerformanceInfo {[
	{"Name" : "Latency", "Min" : "126", "Max" : "126"}
	, {"Name" : "Interval", "Min" : "126", "Max" : "126"}
]}

set PipelineEnableSignalInfo {[
	{"Pipeline" : "0", "EnableSignal" : "ap_enable_pp0"}
]}

set Spec2ImplPortList { 
	conv3_acc_V { ap_memory {  { conv3_acc_V_address0 mem_address 1 7 }  { conv3_acc_V_ce0 mem_ce 1 1 }  { conv3_acc_V_q0 mem_dout 0 16 } } }
	conv3_relu_V { ap_memory {  { conv3_relu_V_address0 mem_address 1 7 }  { conv3_relu_V_ce0 mem_ce 1 1 }  { conv3_relu_V_we0 mem_we 1 1 }  { conv3_relu_V_d0 mem_din 1 3 } } }
}
