import onnxruntime as ort
import numpy as np

def validar_grafo(caminho_onnx="yolov8n.onnx"):
    print(f"Abrindo sessão ONNX para: {caminho_onnx}...")
    session = ort.InferenceSession(caminho_onnx, providers=['CPUExecutionProvider'])

    print("\n--- Tensores de Entrada ---")
    for inp in session.get_inputs():
        print(f"Nome: {inp.name} | Formato: {inp.shape} | Tipo: {inp.type}")

    print("\n--- Tensores de Saída ---")
    for out in session.get_outputs():
        print(f"Nome: {out.name} | Formato: {out.shape} | Tipo: {out.type}")

    # Simulação de um quadro RGB 640x640 sintético
    dummy_input = np.random.randn(1, 3, 640, 640).astype(np.float32)
    pred = session.run([session.get_outputs()[0].name], {session.get_inputs()[0].name: dummy_input})
    
    print("\n[OK] Validação concluída com sucesso!")
    print(f"Saída gerada pelo modelo (Shape): {pred[0].shape}")

if __name__ == "__main__":
    validar_grafo()