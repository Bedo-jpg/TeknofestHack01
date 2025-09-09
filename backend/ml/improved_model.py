# backend/ml/improved_model.py
import torch
import torch.nn as nn
import torchvision.models as models

class ImprovedSegModel(nn.Module):
    """Gerçek UNet modeli - 6 channel input için"""
    def __init__(self):
        super().__init__()
        
        # Encoder (ResNet backbone) - İlk layer'ı 6 channel için değiştir
        self.encoder = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        
        # İlk convolutional layer'ı 6 channel için değiştir
        original_first_conv = self.encoder.conv1
        self.encoder.conv1 = nn.Conv2d(
            in_channels=6,  # ← 3 yerine 6 channel
            out_channels=original_first_conv.out_channels,
            kernel_size=original_first_conv.kernel_size,
            stride=original_first_conv.stride,
            padding=original_first_conv.padding,
            bias=original_first_conv.bias
        )
        
        # Weight'ları initialize et (isteğe bağlı)
        nn.init.kaiming_normal_(self.encoder.conv1.weight, mode='fan_out', nonlinearity='relu')
        
        # Encoder layers
        self.encoder_layers = list(self.encoder.children())[:-2]
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(512, 256, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 1, kernel_size=1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        # Input: [batch, 6, H, W] (before + after concatenated)
        features = self.encoder_layers[0](x)  # Initial conv (artık 6 channel)
        for layer in self.encoder_layers[1:]:
            features = layer(features)
        
        return self.decoder(features)

# Test için
if __name__ == "__main__":
    model = ImprovedSegModel()
    dummy_input = torch.randn(2, 6, 256, 256)  # ← 6 channel input
    output = model(dummy_input)
    print(f"Input: {dummy_input.shape}, Output: {output.shape}")