from ultralytics import YOLO
import os

def treinar():
    caminho_yaml = os.path.abspath("../dataset/data.yaml")

    print("Carregando pesos pré-treinados yolov8n.pt...")
    model = YOLO("yolov8n.pt")

    print("Iniciando treinamento otimizado para CPU Ryzen...")
    model.train(
        data=caminho_yaml,
        epochs=25,             # 25 épocas atingem ótima convergência com transfer learning
        imgsz=640,
        batch=16,              # Lote equilibrado para a CPU
        workers=4,             # Utiliza os núcleos do Ryzen 7 sem sobrecarregar o Windows
        cache=True,            # Mantém as imagens em RAM após o 1º ciclo, acelerando o treino
        project="../runs",
        name="libras_pilot",
        exist_ok=True,
        device="cpu"
    )

    print("\n[OK] Treinamento concluído com sucesso!")
    print("Pesos gerados em: ai_pipeline/runs/libras_pilot/weights/best.pt")

if __name__ == "__main__":
    treinar()