from pathlib import Path

import torch

from model import LeNet5


base_dir = Path(__file__).resolve().parent
weight_path = base_dir / "lenet5_fp32_from_hls.pth"

# 优先使用苹果MPS，没有则使用CPU
if torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")

print("运行设备：", device)

# 创建模型并加载刚生成的FP32权重
model = LeNet5()
state_dict = torch.load(weight_path, map_location="cpu")
model.load_state_dict(state_dict)

model = model.to(device)
model.eval()

# 生成一张形状为1×32×32的模拟灰度图片
test_input = torch.randn(1, 1, 32, 32, device=device)

with torch.no_grad():
    output = model(test_input)

print("输入形状：", tuple(test_input.shape))
print("输出形状：", tuple(output.shape))
print("输出是否全部为有效数值：", torch.isfinite(output).all().item())
print("模拟预测类别：", output.argmax(dim=1).item())

if tuple(output.shape) == (1, 10) and torch.isfinite(output).all():
    print("FP32模型完整推理测试通过。[PASS]")
else:
    print("FP32模型推理测试失败。[FAIL]")