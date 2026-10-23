from ultralytics import YOLO
import os

def exportar_libras():
    # Caminho exato gerado pelo train.py
    pesos_treinados = os.path.abspath("../../runs/runs/libras_pilot/weights/best.pt")
    
    if not os.path.exists(pesos_treinados):
        raise FileNotFoundError(f"Pesos não encontrados em: {pesos_treinados}")

    print(f"Carregando pesos treinados de: {pesos_treinados}...")
    model = YOLO(pesos_treinados)

    print("Iniciando exportação otimizada para ONNX (Web friendly)...")
    caminho_onnx = model.export(
        format="onnx",
        imgsz=640,
        opset=12,
        simplify=True,
        dynamic=False
    )
    
    print(f"\n[OK] Modelo exportado com sucesso: {caminho_onnx}")

if __name__ == "__main__":
    exportar_libras()