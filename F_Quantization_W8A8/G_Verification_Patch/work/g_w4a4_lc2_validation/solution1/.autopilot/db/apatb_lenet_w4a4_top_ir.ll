; ModuleID = 'D:/GitHub/vivado/vivado/F_Quantization_W8A8/G_Verification_Patch/work/g_w4a4_lc2_validation/solution1/.autopilot/db/a.g.ld.5.gdce.bc'
source_filename = "llvm-link"
target datalayout = "e-m:e-i64:64-i128:128-i256:256-i512:512-i1024:1024-i2048:2048-i4096:4096-n8:16:32:64-S128-v16:16-v24:32-v32:32-v48:64-v96:128-v192:256-v256:256-v512:512-v1024:1024"
target triple = "fpga64-xilinx-none"

%"struct.ap_uint<8>" = type { %"struct.ap_int_base<8, false>" }
%"struct.ap_int_base<8, false>" = type { %"struct.ssdm_int<8, false>" }
%"struct.ssdm_int<8, false>" = type { i8 }
%"struct.ap_int<32>" = type { %"struct.ap_int_base<32, true>" }
%"struct.ap_int_base<32, true>" = type { %"struct.ssdm_int<32, true>" }
%"struct.ssdm_int<32, true>" = type { i32 }

; Function Attrs: noinline
define void @apatb_lenet_w4a4_top_ir(%"struct.ap_uint<8>"* noalias nocapture nonnull readonly "fpga.decayed.dim.hint"="512" %feature_in, %"struct.ap_uint<8>"* noalias nocapture nonnull readonly "fpga.decayed.dim.hint"="30735" %weight, %"struct.ap_int<32>"* noalias nocapture nonnull "fpga.decayed.dim.hint"="10" %logits) local_unnamed_addr #0 {
entry:
  %feature_in_copy = alloca [512 x i8], align 512
  %malloccall = call i8* @malloc(i64 30735)
  %weight_copy = bitcast i8* %malloccall to [30735 x i8]*
  %logits_copy = alloca [10 x i32], align 512
  %0 = bitcast %"struct.ap_uint<8>"* %feature_in to [512 x %"struct.ap_uint<8>"]*
  %1 = bitcast %"struct.ap_uint<8>"* %weight to [30735 x %"struct.ap_uint<8>"]*
  %2 = bitcast %"struct.ap_int<32>"* %logits to [10 x %"struct.ap_int<32>"]*
  call fastcc void @copy_in([512 x %"struct.ap_uint<8>"]* nonnull %0, [512 x i8]* nonnull align 512 %feature_in_copy, [30735 x %"struct.ap_uint<8>"]* nonnull %1, [30735 x i8]* %weight_copy, [10 x %"struct.ap_int<32>"]* nonnull %2, [10 x i32]* nonnull align 512 %logits_copy)
  %3 = getelementptr [512 x i8], [512 x i8]* %feature_in_copy, i32 0, i32 0
  %4 = getelementptr [10 x i32], [10 x i32]* %logits_copy, i32 0, i32 0
  call void @apatb_lenet_w4a4_top_hw(i8* %3, i8* %malloccall, i32* %4)
  call void @copy_back([512 x %"struct.ap_uint<8>"]* %0, [512 x i8]* %feature_in_copy, [30735 x %"struct.ap_uint<8>"]* %1, [30735 x i8]* %weight_copy, [10 x %"struct.ap_int<32>"]* %2, [10 x i32]* %logits_copy)
  call void @free(i8* %malloccall)
  ret void
}

declare noalias i8* @malloc(i64) local_unnamed_addr

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @copy_in([512 x %"struct.ap_uint<8>"]* noalias readonly "unpacked"="0", [512 x i8]* noalias nocapture align 512 "unpacked"="1.0.0.0", [30735 x %"struct.ap_uint<8>"]* noalias readonly "unpacked"="2", [30735 x i8]* noalias nocapture "unpacked"="3.0.0.0", [10 x %"struct.ap_int<32>"]* noalias readonly "unpacked"="4", [10 x i32]* noalias nocapture align 512 "unpacked"="5.0.0.0") unnamed_addr #1 {
entry:
  call fastcc void @"onebyonecpy_hls.p0a512struct.ap_uint<8>"([512 x i8]* align 512 %1, [512 x %"struct.ap_uint<8>"]* %0)
  call fastcc void @"onebyonecpy_hls.p0a30735struct.ap_uint<8>.89"([30735 x i8]* %3, [30735 x %"struct.ap_uint<8>"]* %2)
  call fastcc void @"onebyonecpy_hls.p0a10struct.ap_int<32>"([10 x i32]* align 512 %5, [10 x %"struct.ap_int<32>"]* %4)
  ret void
}

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @copy_out([512 x %"struct.ap_uint<8>"]* noalias "unpacked"="0", [512 x i8]* noalias nocapture readonly align 512 "unpacked"="1.0.0.0", [30735 x %"struct.ap_uint<8>"]* noalias "unpacked"="2", [30735 x i8]* noalias nocapture readonly "unpacked"="3.0.0.0", [10 x %"struct.ap_int<32>"]* noalias "unpacked"="4", [10 x i32]* noalias nocapture readonly align 512 "unpacked"="5.0.0.0") unnamed_addr #2 {
entry:
  call fastcc void @"onebyonecpy_hls.p0a512struct.ap_uint<8>.129"([512 x %"struct.ap_uint<8>"]* %0, [512 x i8]* align 512 %1)
  call fastcc void @"onebyonecpy_hls.p0a30735struct.ap_uint<8>"([30735 x %"struct.ap_uint<8>"]* %2, [30735 x i8]* %3)
  call fastcc void @"onebyonecpy_hls.p0a10struct.ap_int<32>.65"([10 x %"struct.ap_int<32>"]* %4, [10 x i32]* align 512 %5)
  ret void
}

declare void @free(i8*) local_unnamed_addr

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @"onebyonecpy_hls.p0a10struct.ap_int<32>.65"([10 x %"struct.ap_int<32>"]* noalias "unpacked"="0", [10 x i32]* noalias nocapture readonly align 512 "unpacked"="1.0.0.0") unnamed_addr #3 {
entry:
  %2 = icmp eq [10 x %"struct.ap_int<32>"]* %0, null
  br i1 %2, label %ret, label %copy

copy:                                             ; preds = %entry
  br label %for.loop

for.loop:                                         ; preds = %for.loop, %copy
  %for.loop.idx1 = phi i64 [ 0, %copy ], [ %for.loop.idx.next, %for.loop ]
  %src.addr.0.0.05 = getelementptr [10 x i32], [10 x i32]* %1, i64 0, i64 %for.loop.idx1
  %dst.addr.0.0.06 = getelementptr [10 x %"struct.ap_int<32>"], [10 x %"struct.ap_int<32>"]* %0, i64 0, i64 %for.loop.idx1, i32 0, i32 0, i32 0
  %3 = load i32, i32* %src.addr.0.0.05, align 4
  store i32 %3, i32* %dst.addr.0.0.06, align 4
  %for.loop.idx.next = add nuw nsw i64 %for.loop.idx1, 1
  %exitcond = icmp ne i64 %for.loop.idx.next, 10
  br i1 %exitcond, label %for.loop, label %ret

ret:                                              ; preds = %for.loop, %entry
  ret void
}

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @"onebyonecpy_hls.p0a10struct.ap_int<32>"([10 x i32]* noalias nocapture align 512 "unpacked"="0.0.0.0", [10 x %"struct.ap_int<32>"]* noalias readonly "unpacked"="1") unnamed_addr #3 {
entry:
  %2 = icmp eq [10 x %"struct.ap_int<32>"]* %1, null
  br i1 %2, label %ret, label %copy

copy:                                             ; preds = %entry
  br label %for.loop

for.loop:                                         ; preds = %for.loop, %copy
  %for.loop.idx1 = phi i64 [ 0, %copy ], [ %for.loop.idx.next, %for.loop ]
  %src.addr.0.0.05 = getelementptr [10 x %"struct.ap_int<32>"], [10 x %"struct.ap_int<32>"]* %1, i64 0, i64 %for.loop.idx1, i32 0, i32 0, i32 0
  %dst.addr.0.0.06 = getelementptr [10 x i32], [10 x i32]* %0, i64 0, i64 %for.loop.idx1
  %3 = load i32, i32* %src.addr.0.0.05, align 4
  store i32 %3, i32* %dst.addr.0.0.06, align 4
  %for.loop.idx.next = add nuw nsw i64 %for.loop.idx1, 1
  %exitcond = icmp ne i64 %for.loop.idx.next, 10
  br i1 %exitcond, label %for.loop, label %ret

ret:                                              ; preds = %for.loop, %entry
  ret void
}

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @"onebyonecpy_hls.p0a30735struct.ap_uint<8>.89"([30735 x i8]* noalias nocapture "unpacked"="0.0.0.0", [30735 x %"struct.ap_uint<8>"]* noalias readonly "unpacked"="1") unnamed_addr #3 {
entry:
  %2 = icmp eq [30735 x %"struct.ap_uint<8>"]* %1, null
  br i1 %2, label %ret, label %copy

copy:                                             ; preds = %entry
  br label %for.loop

for.loop:                                         ; preds = %for.loop, %copy
  %for.loop.idx1 = phi i64 [ 0, %copy ], [ %for.loop.idx.next, %for.loop ]
  %src.addr.0.0.05 = getelementptr [30735 x %"struct.ap_uint<8>"], [30735 x %"struct.ap_uint<8>"]* %1, i64 0, i64 %for.loop.idx1, i32 0, i32 0, i32 0
  %dst.addr.0.0.06 = getelementptr [30735 x i8], [30735 x i8]* %0, i64 0, i64 %for.loop.idx1
  %3 = load i8, i8* %src.addr.0.0.05, align 1
  store i8 %3, i8* %dst.addr.0.0.06, align 1
  %for.loop.idx.next = add nuw nsw i64 %for.loop.idx1, 1
  %exitcond = icmp ne i64 %for.loop.idx.next, 30735
  br i1 %exitcond, label %for.loop, label %ret

ret:                                              ; preds = %for.loop, %entry
  ret void
}

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @"onebyonecpy_hls.p0a30735struct.ap_uint<8>"([30735 x %"struct.ap_uint<8>"]* noalias "unpacked"="0", [30735 x i8]* noalias nocapture readonly "unpacked"="1.0.0.0") unnamed_addr #3 {
entry:
  %2 = icmp eq [30735 x %"struct.ap_uint<8>"]* %0, null
  br i1 %2, label %ret, label %copy

copy:                                             ; preds = %entry
  br label %for.loop

for.loop:                                         ; preds = %for.loop, %copy
  %for.loop.idx1 = phi i64 [ 0, %copy ], [ %for.loop.idx.next, %for.loop ]
  %src.addr.0.0.05 = getelementptr [30735 x i8], [30735 x i8]* %1, i64 0, i64 %for.loop.idx1
  %dst.addr.0.0.06 = getelementptr [30735 x %"struct.ap_uint<8>"], [30735 x %"struct.ap_uint<8>"]* %0, i64 0, i64 %for.loop.idx1, i32 0, i32 0, i32 0
  %3 = load i8, i8* %src.addr.0.0.05, align 1
  store i8 %3, i8* %dst.addr.0.0.06, align 1
  %for.loop.idx.next = add nuw nsw i64 %for.loop.idx1, 1
  %exitcond = icmp ne i64 %for.loop.idx.next, 30735
  br i1 %exitcond, label %for.loop, label %ret

ret:                                              ; preds = %for.loop, %entry
  ret void
}

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @"onebyonecpy_hls.p0a512struct.ap_uint<8>.129"([512 x %"struct.ap_uint<8>"]* noalias "unpacked"="0", [512 x i8]* noalias nocapture readonly align 512 "unpacked"="1.0.0.0") unnamed_addr #3 {
entry:
  %2 = icmp eq [512 x %"struct.ap_uint<8>"]* %0, null
  br i1 %2, label %ret, label %copy

copy:                                             ; preds = %entry
  br label %for.loop

for.loop:                                         ; preds = %for.loop, %copy
  %for.loop.idx1 = phi i64 [ 0, %copy ], [ %for.loop.idx.next, %for.loop ]
  %src.addr.0.0.05 = getelementptr [512 x i8], [512 x i8]* %1, i64 0, i64 %for.loop.idx1
  %dst.addr.0.0.06 = getelementptr [512 x %"struct.ap_uint<8>"], [512 x %"struct.ap_uint<8>"]* %0, i64 0, i64 %for.loop.idx1, i32 0, i32 0, i32 0
  %3 = load i8, i8* %src.addr.0.0.05, align 1
  store i8 %3, i8* %dst.addr.0.0.06, align 1
  %for.loop.idx.next = add nuw nsw i64 %for.loop.idx1, 1
  %exitcond = icmp ne i64 %for.loop.idx.next, 512
  br i1 %exitcond, label %for.loop, label %ret

ret:                                              ; preds = %for.loop, %entry
  ret void
}

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @"onebyonecpy_hls.p0a512struct.ap_uint<8>"([512 x i8]* noalias nocapture align 512 "unpacked"="0.0.0.0", [512 x %"struct.ap_uint<8>"]* noalias readonly "unpacked"="1") unnamed_addr #3 {
entry:
  %2 = icmp eq [512 x %"struct.ap_uint<8>"]* %1, null
  br i1 %2, label %ret, label %copy

copy:                                             ; preds = %entry
  br label %for.loop

for.loop:                                         ; preds = %for.loop, %copy
  %for.loop.idx1 = phi i64 [ 0, %copy ], [ %for.loop.idx.next, %for.loop ]
  %src.addr.0.0.05 = getelementptr [512 x %"struct.ap_uint<8>"], [512 x %"struct.ap_uint<8>"]* %1, i64 0, i64 %for.loop.idx1, i32 0, i32 0, i32 0
  %dst.addr.0.0.06 = getelementptr [512 x i8], [512 x i8]* %0, i64 0, i64 %for.loop.idx1
  %3 = load i8, i8* %src.addr.0.0.05, align 1
  store i8 %3, i8* %dst.addr.0.0.06, align 1
  %for.loop.idx.next = add nuw nsw i64 %for.loop.idx1, 1
  %exitcond = icmp ne i64 %for.loop.idx.next, 512
  br i1 %exitcond, label %for.loop, label %ret

ret:                                              ; preds = %for.loop, %entry
  ret void
}

declare void @apatb_lenet_w4a4_top_hw(i8*, i8*, i32*)

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @copy_back([512 x %"struct.ap_uint<8>"]* noalias "unpacked"="0", [512 x i8]* noalias nocapture readonly align 512 "unpacked"="1.0.0.0", [30735 x %"struct.ap_uint<8>"]* noalias "unpacked"="2", [30735 x i8]* noalias nocapture readonly "unpacked"="3.0.0.0", [10 x %"struct.ap_int<32>"]* noalias "unpacked"="4", [10 x i32]* noalias nocapture readonly align 512 "unpacked"="5.0.0.0") unnamed_addr #2 {
entry:
  call fastcc void @"onebyonecpy_hls.p0a10struct.ap_int<32>.65"([10 x %"struct.ap_int<32>"]* %4, [10 x i32]* align 512 %5)
  ret void
}

define void @lenet_w4a4_top_hw_stub_wrapper(i8*, i8*, i32*) #4 {
entry:
  %3 = alloca [512 x %"struct.ap_uint<8>"]
  %malloccall = tail call i8* @malloc(i64 30735)
  %4 = bitcast i8* %malloccall to [30735 x %"struct.ap_uint<8>"]*
  %5 = alloca [10 x %"struct.ap_int<32>"]
  %6 = bitcast i8* %0 to [512 x i8]*
  %7 = bitcast i8* %1 to [30735 x i8]*
  %8 = bitcast i32* %2 to [10 x i32]*
  call void @copy_out([512 x %"struct.ap_uint<8>"]* %3, [512 x i8]* %6, [30735 x %"struct.ap_uint<8>"]* %4, [30735 x i8]* %7, [10 x %"struct.ap_int<32>"]* %5, [10 x i32]* %8)
  %9 = bitcast [512 x %"struct.ap_uint<8>"]* %3 to %"struct.ap_uint<8>"*
  %10 = bitcast [30735 x %"struct.ap_uint<8>"]* %4 to %"struct.ap_uint<8>"*
  %11 = bitcast [10 x %"struct.ap_int<32>"]* %5 to %"struct.ap_int<32>"*
  call void @lenet_w4a4_top_hw_stub(%"struct.ap_uint<8>"* %9, %"struct.ap_uint<8>"* %10, %"struct.ap_int<32>"* %11)
  call void @copy_in([512 x %"struct.ap_uint<8>"]* %3, [512 x i8]* %6, [30735 x %"struct.ap_uint<8>"]* %4, [30735 x i8]* %7, [10 x %"struct.ap_int<32>"]* %5, [10 x i32]* %8)
  ret void
}

declare void @lenet_w4a4_top_hw_stub(%"struct.ap_uint<8>"*, %"struct.ap_uint<8>"*, %"struct.ap_int<32>"*)

attributes #0 = { noinline "fpga.wrapper.func"="wrapper" }
attributes #1 = { argmemonly noinline norecurse "fpga.wrapper.func"="copyin" }
attributes #2 = { argmemonly noinline norecurse "fpga.wrapper.func"="copyout" }
attributes #3 = { argmemonly noinline norecurse "fpga.wrapper.func"="onebyonecpy_hls" }
attributes #4 = { "fpga.wrapper.func"="stub" }

!llvm.dbg.cu = !{}
!llvm.ident = !{!0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0}
!llvm.module.flags = !{!1, !2, !3}
!blackbox_cfg = !{!4}

!0 = !{!"clang version 7.0.0 "}
!1 = !{i32 2, !"Dwarf Version", i32 4}
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 1, !"wchar_size", i32 4}
!4 = !{}
