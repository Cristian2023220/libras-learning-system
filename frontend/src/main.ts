import * as ort from "onnxruntime-web";
import { COCO_CLASSES } from "./core/labels";
import { FramePreprocessor } from "./core/preprocessor";
import { Postprocessor, type Detection } from "./core/postprocessor";

ort.env.wasm.wasmPaths = "https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/";

// Elementos da Interface
const container = document.createElement("div");
container.style.position = "relative";
container.style.display = "inline-block";
container.style.fontFamily = "sans-serif";

const video = document.createElement("video");
video.autoplay = true;
video.playsInline = true;
video.width = 640;
video.height = 480;

const overlay = document.createElement("canvas");
overlay.width = 640;
overlay.height = 480;
overlay.style.position = "absolute";
overlay.style.left = "0";
overlay.style.top = "0";
overlay.style.pointerEvents = "none";

const overlayCtx = overlay.getContext("2d")!;

const statusText = document.createElement("div");
statusText.style.fontFamily = "monospace";
statusText.style.fontSize = "14px";
statusText.style.margin = "10px 0";
statusText.innerText = "Iniciando câmera e carregando modelo...";

container.appendChild(video);
container.appendChild(overlay);
document.body.appendChild(statusText);
document.body.appendChild(container);

// Instâncias do Pipeline
const preprocessor = new FramePreprocessor(640);
const postprocessor = new Postprocessor(COCO_CLASSES, 0.5, 0.45);
let session: ort.InferenceSession | null = null;
let isInferring = false;

async function init() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480 },
      audio: false,
    });
    video.srcObject = stream;

    statusText.innerText = "Carregando grafo ONNX no navegador...";
    session = await ort.InferenceSession.create("/models/yolov8n.onnx", {
      executionProviders: ["webgl", "wasm"],
    });

    statusText.innerText = "YOLO ativo em tempo real.";
    requestAnimationFrame(inferenceLoop);
  } catch (err) {
    statusText.innerText = `Erro de inicialização: ${err}`;
  }
}

async function inferenceLoop() {
  if (!session || video.readyState !== 4) {
    requestAnimationFrame(inferenceLoop);
    return;
  }

  if (!isInferring) {
    isInferring = true;
    const start = performance.now();

    // 1. Pré-processamento
    const inputTensor = preprocessor.process(video);

    // 2. Inferência no navegador
    const results = await session.run({ images: inputTensor });
    const outputTensor = results[session.outputNames[0]];

    // 3. Pós-processamento e NMS
    const detections = postprocessor.process(
      outputTensor.data as Float32Array,
      video.width,
      video.height,
    );

    const latency = performance.now() - start;
    const fps = (1000 / latency).toFixed(1);
    statusText.innerText = `Inferência Local | Latência: ${latency.toFixed(1)} ms | FPS: ~${fps} | Objetos: ${detections.length}`;

    // 4. Renderização visual
    renderDetections(detections);
    isInferring = false;
  }

  requestAnimationFrame(inferenceLoop);
}

function renderDetections(detections: Detection[]) {
  overlayCtx.clearRect(0, 0, overlay.width, overlay.height);

  for (const det of detections) {
    const width = det.x2 - det.x1;
    const height = det.y2 - det.y1;

    // Caixa Delimitadora
    overlayCtx.strokeStyle = "#00FF66";
    overlayCtx.lineWidth = 3;
    overlayCtx.strokeRect(det.x1, det.y1, width, height);

    // Rótulo de identificação
    const label = `${det.className} (${(det.score * 100).toFixed(0)}%)`;
    overlayCtx.font = "bold 14px sans-serif";
    const textWidth = overlayCtx.measureText(label).width;

    overlayCtx.fillStyle = "#00FF66";
    overlayCtx.fillRect(det.x1, Math.max(0, det.y1 - 22), textWidth + 10, 22);

    overlayCtx.fillStyle = "#000000";
    overlayCtx.fillText(label, det.x1 + 5, Math.max(16, det.y1 - 6));
  }
}

init();
