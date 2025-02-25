import torch.nn as nn
import torch.optim as optim

def calculate_output_length(input_seq, kernel_size, stride=1, padding=0, dilation=1):
    return (input_seq + 2 * padding - dilation * (kernel_size - 1) - 1) // stride + 1

class CNN1D(nn.Module):
    def __init__(self, input_channels, output_channels, kernel_size, stride, padding, drop_out, input_seq, num_classes, **extra_model_param):
        """

        Args:
            input_channels (int): input_channels
        """
        super(CNN1D, self).__init__()
        # 첫 번째 1-dimensional convolution layer 구축
        self.layer1 = nn.Sequential(
            nn.Conv1d(input_channels, 32, kernel_size = kernel_size, stride = stride, padding = padding),
            nn.ReLU(),
            nn.AvgPool1d(2)
        )
        
        next_seq = calculate_output_length(input_seq, kernel_size, stride, padding, dilation=1)
        next_seq = next_seq // 2
        
        # 두 번째 1-dimensional convolution layer 구축
        self.layer2 = nn.Sequential(
            nn.Conv1d(32, output_channels, kernel_size = kernel_size, stride = stride, padding = padding),
            nn.ReLU(),
            nn.AvgPool1d(2)
        )
        
        next_seq = calculate_output_length(next_seq, kernel_size, stride, padding, dilation=1)
        next_seq = next_seq // 2
        
        # fully-connected layer 구축
        self.dropout = nn.Dropout(drop_out)
        self.fc = nn.Linear(output_channels * next_seq, num_classes) # 이부분은 hyperparameter에 따라 계산을 해줘야 함


    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        x = self.fc(x)
        return x
