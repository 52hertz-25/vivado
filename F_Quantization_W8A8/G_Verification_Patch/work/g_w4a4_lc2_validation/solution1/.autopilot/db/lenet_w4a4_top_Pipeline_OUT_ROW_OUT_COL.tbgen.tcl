set moduleName lenet_w4a4_top_Pipeline_OUT_ROW_OUT_COL
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
set C_modelName {lenet_w4a4_top_Pipeline_OUT_ROW_OUT_COL}
set C_modelType { void 0 }
set C_modelArgList {
	{ empty int 9 regular  }
	{ input_V int 4 regular {array 1024 { 1 1 1 1 1 1 1 1 1 1 1 1 1 3 3 3 3 } 1 1 }  }
	{ sext_ln178 int 4 regular  }
	{ sext_ln172 int 4 regular  }
	{ sext_ln178_1 int 4 regular  }
	{ sext_ln172_1 int 4 regular  }
	{ sext_ln178_2 int 4 regular  }
	{ sext_ln172_2 int 4 regular  }
	{ sext_ln178_3 int 4 regular  }
	{ sext_ln172_3 int 4 regular  }
	{ sext_ln178_4 int 4 regular  }
	{ sext_ln172_4 int 4 regular  }
	{ sext_ln178_5 int 4 regular  }
	{ sext_ln172_5 int 4 regular  }
	{ sext_ln178_6 int 4 regular  }
	{ sext_ln172_6 int 4 regular  }
	{ sext_ln178_7 int 4 regular  }
	{ sext_ln172_7 int 4 regular  }
	{ sext_ln178_8 int 4 regular  }
	{ sext_ln172_8 int 4 regular  }
	{ sext_ln178_9 int 4 regular  }
	{ sext_ln172_9 int 4 regular  }
	{ sext_ln178_10 int 4 regular  }
	{ sext_ln172_10 int 4 regular  }
	{ sext_ln178_11 int 4 regular  }
	{ sext_ln172_11 int 4 regular  }
	{ sext_ln138 int 4 regular  }
	{ conv1_acc_V int 12 regular {array 4704 { 0 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 } 0 1 }  }
}
set C_modelArgMapList {[ 
	{ "Name" : "empty", "interface" : "wire", "bitwidth" : 9, "direction" : "READONLY"} , 
 	{ "Name" : "input_V", "interface" : "memory", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln178", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln172", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln178_1", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln172_1", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln178_2", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln172_2", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln178_3", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln172_3", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln178_4", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln172_4", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln178_5", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln172_5", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln178_6", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln172_6", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln178_7", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln172_7", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln178_8", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln172_8", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln178_9", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln172_9", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln178_10", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln172_10", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln178_11", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln172_11", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "sext_ln138", "interface" : "wire", "bitwidth" : 4, "direction" : "READONLY"} , 
 	{ "Name" : "conv1_acc_V", "interface" : "memory", "bitwidth" : 12, "direction" : "WRITEONLY"} ]}
# RTL Port declarations: 
set portNum 75
set portList { 
	{ ap_clk sc_in sc_logic 1 clock -1 } 
	{ ap_rst sc_in sc_logic 1 reset -1 active_high_sync } 
	{ ap_start sc_in sc_logic 1 start -1 } 
	{ ap_done sc_out sc_logic 1 predone -1 } 
	{ ap_idle sc_out sc_logic 1 done -1 } 
	{ ap_ready sc_out sc_logic 1 ready -1 } 
	{ empty sc_in sc_lv 9 signal 0 } 
	{ input_V_address0 sc_out sc_lv 10 signal 1 } 
	{ input_V_ce0 sc_out sc_logic 1 signal 1 } 
	{ input_V_q0 sc_in sc_lv 4 signal 1 } 
	{ input_V_address1 sc_out sc_lv 10 signal 1 } 
	{ input_V_ce1 sc_out sc_logic 1 signal 1 } 
	{ input_V_q1 sc_in sc_lv 4 signal 1 } 
	{ input_V_address2 sc_out sc_lv 10 signal 1 } 
	{ input_V_ce2 sc_out sc_logic 1 signal 1 } 
	{ input_V_q2 sc_in sc_lv 4 signal 1 } 
	{ input_V_address3 sc_out sc_lv 10 signal 1 } 
	{ input_V_ce3 sc_out sc_logic 1 signal 1 } 
	{ input_V_q3 sc_in sc_lv 4 signal 1 } 
	{ input_V_address4 sc_out sc_lv 10 signal 1 } 
	{ input_V_ce4 sc_out sc_logic 1 signal 1 } 
	{ input_V_q4 sc_in sc_lv 4 signal 1 } 
	{ input_V_address5 sc_out sc_lv 10 signal 1 } 
	{ input_V_ce5 sc_out sc_logic 1 signal 1 } 
	{ input_V_q5 sc_in sc_lv 4 signal 1 } 
	{ input_V_address6 sc_out sc_lv 10 signal 1 } 
	{ input_V_ce6 sc_out sc_logic 1 signal 1 } 
	{ input_V_q6 sc_in sc_lv 4 signal 1 } 
	{ input_V_address7 sc_out sc_lv 10 signal 1 } 
	{ input_V_ce7 sc_out sc_logic 1 signal 1 } 
	{ input_V_q7 sc_in sc_lv 4 signal 1 } 
	{ input_V_address8 sc_out sc_lv 10 signal 1 } 
	{ input_V_ce8 sc_out sc_logic 1 signal 1 } 
	{ input_V_q8 sc_in sc_lv 4 signal 1 } 
	{ input_V_address9 sc_out sc_lv 10 signal 1 } 
	{ input_V_ce9 sc_out sc_logic 1 signal 1 } 
	{ input_V_q9 sc_in sc_lv 4 signal 1 } 
	{ input_V_address10 sc_out sc_lv 10 signal 1 } 
	{ input_V_ce10 sc_out sc_logic 1 signal 1 } 
	{ input_V_q10 sc_in sc_lv 4 signal 1 } 
	{ input_V_address11 sc_out sc_lv 10 signal 1 } 
	{ input_V_ce11 sc_out sc_logic 1 signal 1 } 
	{ input_V_q11 sc_in sc_lv 4 signal 1 } 
	{ input_V_address12 sc_out sc_lv 10 signal 1 } 
	{ input_V_ce12 sc_out sc_logic 1 signal 1 } 
	{ input_V_q12 sc_in sc_lv 4 signal 1 } 
	{ sext_ln178 sc_in sc_lv 4 signal 2 } 
	{ sext_ln172 sc_in sc_lv 4 signal 3 } 
	{ sext_ln178_1 sc_in sc_lv 4 signal 4 } 
	{ sext_ln172_1 sc_in sc_lv 4 signal 5 } 
	{ sext_ln178_2 sc_in sc_lv 4 signal 6 } 
	{ sext_ln172_2 sc_in sc_lv 4 signal 7 } 
	{ sext_ln178_3 sc_in sc_lv 4 signal 8 } 
	{ sext_ln172_3 sc_in sc_lv 4 signal 9 } 
	{ sext_ln178_4 sc_in sc_lv 4 signal 10 } 
	{ sext_ln172_4 sc_in sc_lv 4 signal 11 } 
	{ sext_ln178_5 sc_in sc_lv 4 signal 12 } 
	{ sext_ln172_5 sc_in sc_lv 4 signal 13 } 
	{ sext_ln178_6 sc_in sc_lv 4 signal 14 } 
	{ sext_ln172_6 sc_in sc_lv 4 signal 15 } 
	{ sext_ln178_7 sc_in sc_lv 4 signal 16 } 
	{ sext_ln172_7 sc_in sc_lv 4 signal 17 } 
	{ sext_ln178_8 sc_in sc_lv 4 signal 18 } 
	{ sext_ln172_8 sc_in sc_lv 4 signal 19 } 
	{ sext_ln178_9 sc_in sc_lv 4 signal 20 } 
	{ sext_ln172_9 sc_in sc_lv 4 signal 21 } 
	{ sext_ln178_10 sc_in sc_lv 4 signal 22 } 
	{ sext_ln172_10 sc_in sc_lv 4 signal 23 } 
	{ sext_ln178_11 sc_in sc_lv 4 signal 24 } 
	{ sext_ln172_11 sc_in sc_lv 4 signal 25 } 
	{ sext_ln138 sc_in sc_lv 4 signal 26 } 
	{ conv1_acc_V_address0 sc_out sc_lv 13 signal 27 } 
	{ conv1_acc_V_ce0 sc_out sc_logic 1 signal 27 } 
	{ conv1_acc_V_we0 sc_out sc_logic 1 signal 27 } 
	{ conv1_acc_V_d0 sc_out sc_lv 12 signal 27 } 
}
set NewPortList {[ 
	{ "name": "ap_clk", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "clock", "bundle":{"name": "ap_clk", "role": "default" }} , 
 	{ "name": "ap_rst", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "reset", "bundle":{"name": "ap_rst", "role": "default" }} , 
 	{ "name": "ap_start", "direction": "in", "datatype": "sc_logic", "bitwidth":1, "type": "start", "bundle":{"name": "ap_start", "role": "default" }} , 
 	{ "name": "ap_done", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "predone", "bundle":{"name": "ap_done", "role": "default" }} , 
 	{ "name": "ap_idle", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "done", "bundle":{"name": "ap_idle", "role": "default" }} , 
 	{ "name": "ap_ready", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "ready", "bundle":{"name": "ap_ready", "role": "default" }} , 
 	{ "name": "empty", "direction": "in", "datatype": "sc_lv", "bitwidth":9, "type": "signal", "bundle":{"name": "empty", "role": "default" }} , 
 	{ "name": "input_V_address0", "direction": "out", "datatype": "sc_lv", "bitwidth":10, "type": "signal", "bundle":{"name": "input_V", "role": "address0" }} , 
 	{ "name": "input_V_ce0", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "input_V", "role": "ce0" }} , 
 	{ "name": "input_V_q0", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "input_V", "role": "q0" }} , 
 	{ "name": "input_V_address1", "direction": "out", "datatype": "sc_lv", "bitwidth":10, "type": "signal", "bundle":{"name": "input_V", "role": "address1" }} , 
 	{ "name": "input_V_ce1", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "input_V", "role": "ce1" }} , 
 	{ "name": "input_V_q1", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "input_V", "role": "q1" }} , 
 	{ "name": "input_V_address2", "direction": "out", "datatype": "sc_lv", "bitwidth":10, "type": "signal", "bundle":{"name": "input_V", "role": "address2" }} , 
 	{ "name": "input_V_ce2", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "input_V", "role": "ce2" }} , 
 	{ "name": "input_V_q2", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "input_V", "role": "q2" }} , 
 	{ "name": "input_V_address3", "direction": "out", "datatype": "sc_lv", "bitwidth":10, "type": "signal", "bundle":{"name": "input_V", "role": "address3" }} , 
 	{ "name": "input_V_ce3", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "input_V", "role": "ce3" }} , 
 	{ "name": "input_V_q3", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "input_V", "role": "q3" }} , 
 	{ "name": "input_V_address4", "direction": "out", "datatype": "sc_lv", "bitwidth":10, "type": "signal", "bundle":{"name": "input_V", "role": "address4" }} , 
 	{ "name": "input_V_ce4", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "input_V", "role": "ce4" }} , 
 	{ "name": "input_V_q4", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "input_V", "role": "q4" }} , 
 	{ "name": "input_V_address5", "direction": "out", "datatype": "sc_lv", "bitwidth":10, "type": "signal", "bundle":{"name": "input_V", "role": "address5" }} , 
 	{ "name": "input_V_ce5", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "input_V", "role": "ce5" }} , 
 	{ "name": "input_V_q5", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "input_V", "role": "q5" }} , 
 	{ "name": "input_V_address6", "direction": "out", "datatype": "sc_lv", "bitwidth":10, "type": "signal", "bundle":{"name": "input_V", "role": "address6" }} , 
 	{ "name": "input_V_ce6", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "input_V", "role": "ce6" }} , 
 	{ "name": "input_V_q6", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "input_V", "role": "q6" }} , 
 	{ "name": "input_V_address7", "direction": "out", "datatype": "sc_lv", "bitwidth":10, "type": "signal", "bundle":{"name": "input_V", "role": "address7" }} , 
 	{ "name": "input_V_ce7", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "input_V", "role": "ce7" }} , 
 	{ "name": "input_V_q7", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "input_V", "role": "q7" }} , 
 	{ "name": "input_V_address8", "direction": "out", "datatype": "sc_lv", "bitwidth":10, "type": "signal", "bundle":{"name": "input_V", "role": "address8" }} , 
 	{ "name": "input_V_ce8", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "input_V", "role": "ce8" }} , 
 	{ "name": "input_V_q8", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "input_V", "role": "q8" }} , 
 	{ "name": "input_V_address9", "direction": "out", "datatype": "sc_lv", "bitwidth":10, "type": "signal", "bundle":{"name": "input_V", "role": "address9" }} , 
 	{ "name": "input_V_ce9", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "input_V", "role": "ce9" }} , 
 	{ "name": "input_V_q9", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "input_V", "role": "q9" }} , 
 	{ "name": "input_V_address10", "direction": "out", "datatype": "sc_lv", "bitwidth":10, "type": "signal", "bundle":{"name": "input_V", "role": "address10" }} , 
 	{ "name": "input_V_ce10", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "input_V", "role": "ce10" }} , 
 	{ "name": "input_V_q10", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "input_V", "role": "q10" }} , 
 	{ "name": "input_V_address11", "direction": "out", "datatype": "sc_lv", "bitwidth":10, "type": "signal", "bundle":{"name": "input_V", "role": "address11" }} , 
 	{ "name": "input_V_ce11", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "input_V", "role": "ce11" }} , 
 	{ "name": "input_V_q11", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "input_V", "role": "q11" }} , 
 	{ "name": "input_V_address12", "direction": "out", "datatype": "sc_lv", "bitwidth":10, "type": "signal", "bundle":{"name": "input_V", "role": "address12" }} , 
 	{ "name": "input_V_ce12", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "input_V", "role": "ce12" }} , 
 	{ "name": "input_V_q12", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "input_V", "role": "q12" }} , 
 	{ "name": "sext_ln178", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln178", "role": "default" }} , 
 	{ "name": "sext_ln172", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln172", "role": "default" }} , 
 	{ "name": "sext_ln178_1", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln178_1", "role": "default" }} , 
 	{ "name": "sext_ln172_1", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln172_1", "role": "default" }} , 
 	{ "name": "sext_ln178_2", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln178_2", "role": "default" }} , 
 	{ "name": "sext_ln172_2", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln172_2", "role": "default" }} , 
 	{ "name": "sext_ln178_3", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln178_3", "role": "default" }} , 
 	{ "name": "sext_ln172_3", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln172_3", "role": "default" }} , 
 	{ "name": "sext_ln178_4", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln178_4", "role": "default" }} , 
 	{ "name": "sext_ln172_4", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln172_4", "role": "default" }} , 
 	{ "name": "sext_ln178_5", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln178_5", "role": "default" }} , 
 	{ "name": "sext_ln172_5", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln172_5", "role": "default" }} , 
 	{ "name": "sext_ln178_6", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln178_6", "role": "default" }} , 
 	{ "name": "sext_ln172_6", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln172_6", "role": "default" }} , 
 	{ "name": "sext_ln178_7", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln178_7", "role": "default" }} , 
 	{ "name": "sext_ln172_7", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln172_7", "role": "default" }} , 
 	{ "name": "sext_ln178_8", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln178_8", "role": "default" }} , 
 	{ "name": "sext_ln172_8", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln172_8", "role": "default" }} , 
 	{ "name": "sext_ln178_9", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln178_9", "role": "default" }} , 
 	{ "name": "sext_ln172_9", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln172_9", "role": "default" }} , 
 	{ "name": "sext_ln178_10", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln178_10", "role": "default" }} , 
 	{ "name": "sext_ln172_10", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln172_10", "role": "default" }} , 
 	{ "name": "sext_ln178_11", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln178_11", "role": "default" }} , 
 	{ "name": "sext_ln172_11", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln172_11", "role": "default" }} , 
 	{ "name": "sext_ln138", "direction": "in", "datatype": "sc_lv", "bitwidth":4, "type": "signal", "bundle":{"name": "sext_ln138", "role": "default" }} , 
 	{ "name": "conv1_acc_V_address0", "direction": "out", "datatype": "sc_lv", "bitwidth":13, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "address0" }} , 
 	{ "name": "conv1_acc_V_ce0", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "ce0" }} , 
 	{ "name": "conv1_acc_V_we0", "direction": "out", "datatype": "sc_logic", "bitwidth":1, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "we0" }} , 
 	{ "name": "conv1_acc_V_d0", "direction": "out", "datatype": "sc_lv", "bitwidth":12, "type": "signal", "bundle":{"name": "conv1_acc_V", "role": "d0" }}  ]}

set RtlHierarchyInfo {[
	{"ID" : "0", "Level" : "0", "Path" : "`AUTOTB_DUT_INST", "Parent" : "", "Child" : ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26"],
		"CDFG" : "lenet_w4a4_top_Pipeline_OUT_ROW_OUT_COL",
		"Protocol" : "ap_ctrl_hs",
		"ControlExist" : "1", "ap_start" : "1", "ap_ready" : "1", "ap_done" : "1", "ap_continue" : "0", "ap_idle" : "1", "real_start" : "0",
		"Pipeline" : "None", "UnalignedPipeline" : "0", "RewindPipeline" : "0", "ProcessNetwork" : "0",
		"II" : "0",
		"VariableLatency" : "1", "ExactLatency" : "-1", "EstimateLatencyMin" : "1576", "EstimateLatencyMax" : "1576",
		"Combinational" : "0",
		"Datapath" : "0",
		"ClockEnable" : "0",
		"HasSubDataflow" : "0",
		"InDataflowNetwork" : "0",
		"HasNonBlockingOperation" : "0",
		"IsBlackBox" : "0",
		"Port" : [
			{"Name" : "empty", "Type" : "None", "Direction" : "I"},
			{"Name" : "input_V", "Type" : "Memory", "Direction" : "I"},
			{"Name" : "sext_ln178", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln172", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln178_1", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln172_1", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln178_2", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln172_2", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln178_3", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln172_3", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln178_4", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln172_4", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln178_5", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln172_5", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln178_6", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln172_6", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln178_7", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln172_7", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln178_8", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln172_8", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln178_9", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln172_9", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln178_10", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln172_10", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln178_11", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln172_11", "Type" : "None", "Direction" : "I"},
			{"Name" : "sext_ln138", "Type" : "None", "Direction" : "I"},
			{"Name" : "conv1_acc_V", "Type" : "Memory", "Direction" : "O"}],
		"Loop" : [
			{"Name" : "OUT_ROW_OUT_COL", "PipelineType" : "UPC",
				"LoopDec" : {"FSMBitwidth" : "2", "FirstState" : "ap_ST_fsm_pp0_stage0", "FirstStateIter" : "ap_enable_reg_pp0_iter0", "FirstStateBlock" : "ap_block_pp0_stage0_subdone", "LastState" : "ap_ST_fsm_pp0_stage0", "LastStateIter" : "ap_enable_reg_pp0_iter4", "LastStateBlock" : "ap_block_pp0_stage0_subdone", "QuitState" : "ap_ST_fsm_pp0_stage0", "QuitStateIter" : "ap_enable_reg_pp0_iter4", "QuitStateBlock" : "ap_block_pp0_stage0_subdone", "OneDepthLoop" : "0", "has_ap_ctrl" : "1", "has_continue" : "0"}}]},
	{"ID" : "1", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mul_4s_4s_8_1_1_U9", "Parent" : "0"},
	{"ID" : "2", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mul_4s_4s_8_1_1_U10", "Parent" : "0"},
	{"ID" : "3", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mul_4s_4s_8_1_1_U11", "Parent" : "0"},
	{"ID" : "4", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mul_4s_4s_8_1_1_U12", "Parent" : "0"},
	{"ID" : "5", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mul_4s_4s_8_1_1_U13", "Parent" : "0"},
	{"ID" : "6", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mul_4s_4s_8_1_1_U14", "Parent" : "0"},
	{"ID" : "7", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mul_4s_4s_8_1_1_U15", "Parent" : "0"},
	{"ID" : "8", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mul_4s_4s_8_1_1_U16", "Parent" : "0"},
	{"ID" : "9", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mul_4s_4s_8_1_1_U17", "Parent" : "0"},
	{"ID" : "10", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_8s_9_4_1_U18", "Parent" : "0"},
	{"ID" : "11", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_8s_9_4_1_U19", "Parent" : "0"},
	{"ID" : "12", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_9s_9_4_1_U20", "Parent" : "0"},
	{"ID" : "13", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_8s_9_4_1_U21", "Parent" : "0"},
	{"ID" : "14", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_8s_9_4_1_U22", "Parent" : "0"},
	{"ID" : "15", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_8s_9_4_1_U23", "Parent" : "0"},
	{"ID" : "16", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_8s_9_4_1_U24", "Parent" : "0"},
	{"ID" : "17", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_8s_9_4_1_U25", "Parent" : "0"},
	{"ID" : "18", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_9s_9_4_1_U26", "Parent" : "0"},
	{"ID" : "19", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_9s_9_4_1_U27", "Parent" : "0"},
	{"ID" : "20", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_9s_9_4_1_U28", "Parent" : "0"},
	{"ID" : "21", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_9s_9_4_1_U29", "Parent" : "0"},
	{"ID" : "22", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_9s_9_4_1_U30", "Parent" : "0"},
	{"ID" : "23", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_8s_9_4_1_U31", "Parent" : "0"},
	{"ID" : "24", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_8s_9_4_1_U32", "Parent" : "0"},
	{"ID" : "25", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.mac_muladd_4s_4s_9s_9_4_1_U33", "Parent" : "0"},
	{"ID" : "26", "Level" : "1", "Path" : "`AUTOTB_DUT_INST.flow_control_loop_pipe_sequential_init_U", "Parent" : "0"}]}


set ArgLastReadFirstWriteLatency {
	lenet_w4a4_top_Pipeline_OUT_ROW_OUT_COL {
		empty {Type I LastRead 0 FirstWrite -1}
		input_V {Type I LastRead 3 FirstWrite -1}
		sext_ln178 {Type I LastRead 0 FirstWrite -1}
		sext_ln172 {Type I LastRead 0 FirstWrite -1}
		sext_ln178_1 {Type I LastRead 0 FirstWrite -1}
		sext_ln172_1 {Type I LastRead 0 FirstWrite -1}
		sext_ln178_2 {Type I LastRead 0 FirstWrite -1}
		sext_ln172_2 {Type I LastRead 0 FirstWrite -1}
		sext_ln178_3 {Type I LastRead 0 FirstWrite -1}
		sext_ln172_3 {Type I LastRead 0 FirstWrite -1}
		sext_ln178_4 {Type I LastRead 0 FirstWrite -1}
		sext_ln172_4 {Type I LastRead 0 FirstWrite -1}
		sext_ln178_5 {Type I LastRead 0 FirstWrite -1}
		sext_ln172_5 {Type I LastRead 0 FirstWrite -1}
		sext_ln178_6 {Type I LastRead 0 FirstWrite -1}
		sext_ln172_6 {Type I LastRead 0 FirstWrite -1}
		sext_ln178_7 {Type I LastRead 0 FirstWrite -1}
		sext_ln172_7 {Type I LastRead 0 FirstWrite -1}
		sext_ln178_8 {Type I LastRead 0 FirstWrite -1}
		sext_ln172_8 {Type I LastRead 0 FirstWrite -1}
		sext_ln178_9 {Type I LastRead 0 FirstWrite -1}
		sext_ln172_9 {Type I LastRead 0 FirstWrite -1}
		sext_ln178_10 {Type I LastRead 0 FirstWrite -1}
		sext_ln172_10 {Type I LastRead 0 FirstWrite -1}
		sext_ln178_11 {Type I LastRead 0 FirstWrite -1}
		sext_ln172_11 {Type I LastRead 0 FirstWrite -1}
		sext_ln138 {Type I LastRead 0 FirstWrite -1}
		conv1_acc_V {Type O LastRead -1 FirstWrite 8}}}

set hasDtUnsupportedChannel 0

set PerformanceInfo {[
	{"Name" : "Latency", "Min" : "1576", "Max" : "1576"}
	, {"Name" : "Interval", "Min" : "1576", "Max" : "1576"}
]}

set PipelineEnableSignalInfo {[
	{"Pipeline" : "0", "EnableSignal" : "ap_enable_pp0"}
]}

set Spec2ImplPortList { 
	empty { ap_none {  { empty in_data 0 9 } } }
	input_V { ap_memory {  { input_V_address0 mem_address 1 10 }  { input_V_ce0 mem_ce 1 1 }  { input_V_q0 in_data 0 4 }  { input_V_address1 MemPortADDR2 1 10 }  { input_V_ce1 MemPortCE2 1 1 }  { input_V_q1 in_data 0 4 }  { input_V_address2 MemPortADDR2 1 10 }  { input_V_ce2 MemPortCE2 1 1 }  { input_V_q2 in_data 0 4 }  { input_V_address3 MemPortADDR2 1 10 }  { input_V_ce3 MemPortCE2 1 1 }  { input_V_q3 MemPortDOUT2 0 4 }  { input_V_address4 MemPortADDR2 1 10 }  { input_V_ce4 MemPortCE2 1 1 }  { input_V_q4 in_data 0 4 }  { input_V_address5 MemPortADDR2 1 10 }  { input_V_ce5 MemPortCE2 1 1 }  { input_V_q5 in_data 0 4 }  { input_V_address6 MemPortADDR2 1 10 }  { input_V_ce6 MemPortCE2 1 1 }  { input_V_q6 in_data 0 4 }  { input_V_address7 MemPortADDR2 1 10 }  { input_V_ce7 MemPortCE2 1 1 }  { input_V_q7 MemPortDOUT2 0 4 }  { input_V_address8 MemPortADDR2 1 10 }  { input_V_ce8 MemPortCE2 1 1 }  { input_V_q8 MemPortDOUT2 0 4 }  { input_V_address9 MemPortADDR2 1 10 }  { input_V_ce9 MemPortCE2 1 1 }  { input_V_q9 in_data 0 4 }  { input_V_address10 MemPortADDR2 1 10 }  { input_V_ce10 MemPortCE2 1 1 }  { input_V_q10 in_data 0 4 }  { input_V_address11 MemPortADDR2 1 10 }  { input_V_ce11 MemPortCE2 1 1 }  { input_V_q11 in_data 0 4 }  { input_V_address12 MemPortADDR2 1 10 }  { input_V_ce12 MemPortCE2 1 1 }  { input_V_q12 MemPortDOUT2 0 4 } } }
	sext_ln178 { ap_none {  { sext_ln178 in_data 0 4 } } }
	sext_ln172 { ap_none {  { sext_ln172 in_data 0 4 } } }
	sext_ln178_1 { ap_none {  { sext_ln178_1 in_data 0 4 } } }
	sext_ln172_1 { ap_none {  { sext_ln172_1 in_data 0 4 } } }
	sext_ln178_2 { ap_none {  { sext_ln178_2 in_data 0 4 } } }
	sext_ln172_2 { ap_none {  { sext_ln172_2 in_data 0 4 } } }
	sext_ln178_3 { ap_none {  { sext_ln178_3 in_data 0 4 } } }
	sext_ln172_3 { ap_none {  { sext_ln172_3 in_data 0 4 } } }
	sext_ln178_4 { ap_none {  { sext_ln178_4 in_data 0 4 } } }
	sext_ln172_4 { ap_none {  { sext_ln172_4 in_data 0 4 } } }
	sext_ln178_5 { ap_none {  { sext_ln178_5 in_data 0 4 } } }
	sext_ln172_5 { ap_none {  { sext_ln172_5 in_data 0 4 } } }
	sext_ln178_6 { ap_none {  { sext_ln178_6 in_data 0 4 } } }
	sext_ln172_6 { ap_none {  { sext_ln172_6 in_data 0 4 } } }
	sext_ln178_7 { ap_none {  { sext_ln178_7 in_data 0 4 } } }
	sext_ln172_7 { ap_none {  { sext_ln172_7 in_data 0 4 } } }
	sext_ln178_8 { ap_none {  { sext_ln178_8 in_data 0 4 } } }
	sext_ln172_8 { ap_none {  { sext_ln172_8 in_data 0 4 } } }
	sext_ln178_9 { ap_none {  { sext_ln178_9 in_data 0 4 } } }
	sext_ln172_9 { ap_none {  { sext_ln172_9 in_data 0 4 } } }
	sext_ln178_10 { ap_none {  { sext_ln178_10 in_data 0 4 } } }
	sext_ln172_10 { ap_none {  { sext_ln172_10 in_data 0 4 } } }
	sext_ln178_11 { ap_none {  { sext_ln178_11 in_data 0 4 } } }
	sext_ln172_11 { ap_none {  { sext_ln172_11 in_data 0 4 } } }
	sext_ln138 { ap_none {  { sext_ln138 in_data 0 4 } } }
	conv1_acc_V { ap_memory {  { conv1_acc_V_address0 mem_address 1 13 }  { conv1_acc_V_ce0 mem_ce 1 1 }  { conv1_acc_V_we0 mem_we 1 1 }  { conv1_acc_V_d0 mem_din 1 12 } } }
}
