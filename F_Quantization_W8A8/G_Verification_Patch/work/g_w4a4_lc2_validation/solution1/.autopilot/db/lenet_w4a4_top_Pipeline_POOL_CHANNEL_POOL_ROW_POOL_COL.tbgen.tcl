set moduleName lenet_w4a4_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL
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
set C_modelName {lenet_w4a4_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL}
set C_modelType { void 0 }
set C_modelArgList {
	{ conv1_acc_V int 12 regular {array 4704 { 1 1 1 1 3 3 3 3 3 3 3 3 3 3 3 3 3 } 1 1 }  }
	{ pool1_V int 3 regular {array 1176 { 0 3 } 0 1 }  }
}
set C_modelArgMapList {[ 
	{ "Name" : "conv1_acc_V", "interface" : "memory", "bitwidth" : 12, "direction" : "READONLY"} , 
 	{ "Name" : "pool1_V", "interface" : "memory", "bitwidth" : 3, "direction" : "WRITEONLY"} ]}
# RTL Port declarations: 
set portNum 22
set portList { 
	{ ap_clk sc_in sc_logic 1 clock -1 } 
	{ ap_rst sc_in sc_logic 1 reset -1 active_high_sync } 
	{ ap_start sc_in sc_logic 1 start -1 } 
	{ ap_done sc_out sc_logic 1 predone -1 } 
	{ ap_idle sc_out sc_logic 1 done -1 } 
	{ ap_ready sc_out sc_logic 1 ready -1 } 
	{ conv1_acc_V_address0 sc_out sc_lv 13 signal 0 } 
	{ conv1_acc_V_ce0 sc_out sc_logic 1 signal 0 } 
	{ conv1_acc_V_q0 sc_in sc_lv 12 signal 0 } 
	{ conv1_acc_V_address1 sc_out sc_lv 13 signal 0 } 
	{ conv1_acc_V_ce1 sc_out sc_logic 1 signal 0 } 
	{ conv1_acc_V_q1 sc_in sc_lv 12 signal 0 } 
	{ conv1_acc_V_address2 sc_out sc_lv 13 signal 0 } 
	{ conv1_acc_V_ce2 sc_out sc_logic 1 signal 0 } 
	{ conv1_acc_V_q2 sc_in sc_lv 12 signal 0 } 
	{ conv1_acc_V_address3 sc_out sc_lv 13 signal 0 } 
	{ conv1_acc_V_ce3 sc_out sc_logic 1 signal 0 } 
	{ conv1_acc_V_q3 sc_in sc_lv 12 signal 0 } 
	{ pool1_V_address0 sc_out sc_lv 11 signal 1 } 
	{ pool1_V_ce0 sc_out sc_logic 1 signal 1 } 
	{ pool1_V_we0 sc_out sc_logic 1 signal 1 } 
	{ pool1_V_d0 sc_out sc_lv 3 signal 1 } 
}
set NewPortList {[ 
	{ "name": "ap_clk", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "clock", "bundle":{"name": "ap_clk", "role": "default" }} , 
 	{ "name": "ap_rst", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "reset", "bundle":{"name": "ap_rst", "role": "default" }} , 
 	{ "name": "ap_start", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "start", "bundle":{"name": "ap_start", "role": "default" }} , 
 	{ "name": "ap_done", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "predone", "bundle":{"name": "ap_done", "role": "default" }} , 
 	{ "name": "ap_idle", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "done", "bundle":{"name": "ap_idle", "role": "default" }} , 
 	{ "name": "ap_ready", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "ready", "bundle":{"name": "ap_ready", "role": "default" }} , 
 	{ "name": "conv1_acc_V_address0", "direction": "out", "datatype": "sc_lv", "bitwidth":13, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "address0" }} , 
 	{ "name": "conv1_acc_V_ce0", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "ce0" }} , 
 	{ "name": "conv1_acc_V_q0", "direction": "in", "datatype": "sc_lv", "bitwidth":12, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "q0" }} , 
 	{ "name": "conv1_acc_V_address1", "direction": "out", "datatype": "sc_lv", "bitwidth":13, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "address1" }} , 
 	{ "name": "conv1_acc_V_ce1", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "ce1" }} , 
 	{ "name": "conv1_acc_V_q1", "direction": "in", "datatype": "sc_lv", "bitwidth":12, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "q1" }} , 
 	{ "name": "conv1_acc_V_address2", "direction": "out", "datatype": "sc_lv", "bitwidth":13, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "address2" }} , 
 	{ "name": "conv1_acc_V_ce2", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "ce2" }} , 
 	{ "name": "conv1_acc_V_q2", "direction": "in", "datatype": "sc_lv", "bitwidth":12, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "q2" }} , 
 	{ "name": "conv1_acc_V_address3", "direction": "out", "datatype": "sc_lv", "bitwidth":13, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "address3" }} , 
 	{ "name": "conv1_acc_V_ce3", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "ce3" }} , 
 	{ "name": "conv1_acc_V_q3", "direction": "in", "datatype": "sc_lv", "bitwidth":12, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "q3" }} , 
 	{ "name": "pool1_V_address0", "direction": "out", "datatype": "sc_lv", "bitwidth":11, "type": "signal", "bundle":{"name": "pool1_V", "role": "address0" }} , 
 	{ "name": "pool1_V_ce0", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "pool1_V", "role": "ce0" }} , 
 	{ "name": "pool1_V_we0", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "pool1_V", "role": "we0" }} , 
 	{ "name": "pool1_V_d0", "direction": "out", "datatype": "sc_lv", "bitwidth":3, "type": "signal", "bundle":{"name": "pool1_V", "role": "d0" }}  ]}

set RtlHierarchyInfo {[
	{"ID" : "0", "Level" : "0", "Path" : "`AUTOTB_DUT_INST", "Parent" : "", "Child" : ["1", "2", "3", "4", "5"],
		"CDFG" : "lenet_w4a4_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL",
		"Protocol" : "ap_ctrl_hs",
		"ControlExist" : "1", "ap_start" : "1", "ap_ready" : "1", "ap_done" : "1", "ap_continue" : "0", "ap_idle" : "1", "real_start" : "0",
		"Pipeline" : "None", "UnalignedPipeline" : "0", "RewindPipeline" : "0", "ProcessNetwork" : "0",
		"II" : "0",
		"VariableLatency" : "1", "ExactLatency" : "-1", "EstimateLatencyMin" : "1184", "EstimateLatencyMax" : "1184",
		"Combinational" : "0",
		"Datapath" : "0",
		"ClockEnable" : "0",
		"HasSubDataflow" : "0",
		"InDataflowNetwork" : "0",
		"HasNonBlockingOperation" : "0",
		"IsBlackBox" : "0",
		"Port" : [
			{"Name" : "conv1_acc_V", "Type" : "Memory", "Direction" : "I"},
			{"Name" : "pool1_V", "Type" : "Memory", "Direction" : "O"}],
		"Loop" : [
			{"Name" : "POOL_CHANNEL_POOL_ROW_POOL_COL", "PipelineType" : "UPC",
				"LoopDec" : {"FSMBitwidth" : "1", "FirstState" : "ap_ST_fsm_pp0_stage0", "FirstStateIter" : "ap_enable_reg_pp0_iter0", "FirstStateBlock" : "ap_block_pp0_stage0_subdone", "LastState" : "ap_ST_fsm_pp0_stage0", "LastStateIter" : "ap_enable_reg_pp0_iter7", "LastStateBlock" : "ap_block_pp0_stage0_subdone", "QuitState" : "ap_ST_fsm_pp0_stage0", "QuitStateIter" : "ap_enable_reg_pp0_iter7", "QuitStateBlock" : "ap_block_pp0_stage0_subdone", "OneDepthLoop" : "0", "has_ap_ctrl" : "1", "has_continue" : "0"}}]},
	{"ID" : "1", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mul_32ns_36ns_67_2_1_U65", "Parent" : "0"},
	{"ID" : "2", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mul_32ns_36ns_67_2_1_U66", "Parent" : "0"},
	{"ID" : "3", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mul_32ns_36ns_67_2_1_U67", "Parent" : "0"},
	{"ID" : "4", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mul_32ns_36ns_67_2_1_U68", "Parent" : "0"},
	{"ID" : "5", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.flow_control_loop_pipe_sequential_init_U", "Parent" : "0"}]}


set ArgLastReadFirstWriteLatency {
	lenet_w4a4_top_Pipeline_POOL_CHANNEL_POOL_ROW_POOL_COL {
		conv1_acc_V {Type I LastRead 2 FirstWrite -1}
		pool1_V {Type O LastRead -1 FirstWrite 7}}}

set hasDtUnsupportedChannel 0

set PerformanceInfo {[
	{"Name" : "Latency", "Min" : "1184", "Max" : "1184"}
	, {"Name" : "Interval", "Min" : "1184", "Max" : "1184"}
]}

set PipelineEnableSignalInfo {[
	{"Pipeline" : "0", "EnableSignal" : "ap_enable_pp0"}
]}

set Spec2ImplPortList { 
	conv1_acc_V { ap_memory {  { conv1_acc_V_address0 mem_address 1 13 }  { conv1_acc_V_ce0 mem_ce 1 1 }  { conv1_acc_V_q0 mem_dout 0 12 }  { conv1_acc_V_address1 MemPortADDR2 1 13 }  { conv1_acc_V_ce1 MemPortCE2 1 1 }  { conv1_acc_V_q1 MemPortDOUT2 0 12 }  { conv1_acc_V_address2 MemPortADDR2 1 13 }  { conv1_acc_V_ce2 MemPortCE2 1 1 }  { conv1_acc_V_q2 MemPortDOUT2 0 12 }  { conv1_acc_V_address3 MemPortADDR2 1 13 }  { conv1_acc_V_ce3 MemPortCE2 1 1 }  { conv1_acc_V_q3 MemPortDOUT2 0 12 } } }
	pool1_V { ap_memory {  { pool1_V_address0 mem_address 1 11 }  { pool1_V_ce0 mem_ce 1 1 }  { pool1_V_we0 mem_we 1 1 }  { pool1_V_d0 mem_din 1 3 } } }
}
