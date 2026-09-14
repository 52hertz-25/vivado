# ============================================================
# LeNet-5 W8A8 Vivado independent review project
# Vivado 2022.2
#
# This script:
# 1. Extracts the W8A8 HLS IP
# 2. Copies the original FP32 Vivado project
# 3. Replaces lenet_full_top with lenet_w8a8_top
# 4. Changes SmartConnect from 4 inputs to 3 inputs
# 5. Reconnects AXI, clock and reset
# 6. Assigns the AXI-Lite control address
# 7. Validates and saves the copied Block Design
# ============================================================

set repo_root {D:/GitHub/vivado/vivado}

set original_xpr [file join \
    $repo_root \
    lenet_project \
    vivado \
    LeNet_Zynq_System \
    LeNet_Zynq_System.xpr]

set w8a8_root [file join \
    $repo_root \
    F_Quantization_W8A8 \
    hls_w8a8]

set ip_zip [file join \
    $w8a8_root \
    export \
    lenet_w8a8_top_ip.zip]

set ip_repo [file join \
    $w8a8_root \
    vivado_review \
    ip_repo \
    lenet_w8a8_top]

set review_root [file join \
    $w8a8_root \
    vivado_review \
    project]

set review_name LeNet_W8A8_Review

puts "============================================================"
puts "LeNet-5 W8A8 Vivado review project"
puts "Original project : $original_xpr"
puts "W8A8 IP ZIP      : $ip_zip"
puts "W8A8 IP repo     : $ip_repo"
puts "Review project   : $review_root"
puts "============================================================"

# ------------------------------------------------------------
# Check inputs
# ------------------------------------------------------------

if {![file exists $original_xpr]} {
    puts "ERROR: original Vivado project not found:"
    puts $original_xpr
    exit 2
}

if {![file exists $ip_zip]} {
    puts "ERROR: W8A8 IP ZIP not found:"
    puts $ip_zip
    exit 2
}

# ------------------------------------------------------------
# Extract packaged IP
# ------------------------------------------------------------

file mkdir $ip_repo

puts "Extracting W8A8 IP..."

exec powershell.exe \
    -NoProfile \
    -Command \
    "Expand-Archive -LiteralPath '$ip_zip' -DestinationPath '$ip_repo' -Force"

set component_xml [file join $ip_repo component.xml]

if {![file exists $component_xml]} {
    puts "ERROR: component.xml was not extracted:"
    puts $component_xml
    exit 2
}

puts "W8A8 IP extraction completed."

# ------------------------------------------------------------
# Open original project and save an independent copy
# ------------------------------------------------------------

open_project $original_xpr

puts "Creating an independent Vivado project copy..."

file mkdir $review_root

save_project_as \
    -force \
    $review_name \
    $review_root

puts "Current project: [current_project]"
puts "Project path   : [get_property DIRECTORY [current_project]]"

# ------------------------------------------------------------
# Add the W8A8 IP repository
# ------------------------------------------------------------

set old_repositories [get_property ip_repo_paths [current_project]]

set_property ip_repo_paths \
    [concat [list $ip_repo] $old_repositories] \
    [current_project]

update_ip_catalog

set w8a8_vlnv [get_ipdefs -all -quiet \
    -filter {VLNV == "user.org:hls:lenet_w8a8_top:1.0"}]

if {[llength $w8a8_vlnv] == 0} {
    puts "ERROR: user.org:hls:lenet_w8a8_top:1.0 was not found."
    puts "Check the exported component.xml file."
    close_project
    exit 2
}

puts "W8A8 IP definition found:"
puts $w8a8_vlnv

# ------------------------------------------------------------
# Open the existing Block Design
# ------------------------------------------------------------

set bd_file [get_files -quiet {*/lenet_system.bd}]

if {[llength $bd_file] == 0} {
    puts "ERROR: lenet_system.bd was not found."
    close_project
    exit 2
}

open_bd_design $bd_file

set old_hls [get_bd_cells -quiet lenet_full_top_0]
set ps7     [get_bd_cells -quiet processing_system7_0]
set ctrl_ic [get_bd_cells -quiet ps7_0_axi_periph]
set data_sc [get_bd_cells -quiet smartconnect_0]

if {[llength $old_hls] == 0} {
    puts "ERROR: original HLS cell lenet_full_top_0 was not found."
    close_project
    exit 2
}

if {[llength $ps7] == 0 ||
    [llength $ctrl_ic] == 0 ||
    [llength $data_sc] == 0} {

    puts "ERROR: required Zynq or AXI infrastructure is missing."
    close_project
    exit 2
}

# ------------------------------------------------------------
# Preserve clock and reset nets before deleting the old IP
# ------------------------------------------------------------

set old_clk_pin [get_bd_pins -quiet lenet_full_top_0/ap_clk]
set old_rst_pin [get_bd_pins -quiet lenet_full_top_0/ap_rst_n]

set clock_nets [get_bd_nets -quiet -of_objects $old_clk_pin]
set reset_nets [get_bd_nets -quiet -of_objects $old_rst_pin]

if {[llength $clock_nets] == 0} {
    puts "ERROR: the old HLS clock net was not found."
    close_project
    exit 2
}

if {[llength $reset_nets] == 0} {
    puts "ERROR: the old HLS reset net was not found."
    close_project
    exit 2
}

set hls_clock_net [lindex $clock_nets 0]
set hls_reset_net [lindex $reset_nets 0]

puts "Preserved clock net: $hls_clock_net"
puts "Preserved reset net: $hls_reset_net"

# ------------------------------------------------------------
# Delete the FP32 HLS IP
# ------------------------------------------------------------

puts "Removing original FP32 HLS cell..."

delete_bd_objs $old_hls

# ------------------------------------------------------------
# Configure SmartConnect for three W8A8 memory masters
# ------------------------------------------------------------

set_property CONFIG.NUM_SI {3} $data_sc

# ------------------------------------------------------------
# Create the new W8A8 HLS IP
# ------------------------------------------------------------

puts "Creating W8A8 HLS cell..."

set new_hls [create_bd_cell \
    -type ip \
    -vlnv user.org:hls:lenet_w8a8_top:1.0 \
    lenet_w8a8_top_0]

# ------------------------------------------------------------
# Connect clock and reset
# ------------------------------------------------------------

connect_bd_net \
    $hls_clock_net \
    [get_bd_pins lenet_w8a8_top_0/ap_clk]

connect_bd_net \
    $hls_reset_net \
    [get_bd_pins lenet_w8a8_top_0/ap_rst_n]

# ------------------------------------------------------------
# Connect AXI-Lite control interface
# ------------------------------------------------------------

connect_bd_intf_net \
    [get_bd_intf_pins ps7_0_axi_periph/M00_AXI] \
    [get_bd_intf_pins lenet_w8a8_top_0/s_axi_control]

# ------------------------------------------------------------
# Connect three AXI memory master interfaces
# ------------------------------------------------------------

connect_bd_intf_net \
    [get_bd_intf_pins lenet_w8a8_top_0/m_axi_gmem0] \
    [get_bd_intf_pins smartconnect_0/S00_AXI]

connect_bd_intf_net \
    [get_bd_intf_pins lenet_w8a8_top_0/m_axi_gmem1] \
    [get_bd_intf_pins smartconnect_0/S01_AXI]

connect_bd_intf_net \
    [get_bd_intf_pins lenet_w8a8_top_0/m_axi_gmem2] \
    [get_bd_intf_pins smartconnect_0/S02_AXI]

# ------------------------------------------------------------
# Recreate address mappings
# ------------------------------------------------------------

assign_bd_address

set control_segment \
    [get_bd_addr_segs -quiet lenet_w8a8_top_0/s_axi_control/Reg]

if {[llength $control_segment] > 0} {
    set control_mapping [get_bd_addr_segs -quiet \
        processing_system7_0/Data/SEG_lenet_w8a8_top_0_Reg]

    if {[llength $control_mapping] > 0} {
        set_property offset 0x40000000 $control_mapping
        set_property range 64K $control_mapping
    }
}

# ------------------------------------------------------------
# Validate the new Block Design
# ------------------------------------------------------------

puts "============================================================"
puts "Validating the W8A8 Block Design..."
puts "============================================================"

validate_bd_design -force

save_bd_design

generate_target all [get_files {*/lenet_system.bd}]

# ------------------------------------------------------------
# Print review information
# ------------------------------------------------------------

puts "================ W8A8 BD CELLS ================"

foreach cell [get_bd_cells] {
    puts "$cell | [get_property VLNV $cell]"
}

puts "================ W8A8 INTERFACE NETS ================"

foreach net [get_bd_intf_nets] {
    puts "NET: $net"

    foreach pin [get_bd_intf_pins -of_objects $net] {
        puts "  $pin"
    }
}

puts "================ W8A8 ADDRESS MAP ================"

foreach seg [get_bd_addr_segs] {
    puts "$seg | OFFSET=[get_property OFFSET $seg] | RANGE=[get_property RANGE $seg]"
}

puts "============================================================"
puts "W8A8 VIVADO BLOCK DESIGN VALIDATION PASSED"
puts "Independent project:"
puts [get_property DIRECTORY [current_project]]
puts "============================================================"

close_project
exit