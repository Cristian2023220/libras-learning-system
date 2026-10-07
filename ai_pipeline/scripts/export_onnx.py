from ultralytics import YOLO
import os

def exportar_modelo(caminho_pesos="yolov8n.pt", destino_saida="../weights/yolov8n.onnx"):
    print(f"Carregando pesos de: {caminho_pesos}...")
    model = YOLO(caminho_pesos)

    print("Iniciando exportação otimizada para ONNX (Web friendly)...")
    caminho_gerado = model.export(
        format="onnx",
        imgsz=640,
        opset=12,         # Compatibilidade total com ONNX Runtime Web
        simplify=True,    # Remove nós redundantes do grafo
        dynamic=False     # Buffer fixo [1, 3, 640, 640] para alta performance no cliente
    )
    
    print(f"\n[OK] Modelo exportado com sucesso: {caminho_gerado}")

if __name__ == "__main__":
    exportar_modelo()