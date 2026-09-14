set moduleName lenet_w4a4_top_Pipeline_VITIS_LOOP_147_1_KERNEL_ROW_KERNEL_COL
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
set C_modelName {lenet_w4a4_top_Pipeline_VITIS_LOOP_147_1_KERNEL_ROW_KERNEL_COL}
set C_modelType { void 0 }
set C_modelArgList {
	{ select_ln138_8 int 4 regular  }
	{ tmp60_cast_mid1145 int 4 regular  }
	{ select_ln138_7 int 4 regular  }
	{ local_weight_V_2 int 4 regular {array 75 { 1 3 } 1 1 }  }
	{ local_weight_V_3 int 4 regular {array 75 { 1 3 } 1 1 }  }
	{ pool1_V int 3 regular {array 1176 { 1 3 } 1 1 }  }
	{ accumulator_V_2_out int 15 regular {pointer 1}  }
}
set C_modelArgMapList {[ 
	{ "Name" : "select_ln138_8", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "tmp60_cast_mid1145", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "select_ln138_7", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "local_weight_V_2", "interface" : "memory", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "local_weight_V_3", "interface" : "memory", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "pool1_V", "interface" : "memory", "bitwidth" : 3, "direction" : "READONLY"} , 
 	{ "Name" : "accumulator_V_2_out", "interface" : "wire", "bitwidth" : 15, "direction" : "WRITEONLY"} ]}
# RTL Port declarations: 
set portNum 20
set portList { 
	{ ap_clk sc_in sc_logic 1 clock -1 } 
	{ ap_rst sc_in sc_logic 1 reset -1 active_high_sync } 
	{ ap_start sc_in sc_logic 1 start -1 } 
	{ ap_done sc_out sc_logic 1 predone -1 } 
	{ ap_idle sc_out sc_logic 1 done -1 } 
	{ ap_ready sc_out sc_logic 1 ready -1 } 
	{ select_ln138_8 sc_in sc_lv 4 signal 0 } 
	{ tmp60_cast_mid1145 sc_in sc_lv 4 signal 1 } 
	{ select_ln138_7 sc_in sc_lv 4 signal 2 } 
	{ local_weight_V_2_address0 sc_out sc_lv 7 signal 3 } 
	{ local_weight_V_2_ce0 sc_out sc_logic 1 signal 3 } 
	{ local_weight_V_2_q0 sc_in sc_lv 4 signal 3 } 
	{ local_weight_V_3_address0 sc_out sc_lv 7 signal 4 } 
	{ local_weight_V_3_ce0 sc_out sc_logic 1 signal 4 } 
	{ local_weight_V_3_q0 sc_in sc_lv 4 signal 4 } 
	{ pool1_V_address0 sc_out sc_lv 11 signal 5 } 
	{ pool1_V_ce0 sc_out sc_logic 1 signal 5 } 
	{ pool1_V_q0 sc_in sc_lv 3 signal 5 } 
	{ accumulator_V_2_out sc_out sc_lv 15 signal 6 } 
	{ accumulator_V_2_out_ap_vld sc_out sc_logic 1 outvld 6 } 
}
set NewPortList {[ 
	{ "name": "ap_clk", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "clock", "bundle":{"name": "ap_clk", "role": "default" }} , 
 	{ "name": "ap_rst", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "reset", "bundle":{"name": "ap_rst", "role": "default" }} , 
 	{ "name": "ap_start", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "start", "bundle":{"name": "ap_start", "role": "default" }} , 
 	{ "name": "ap_done", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "predone", "bundle":{"name": "ap_done", "role": "default" }} , 
 	{ "name": "ap_idle", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "done", "bundle":{"name": "ap_idle", "role": "default" }} , 
 	{ "name": "ap_ready", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "ready", "bundle":{"name": "ap_ready", "role": "default" }} , 
 	{ "name": "select_ln138_8", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "select_ln138_8", "role": "default" }} , 
 	{ "name": "tmp60_cast_mid1145", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "tmp60_cast_mid1145", "role": "default" }} , 
 	{ "name": "select_ln138_7", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "select_ln138_7", "role": "default" }} , 
 	{ "name": "local_weight_V_2_address0", "direction": "out", "datatype": "sc_lv", "bitwidth":7, "type": "signal", "bundle":{"name": "local_weight_V_2", "role": "address0" }} , 
 	{ "name": "local_weight_V_2_ce0", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "local_weight_V_2", "role": "ce0" }} , 
 	{ "name": "local_weight_V_2_q0", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "local_weight_V_2", "role": "q0" }} , 
 	{ "name": "local_weight_V_3_address0", "direction": "out", "datatype": "sc_lv", "bitwidth":7, "type": "signal", "bundle":{"name": "local_weight_V_3", "role": "address0" }} , 
 	{ "name": "local_weight_V_3_ce0", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "local_weight_V_3", "role": "ce0" }} , 
 	{ "name": "local_weight_V_3_q0", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "local_weight_V_3", "role": "q0" }} , 
 	{ "name": "pool1_V_address0", "direction": "out", "datatype": "sc_lv", "bitwidth":11, "type": "signal", "bundle":{"name": "pool1_V", "role": "address0" }} , 
 	{ "name": "pool1_V_ce0", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "pool1_V", "role": "ce0" }} , 
 	{ "name": "pool1_V_q0", "direction": "in", "datatype": "sc_lv", "bitwidth":3, "type": "signal", "bundle":{"name": "pool1_V", "role": "q0" }} , 
 	{ "name": "accumulator_V_2_out", "direction": "out", "datatype": "sc_lv", "bitwidth":15, "type": "signal", "bundle":{"name": "accumulator_V_2_out", "role": "default" }} , 
 	{ "name": "accumulator_V_2_out_ap_vld", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "outvld", "bundle":{"name": "accumulator_V_2_out", "role": "ap_vld" }}  ]}

set RtlHierarchyInfo {[
	{"ID" : "0", "Level" : "0", "Path" : "`AUTOTB_DUT_INST", "Parent" : "", "Child" : ["1", "2", "3"],
		"CDFG" : "lenet_w4a4_top_Pipeline_VITIS_LOOP_147_1_KERNEL_ROW_KERNEL_COL",
		"Protocol" : "ap_ctrl_hs",
		"ControlExist" : "1", "ap_start" : "1", "ap_ready" : "1", "ap_done" : "1", "ap_continue" : "0", "ap_idle" : "1", "real_start" : "0",
		"Pipeline" : "None", "UnalignedPipeline" : "0", "RewindPipeline" : "0", "ProcessNetwork" : "0",
		"II" : "0",
		"VariableLatency" : "1", "ExactLatency" : "-1", "EstimateLatencyMin" : "157", "EstimateLatencyMax" : "157",
		"Combinational" : "0",
		"Datapath" : "0",
		"ClockEnable" : "0",
		"HasSubDataflow" : "0",
		"InDataflowNetwork" : "0",
		"HasNonBlockingOperation" : "0",
		"IsBlackBox" : "0",
		"Port" : [
			{"Name" : "select_ln138_8", "Type" : "None", "Direction" : "I"},
			{"Name" : "tmp60_cast_mid1145", "Type" : "None", "Direction" : "I"},
			{"Name" : "select_ln138_7", "Type" : "None", "Direction" : "I"},
			{"Name" : "local_weight_V_2", "Type" : "Memory", "Direction" : "I"},
			{"Name" : "local_weight_V_3", "Type" : "Memory", "Direction" : "I"},
			{"Name" : "pool1_V", "Type" : "Memory", "Direction" : "I"},
			{"Name" : "accumulator_V_2_out", "Type" : "Vld", "Direction" : "O"}],
		"Loop" : [
			{"Name" : "VITIS_LOOP_147_1_KERNEL_ROW_KERNEL_COL", "PipelineType" : "UPC",
				"LoopDec" : {"FSMBitwidth" : "1", "FirstState" : "ap_ST_fsm_pp0_stage0", "FirstStateIter" : "ap_enable_reg_pp0_iter0", "FirstStateBlock" : "ap_block_pp0_stage0_subdone", "LastState" : "ap_ST_fsm_pp0_stage0", "LastStateIter" : "ap_enable_reg_pp0_iter6", "LastStateBlock" : "ap_block_pp0_stage0_subdone", "QuitState" : "ap_ST_fsm_pp0_stage0", "QuitStateIter" : "ap_enable_reg_pp0_iter6", "QuitStateBlock" : "ap_block_pp0_stage0_subdone", "OneDepthLoop" : "0", "has_ap_ctrl" : "1", "has_continue" : "0"}}]},
	{"ID" : "1", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mux_21_4_1_1_U77", "Parent" : "0"},
	{"ID" : "2", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_3ns_4s_15s_15_4_1_U78", "Parent" : "0"},
	{"ID" : "3", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.flow_control_loop_pipe_sequential_init_U", "Parent" : "0"}]}


set ArgLastReadFirstWriteLatency {
	lenet_w4a4_top_Pipeline_VITIS_LOOP_147_1_KERNEL_ROW_KERNEL_COL {
		select_ln138_8 {Type I LastRead 0 FirstWrite -1}
		tmp60_cast_mid1145 {Type I LastRead 0 FirstWrite -1}
		select_ln138_7 {Type I LastRead 0 FirstWrite -1}
		local_weight_V_2 {Type I LastRead 2 FirstWrite -1}
		local_weight_V_3 {Type I LastRead 2 FirstWrite -1}
		pool1_V {Type I LastRead 2 FirstWrite -1}
		accumulator_V_2_out {Type O LastRead -1 FirstWrite 5}}}

set hasDtUnsupportedChannel 0

set PerformanceInfo {[
	{"Name" : "Latency", "Min" : "157", "Max" : "157"}
	, {"Name" : "Interval", "Min" : "157", "Max" : "157"}
]}

set PipelineEnableSignalInfo {[
	{"Pipeline" : "0", "EnableSignal" : "ap_enable_pp0"}
]}

set Spec2ImplPortList { 
	select_ln138_8 { ap_none {  { select_ln138_8 in_data 0 4 } } }
	tmp60_cast_mid1145 { ap_none {  { tmp60_cast_mid1145 in_data 0 4 } } }
	select_ln138_7 { ap_none {  { select_ln138_7 in_data 0 4 } } }
	local_weight_V_2 { ap_memory {  { local_weight_V_2_address0 mem_address 1 7 }  { local_weight_V_2_ce0 mem_ce 1 1 }  { local_weight_V_2_q0 in_data 0 4 } } }
	local_weight_V_3 { ap_memory {  { local_weight_V_3_address0 mem_address 1 7 }  { local_weight_V_3_ce0 mem_ce 1 1 }  { local_weight_V_3_q0 in_data 0 4 } } }
	pool1_V { ap_memory {  { pool1_V_address0 mem_address 1 11 }  { pool1_V_ce0 mem_ce 1 1 }  { pool1_V_q0 in_data 0 3 } } }
	accumulator_V_2_out { ap_vld {  { accumulator_V_2_out out_data 1 15 }  { accumulator_V_2_out_ap_vld out_vld 1 1 } } }
}
