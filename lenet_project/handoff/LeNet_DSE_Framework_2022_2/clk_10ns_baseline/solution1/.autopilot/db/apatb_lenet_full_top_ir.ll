; ModuleID = 'D:/lenet_project/handoff/LeNet_DSE_Framework_2022_2/LeNet_DSE_Framework_2022_2/clk_10ns_baseline/solution1/.autopilot/db/a.g.ld.5.gdce.bc'
source_filename = "llvm-link"
target datalayout = "e-m:e-i64:64-i128:128-i256:256-i512:512-i1024:1024-i2048:2048-i4096:4096-n8:16:32:64-S128-v16:16-v24:32-v32:32-v48:64-v96:128-v192:256-v256:256-v512:512-v1024:1024"
target triple = "fpga64-xilinx-none"

; Function Attrs: noinline
define void @apatb_lenet_full_top_ir(float* noalias nocapture nonnull readonly "fpga.decayed.dim.hint"="1024" %feature_in, float* noalias nocapture nonnull readonly "fpga.decayed.dim.hint"="61470" %weight, float* noalias nocapture nonnull readonly "fpga.decayed.dim.hint"="236" %bias, float* noalias nocapture nonnull "fpga.decayed.dim.hint"="10" %feature_out) local_unnamed_addr #0 {
entry:
  %malloccall = tail call i8* @malloc(i64 4096)
  %feature_in_copy = bitcast i8* %malloccall to [1024 x float]*
  %malloccall1 = tail call i8* @malloc(i64 245880)
  %weight_copy = bitcast i8* %malloccall1 to [61470 x float]*
  %bias_copy = alloca [236 x float], align 512
  %feature_out_copy = alloca [10 x float], align 512
  %0 = bitcast float* %feature_in to [1024 x float]*
  %1 = bitcast float* %weight to [61470 x float]*
  %2 = bitcast float* %bias to [236 x float]*
  %3 = bitcast float* %feature_out to [10 x float]*
  call fastcc void @copy_in([1024 x float]* nonnull %0, [1024 x float]* %feature_in_copy, [61470 x float]* nonnull %1, [61470 x float]* %weight_copy, [236 x float]* nonnull %2, [236 x float]* nonnull align 512 %bias_copy, [10 x float]* nonnull %3, [10 x float]* nonnull align 512 %feature_out_copy)
  %4 = getelementptr inbounds [1024 x float], [1024 x float]* %feature_in_copy, i32 0, i32 0
  %5 = getelementptr inbounds [61470 x float], [61470 x float]* %weight_copy, i32 0, i32 0
  %6 = getelementptr inbounds [236 x float], [236 x float]* %bias_copy, i32 0, i32 0
  %7 = getelementptr inbounds [10 x float], [10 x float]* %feature_out_copy, i32 0, i32 0
  call void @apatb_lenet_full_top_hw(float* %4, float* %5, float* %6, float* %7)
  call void @copy_back([1024 x float]* %0, [1024 x float]* %feature_in_copy, [61470 x float]* %1, [61470 x float]* %weight_copy, [236 x float]* %2, [236 x float]* %bias_copy, [10 x float]* %3, [10 x float]* %feature_out_copy)
  tail call void @free(i8* %malloccall)
  tail call void @free(i8* %malloccall1)
  ret void
}

declare noalias i8* @malloc(i64) local_unnamed_addr

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @copy_in([1024 x float]* noalias readonly, [1024 x float]* noalias, [61470 x float]* noalias readonly, [61470 x float]* noalias, [236 x float]* noalias readonly, [236 x float]* noalias align 512, [10 x float]* noalias readonly, [10 x float]* noalias align 512) unnamed_addr #1 {
entry:
  call fastcc void @onebyonecpy_hls.p0a1024f32([1024 x float]* %1, [1024 x float]* %0)
  call fastcc void @onebyonecpy_hls.p0a61470f32([61470 x float]* %3, [61470 x float]* %2)
  call fastcc void @onebyonecpy_hls.p0a236f32([236 x float]* align 512 %5, [236 x float]* %4)
  call fastcc void @onebyonecpy_hls.p0a10f32([10 x float]* align 512 %7, [10 x float]* %6)
  ret void
}

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @onebyonecpy_hls.p0a1024f32([1024 x float]* noalias, [1024 x float]* noalias readonly) unnamed_addr #2 {
entry:
  %2 = icmp eq [1024 x float]* %0, null
  %3 = icmp eq [1024 x float]* %1, null
  %4 = or i1 %2, %3
  br i1 %4, label %ret, label %copy

copy:                                             ; preds = %entry
  br label %for.loop

for.loop:                                         ; preds = %for.loop, %copy
  %for.loop.idx1 = phi i64 [ 0, %copy ], [ %for.loop.idx.next, %for.loop ]
  %dst.addr = getelementptr [1024 x float], [1024 x float]* %0, i64 0, i64 %for.loop.idx1
  %src.addr = getelementptr [1024 x float], [1024 x float]* %1, i64 0, i64 %for.loop.idx1
  %5 = load float, float* %src.addr, align 4
  store float %5, float* %dst.addr, align 4
  %for.loop.idx.next = add nuw nsw i64 %for.loop.idx1, 1
  %exitcond = icmp ne i64 %for.loop.idx.next, 1024
  br i1 %exitcond, label %for.loop, label %ret

ret:                                              ; preds = %for.loop, %entry
  ret void
}

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @onebyonecpy_hls.p0a61470f32([61470 x float]* noalias, [61470 x float]* noalias readonly) unnamed_addr #2 {
entry:
  %2 = icmp eq [61470 x float]* %0, null
  %3 = icmp eq [61470 x float]* %1, null
  %4 = or i1 %2, %3
  br i1 %4, label %ret, label %copy

copy:                                             ; preds = %entry
  br label %for.loop

for.loop:                                         ; preds = %for.loop, %copy
  %for.loop.idx1 = phi i64 [ 0, %copy ], [ %for.loop.idx.next, %for.loop ]
  %dst.addr = getelementptr [61470 x float], [61470 x float]* %0, i64 0, i64 %for.loop.idx1
  %src.addr = getelementptr [61470 x float], [61470 x float]* %1, i64 0, i64 %for.loop.idx1
  %5 = load float, float* %src.addr, align 4
  store float %5, float* %dst.addr, align 4
  %for.loop.idx.next = add nuw nsw i64 %for.loop.idx1, 1
  %exitcond = icmp ne i64 %for.loop.idx.next, 61470
  br i1 %exitcond, label %for.loop, label %ret

ret:                                              ; preds = %for.loop, %entry
  ret void
}

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @onebyonecpy_hls.p0a236f32([236 x float]* noalias align 512, [236 x float]* noalias readonly) unnamed_addr #2 {
entry:
  %2 = icmp eq [236 x float]* %0, null
  %3 = icmp eq [236 x float]* %1, null
  %4 = or i1 %2, %3
  br i1 %4, label %ret, label %copy

copy:                                             ; preds = %entry
  br label %for.loop

for.loop:                                         ; preds = %for.loop, %copy
  %for.loop.idx1 = phi i64 [ 0, %copy ], [ %for.loop.idx.next, %for.loop ]
  %dst.addr = getelementptr [236 x float], [236 x float]* %0, i64 0, i64 %for.loop.idx1
  %src.addr = getelementptr [236 x float], [236 x float]* %1, i64 0, i64 %for.loop.idx1
  %5 = load float, float* %src.addr, align 4
  store float %5, float* %dst.addr, align 4
  %for.loop.idx.next = add nuw nsw i64 %for.loop.idx1, 1
  %exitcond = icmp ne i64 %for.loop.idx.next, 236
  br i1 %exitcond, label %for.loop, label %ret

ret:                                              ; preds = %for.loop, %entry
  ret void
}

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @onebyonecpy_hls.p0a10f32([10 x float]* noalias align 512, [10 x float]* noalias readonly) unnamed_addr #2 {
entry:
  %2 = icmp eq [10 x float]* %0, null
  %3 = icmp eq [10 x float]* %1, null
  %4 = or i1 %2, %3
  br i1 %4, label %ret, label %copy

copy:                                             ; preds = %entry
  br label %for.loop

for.loop:                                         ; preds = %for.loop, %copy
  %for.loop.idx1 = phi i64 [ 0, %copy ], [ %for.loop.idx.next, %for.loop ]
  %dst.addr = getelementptr [10 x float], [10 x float]* %0, i64 0, i64 %for.loop.idx1
  %src.addr = getelementptr [10 x float], [10 x float]* %1, i64 0, i64 %for.loop.idx1
  %5 = load float, float* %src.addr, align 4
  store float %5, float* %dst.addr, align 4
  %for.loop.idx.next = add nuw nsw i64 %for.loop.idx1, 1
  %exitcond = icmp ne i64 %for.loop.idx.next, 10
  br i1 %exitcond, label %for.loop, label %ret

ret:                                              ; preds = %for.loop, %entry
  ret void
}

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @copy_out([1024 x float]* noalias, [1024 x float]* noalias readonly, [61470 x float]* noalias, [61470 x float]* noalias readonly, [236 x float]* noalias, [236 x float]* noalias readonly align 512, [10 x float]* noalias, [10 x float]* noalias readonly align 512) unnamed_addr #3 {
entry:
  call fastcc void @onebyonecpy_hls.p0a1024f32([1024 x float]* %0, [1024 x float]* %1)
  call fastcc void @onebyonecpy_hls.p0a61470f32([61470 x float]* %2, [61470 x float]* %3)
  call fastcc void @onebyonecpy_hls.p0a236f32([236 x float]* %4, [236 x float]* align 512 %5)
  call fastcc void @onebyonecpy_hls.p0a10f32([10 x float]* %6, [10 x float]* align 512 %7)
  ret void
}

declare void @free(i8*) local_unnamed_addr

declare void @apatb_lenet_full_top_hw(float*, float*, float*, float*)

; Function Attrs: argmemonly noinline norecurse
define internal fastcc void @copy_back([1024 x float]* noalias, [1024 x float]* noalias readonly, [61470 x float]* noalias, [61470 x float]* noalias readonly, [236 x float]* noalias, [236 x float]* noalias readonly align 512, [10 x float]* noalias, [10 x float]* noalias readonly align 512) unnamed_addr #3 {
entry:
  call fastcc void @onebyonecpy_hls.p0a10f32([10 x float]* %6, [10 x float]* align 512 %7)
  ret void
}

define void @lenet_full_top_hw_stub_wrapper(float*, float*, float*, float*) #4 {
entry:
  %4 = bitcast float* %0 to [1024 x float]*
  %5 = bitcast float* %1 to [61470 x float]*
  %6 = bitcast float* %2 to [236 x float]*
  %7 = bitcast float* %3 to [10 x float]*
  call void @copy_out([1024 x float]* null, [1024 x float]* %4, [61470 x float]* null, [61470 x float]* %5, [236 x float]* null, [236 x float]* %6, [10 x float]* null, [10 x float]* %7)
  %8 = bitcast [1024 x float]* %4 to float*
  %9 = bitcast [61470 x float]* %5 to float*
  %10 = bitcast [236 x float]* %6 to float*
  %11 = bitcast [10 x float]* %7 to float*
  call void @lenet_full_top_hw_stub(float* %8, float* %9, float* %10, float* %11)
  call void @copy_in([1024 x float]* null, [1024 x float]* %4, [61470 x float]* null, [61470 x float]* %5, [236 x float]* null, [236 x float]* %6, [10 x float]* null, [10 x float]* %7)
  ret void
}

declare void @lenet_full_top_hw_stub(float*, float*, float*, float*)

attributes #0 = { noinline "fpga.wrapper.func"="wrapper" }
attributes #1 = { argmemonly noinline norecurse "fpga.wrapper.func"="copyin" }
attributes #2 = { argmemonly noinline norecurse "fpga.wrapper.func"="onebyonecpy_hls" }
attributes #3 = { argmemonly noinline norecurse "fpga.wrapper.func"="copyout" }
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
