from ultralytics import YOLO
import torch

if __name__ == "__main__":
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if torch.cuda.is_available():
        torch.cuda.set_device(0)
    print("training")
    model = YOLO("yolov8n.yaml")
    model.train(data='config.yaml', epochs=200, imgsz=1280, batch=8, device='cuda') 