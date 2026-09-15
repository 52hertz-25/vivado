# Historical Pad preprocessing evidence

The files in this directory are the original software evidence generated with
`Pad(2)`: W4A4 accuracy 97.46% and FP32 accuracy 98.82%. They are retained for
provenance and are now treated as a preprocessing ablation.

The canonical Resize evaluation, all 10,000 per-sample predictions and the HLS
Q40 comparison are in
`../../results/w4a4_preprocessing_ablation/resize/`. The executable evaluator is
`../../evaluate_w4a4_int32.py`.
