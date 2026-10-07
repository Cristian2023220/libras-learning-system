from ultralytics import YOLO

def treinar():
    model = YOLO("yolov8n.pt")

    model.train(
        data="../dataset/data.yaml",
        epochs=40,
        imgsz=640,
        batch=16,
        project="../runs",
        name="libras_pilot",
        device="cpu"  # Se tiver GPU NVIDIA com CUDA configurado, troque para 0
    )

if __name__ == "__main__":
    treinar()