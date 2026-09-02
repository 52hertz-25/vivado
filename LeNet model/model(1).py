import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import os

#模型定义

class LeNet5(nn.Module):
    def __init__(self):
        super(LeNet5, self).__init__()
        # 输入: 1 x 32 x 32
        self.conv1 = nn.Conv2d(1, 6, kernel_size=5, stride=1, padding=0, bias=False)   # 输出: 6 x 28 x 28
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)                            # 输出: 6 x 14 x 14
        
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5, stride=1, padding=0, bias=False) # 输出: 16 x 10 x 10
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)                            # 输出: 16 x 5 x 5
        
        #1 x 1卷积
        self.conv3 = nn.Conv2d(16, 120, kernel_size=5, stride=1, padding=0, bias=False) # 输出: 120 x 1 x 1
        
        self.fc1 = nn.Linear(120, 84, bias=False)                                     # 输出: 84
        self.fc2 = nn.Linear(84, 10, bias=False)                                      # 输出: 10 (logits)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = self.pool1(x)
        x = torch.relu(self.conv2(x))
        x = self.pool2(x)
        x = torch.relu(self.conv3(x))
        
        # 展平
        x = x.view(x.size(0), -1) 
        
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)  # 不接 Softmax
        return x


#数据预处理

def get_dataloaders(batch_size=64):
    # MNIST 官方均值和标准差
    mean = (0.1307,)
    std = (0.3081,)
    
    transform = transforms.Compose([
        transforms.Resize((32, 32)),    # 将 28x28 放大到 32x32
        transforms.ToTensor(),
        transforms.Normalize(mean, std)
    ])

    # 下载训练集和测试集
    train_dataset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    test_dataset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
    
    return train_loader, test_loader


#训练与测试循环

def train_one_epoch(model, device, train_loader, optimizer, criterion, epoch):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = output.max(1)
        total += target.size(0)
        correct += predicted.eq(target).sum().item()
        
        if batch_idx % 100 == 0:
            print(f'Train Epoch: {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)} '
                  f'({100. * batch_idx / len(train_loader):.0f}%)]\tLoss: {loss.item():.6f}')
    
    avg_loss = running_loss / len(train_loader)
    accuracy = 100. * correct / total
    print(f'====> Epoch {epoch} Average Loss: {avg_loss:.4f}, Training Accuracy: {accuracy:.2f}%')
    return avg_loss, accuracy

def test(model, device, test_loader, criterion):
    model.eval()
    test_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += criterion(output, target).item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()
    
    test_loss /= len(test_loader)
    accuracy = 100. * correct / total
    print(f'====> Test set loss: {test_loss:.4f}, Accuracy: {accuracy:.2f}%')
    return test_loss, accuracy


#主程序入口
def main():
    # 设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # 超参数配置
    BATCH_SIZE = 64
    EPOCHS = 15
    LEARNING_RATE = 0.001
    
    # 加载数据
    train_loader, test_loader = get_dataloaders(BATCH_SIZE)
    
    # 初始化模型并打印参数总量
    model = LeNet5().to(device)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total number of parameters (without bias): {total_params}") # 应为 61,470
    
    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    # 记录最佳测试准确率
    best_acc = 0.0
    
    # 开始训练
    for epoch in range(1, EPOCHS + 1):
        train_loss, train_acc = train_one_epoch(model, device, train_loader, optimizer, criterion, epoch)
        test_loss, test_acc = test(model, device, test_loader, criterion)
        
        # 保存最佳模型
        if test_acc > best_acc:
            best_acc = test_acc
            # 保存 state_dict（只包含权重，不包含优化器状态，方便 HLS 同学加载）
            torch.save(model.state_dict(), 'lenet5_mnist_best.pth')
            print(f"====> Best model saved with accuracy: {best_acc:.2f}%")
    
    print(f"Training finished. Best test accuracy: {best_acc:.2f}%")

if __name__ == "__main__":
    # 先不训练，只测试加载
    train_loader, test_loader = get_dataloaders()
    images, labels = next(iter(train_loader))
    main()
