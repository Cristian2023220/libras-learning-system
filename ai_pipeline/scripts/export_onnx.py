from ultralytics import YOLO
import os

def exportar_libras():
    pesos_treinados = "../runs/libras_pilot/weights/best.pt"
    
    if not os.path.exists(pesos_treinados):
        raise FileNotFoundError(f"Pesos não encontrados em {pesos_treinados}. Execute o train.py primeiro.")

    print(f"Carregando pesos treinados de: {pesos_treinados}...")
    model = YOLO(pesos_treinados)

    print("Exportando para ONNX com otimização Web...")
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