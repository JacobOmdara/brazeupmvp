import torch
import torch.nn as nn


class ConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(ConvBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.relu(self.bn2(self.conv2(x)))
        return x


class EncoderBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(EncoderBlock, self).__init__()
        self.conv_block = ConvBlock(in_channels, out_channels)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

    def forward(self, x):
        skip = self.conv_block(x)
        x = self.pool(skip)
        return x, skip


class DecoderBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(DecoderBlock, self).__init__()
        self.upconv = nn.ConvTranspose2d(
            in_channels, out_channels, kernel_size=2, stride=2
        )
        self.conv_block = ConvBlock(in_channels, out_channels)

    def forward(self, x, skip):
        x = self.upconv(x)

        if x.shape != skip.shape:
            diff_h = skip.shape[2] - x.shape[2]
            diff_w = skip.shape[3] - x.shape[3]
            x = nn.functional.pad(
                x,
                [diff_w // 2, diff_w - diff_w // 2, diff_h // 2, diff_h - diff_h // 2],
            )

        x = torch.cat([skip, x], dim=1)
        x = self.conv_block(x)
        return x


class UNet(nn.Module):
    def __init__(self, in_channels=3, out_channels=7, base_filters=64, depth=4):
        super(UNet, self).__init__()

        self.encoders = nn.ModuleList()
        channels = in_channels
        for i in range(depth):
            self.encoders.append(EncoderBlock(channels, base_filters * (2**i)))
            channels = base_filters * (2**i)

        self.bottleneck = ConvBlock(channels, base_filters * (2**depth))

        self.decoders = nn.ModuleList()
        for i in range(depth - 1, -1, -1):
            self.decoders.append(
                DecoderBlock(base_filters * (2 ** (i + 1)), base_filters * (2**i))
            )

        self.output = nn.Conv2d(base_filters, out_channels, kernel_size=1)

    def forward(self, x):
        skip_connections = []
        for encoder in self.encoders:
            x, skip = encoder(x)
            skip_connections.append(skip)

        x = self.bottleneck(x)

        skip_connections = skip_connections[::-1]
        for decoder, skip in zip(self.decoders, skip_connections):
            x = decoder(x, skip)

        x = self.output(x)
        return x
