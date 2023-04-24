import ray
import ray.train as train
from ray.train.torch import TorchTrainer
from ray.air.config import ScalingConfig
from ray.air import session

import numpy as np
import matplotlib.pyplot as plt

import torch
from torch import nn
from torch.utils.data import DataLoader
import torchvision
import torchvision.transforms as transforms


transform = transforms.Compose([transforms.ToTensor()])

train_set = torchvision.datasets.FashionMNIST(
    root="./data", train=True, download=True, transform=transform
)

test_set = torchvision.datasets.FashionMNIST(
    root="./data", train=False, download=True, transform=transform
)


classes = (
    "top",
    "Trouser",
    "Pullover",
    "Dress",
    "Coat",
    "Sandal",
    "Shirt",
    "Sneaker",
    "Bag",
    "Ankle boot"
)


class LeNet(nn.Module):
    def __init__(self, input_size: int, num_of_classes: int):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=6, kernel_size=5, padding=0),
            nn.AvgPool2d(kernel_size=2, stride=2),
            nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5, padding=0),
            nn.AvgPool2d(kernel_size=2, stride=2)
        )

        self.head = nn.Sequential(
            nn.Linear(in_features=input_size, out_features=120),
            nn.ReLU(),
            nn.Linear(in_features=120, out_features=84),
            nn.ReLU(),
            nn.Linear(in_features=84, out_features=num_of_classes)
        )

    def forward(self, x):
        return self.head(torch.flatten(self.backbone(x), 1))


def show_image(img):
    img = img / 2 + 0.5
    np_img = img.numpy()
    plt.imshow(np.transpose(np_img, (1, 2, 0)))
    plt.axis("off")
    plt.show()


def train_epoch(train_loader, net, criterion, optimizer, epoch):
    net.train()
    running_loss = 0.0
    for i, data in enumerate(train_loader):
        inputs, labels = data

        optimizer.zero_grad()

        # Compute prediction error
        outputs = net(inputs)
        loss = criterion(outputs, labels)

        running_loss += loss.item()

        # Backpropagation
        loss.backward()
        optimizer.step()
        if i % 200 == 199:
            print(f"[{epoch + 1}, {i + 1:5d}] loss: {running_loss / 200:.3f}")
            running_loss = 0.0


def validate_epoch(test_loader, net, criterion):
    size = len(test_loader.dataset) // session.get_world_size()
    num_batches = len(test_loader)
    net.eval()
    test_loss, correct = 0, 0

    correct_pred = {classname: 0 for classname in classes}
    total_pred = {classname: 0 for classname in classes}
    with torch.no_grad():
        for data in test_loader:
            images, labels = data
            outputs = net(images)

            _, predictions = torch.max(outputs, 1)
            for i, classname in enumerate(classes):
                class_pred = labels[labels == i] == predictions[labels == i]
                correct_pred[classname] += class_pred.sum()
                total_pred[classname] += class_pred.size(0)

            test_loss += criterion(outputs, labels).item()
            correct += (outputs.argmax(1) == labels).type(torch.float).sum().item()

    test_loss /= num_batches
    correct /= size
    print(
        f"Test Error: \n "
        f"Accuracy: {(100 * correct):>0.1f}%, "
        f"Avg loss: {test_loss:>8f} \n"
    )

    for classname, correct_count in correct_pred.items():
        accuracy = 100 * float(correct_count) / total_pred[classname]
        print(f"Accuracy for class {classname:5s} is {accuracy:.1f}%")

    return test_loss


def train_func(config):
    batch_size = config["batch_size"]
    lr = config["lr"]
    momentum = config["momentum"]
    epochs = config["epochs"]

    worker_batch_size = batch_size // session.get_world_size()
    print(worker_batch_size, batch_size, session.get_world_size())

    train_loader = torch.utils.data.DataLoader(train_set, batch_size=worker_batch_size, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_set, batch_size=worker_batch_size, shuffle=True)

    train_loader = train.torch.prepare_data_loader(train_loader)
    test_loader = train.torch.prepare_data_loader(test_loader)

    # Create model.
    net = LeNet(256, len(classes))
    net = train.torch.prepare_model(net)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(net.parameters(), lr=lr, momentum=momentum)

    for epoch in range(epochs):
        train_epoch(train_loader, net, criterion, optimizer, epoch)
        loss = validate_epoch(test_loader, net, criterion)
        session.report(dict(loss=loss))


def train_fashion_mnist(num_workers=2, use_gpu=False):
    trainer = TorchTrainer(
        train_loop_per_worker=train_func,
        train_loop_config={
            "lr": 0.001,
            "momentum": 0.9,
            "batch_size": 32,
            "epochs": 1
        },
        scaling_config=ScalingConfig(num_workers=num_workers, use_gpu=use_gpu),
    )
    result = trainer.fit()
    print(f"Last result: {result.metrics}")


if __name__ == "__main__":
    ray.init()
    train_fashion_mnist()
    ray.shutdown()
