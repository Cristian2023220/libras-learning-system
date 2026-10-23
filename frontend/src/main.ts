import * as ort from "onnxruntime-web";
import { LIBRAS_CLASSES } from "./core/labels";
import { FramePreprocessor } from "./core/preprocessor";
import { Postprocessor, type Detection } from "./core/postprocessor";
import { TemporalStabilizer } from "./core/stabilizer";
import { AvatarFeedback } from "./components/AvatarFeedback";

ort.env.wasm.wasmPaths = "https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/";

// Configuração do Exercício / Lição (Usando classes do modelo base atual para teste)
const TARGET_GESTURE = "A";

// Estrutura Principal da Página (Dark Theme)
document.body.style.margin = "0";
document.body.style.backgroundColor = "#0b0f19";
document.body.style.color = "#f8fafc";
document.body.style.fontFamily =
  'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

const mainLayout = document.createElement("div");
mainLayout.style.display = "grid";
mainLayout.style.gridTemplateColumns = "660px 340px";
mainLayout.style.gap = "20px";
mainLayout.style.padding = "25px";
mainLayout.style.maxWidth = "1050px";
mainLayout.style.margin = "0 auto";

// --- Painel Esquerdo: Câmera & Detecção ---
const leftPanel = document.createElement("div");
leftPanel.style.display = "flex";
leftPanel.style.flexDirection = "column";
leftPanel.style.gap = "10px";

const title = document.createElement("h2");
title.innerText = "LIBRAS Learning System";
title.style.margin = "0 0 5px 0";
title.style.color = "#38bdf8";

const statusText = document.createElement("div");
statusText.style.fontFamily = "monospace";
statusText.style.fontSize = "13px";
statusText.style.color = "#94a3b8";
statusText.innerText = "Iniciando sistema...";

const videoWrapper = document.createElement("div");
videoWrapper.style.position = "relative";
videoWrapper.style.width = "640px";
videoWrapper.style.height = "480px";
videoWrapper.style.borderRadius = "12px";
videoWrapper.style.overflow = "hidden";
videoWrapper.style.border = "2px solid #1e293b";

const video = document.createElement("video");
video.autoplay = true;
video.playsInline = true;
video.width = 640;
video.height = 480;
video.style.transform = "scaleX(-1)"; // Efeito espelho para uso natural do aluno

const overlay = document.createElement("canvas");
overlay.width = 640;
overlay.height = 480;
overlay.style.position = "absolute";
overlay.style.left = "0";
overlay.style.top = "0";
// overlay.style.transform = "scaleX(-1)"; // Acompanha o efeito espelho da câmera
const overlayCtx = overlay.getContext("2d")!;

videoWrapper.appendChild(video);
videoWrapper.appendChild(overlay);
leftPanel.appendChild(title);
leftPanel.appendChild(statusText);
leftPanel.appendChild(videoWrapper);

// --- Painel Direito: Gamificação & Avatar ---
const rightPanel = document.createElement("div");
rightPanel.style.backgroundColor = "#111827";
rightPanel.style.borderRadius = "12px";
rightPanel.style.border = "2px solid #1e293b";
rightPanel.style.padding = "20px";
rightPanel.style.display = "flex";
rightPanel.style.flexDirection = "column";
rightPanel.style.justifyContent = "space-between";

const targetBox = document.createElement("div");
targetBox.style.backgroundColor = "#1f2937";
targetBox.style.padding = "12px 16px";
targetBox.style.borderRadius = "8px";
targetBox.style.borderLeft = "4px solid #38bdf8";
targetBox.innerHTML = `
  <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8;">Desafio Atual</div>
  <div style="font-size: 18px; font-weight: bold; color: #f8fafc; margin-top: 4px;">Reproduza: <span style="color: #38bdf8;">${TARGET_GESTURE.toUpperCase()}</span></div>
`;

// Barra de Estabilização
const progressSection = document.createElement("div");
progressSection.style.margin = "15px 0";
progressSection.innerHTML = `
  <div style="display: flex; justify-content: space-between; font-size: 12px; color: #94a3b8; margin-bottom: 5px;">
    <span>Estabilidade do Gesto</span>
    <span id="stabilizer-val">0%</span>
  </div>
  <div style="width: 100%; height: 8px; background-color: #1f2937; border-radius: 4px; overflow: hidden;">
    <div id="stabilizer-bar" style="width: 0%; height: 100%; background-color: #3b82f6; transition: width 0.15s ease, background-color 0.3s ease;"></div>
  </div>
`;

const avatarContainer = document.createElement("div");
avatarContainer.style.height = "270px";

rightPanel.appendChild(targetBox);
rightPanel.appendChild(progressSection);
rightPanel.appendChild(avatarContainer);

mainLayout.appendChild(leftPanel);
mainLayout.appendChild(rightPanel);
document.body.appendChild(mainLayout);

// Inicialização dos Motores
const preprocessor = new FramePreprocessor(640);
const postprocessor = new Postprocessor(LIBRAS_CLASSES, 0.45, 0.45);
const stabilizer = new TemporalStabilizer({
  windowSize: 8,
  thresholdRatio: 0.75,
});
const avatar = new AvatarFeedback(avatarContainer);

let session: ort.InferenceSession | null = null;
let isInferring = false;
let successCooldown = false;

async function init() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480 },
      audio: false,
    });
    video.srcObject = stream;

    statusText.innerText = "Carregando grafo ONNX no navegador...";
    session = await ort.InferenceSession.create("/models/libras_pilot.onnx", {
      executionProviders: ["webgpu", "webgl", "wasm"],
    });

    statusText.innerText =
      "Sistema pronto. Aponte a câmera e pratique o sinal.";
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

    // 2. Inferência ONNX Local
    const results = await session.run({ images: inputTensor });
    const outputTensor = results[session.outputNames[0]];

    // 3. Pós-processamento NMS
    const detections = postprocessor.process(
      outputTensor.data as Float32Array,
      video.width,
      video.height,
    );

    const latency = performance.now() - start;
    const fps = (1000 / latency).toFixed(1);
    statusText.innerText = `Latência: ${latency.toFixed(1)} ms | Taxa: ~${fps} FPS | Detecções: ${detections.length}`;

    // 4. Alimentação do Estabilizador Temporal
    const topDetection = detections.length > 0 ? detections[0] : null;
    const detectedClassName = topDetection ? topDetection.className : null;

    if (!successCooldown) {
      stabilizer.push(detectedClassName);
      const stableResult = stabilizer.getStableClass();
      const progressInfo = stabilizer.getStabilizationProgress();

      // Atualiza a barra de estabilização
      const progressBar = document.getElementById(
        "stabilizer-bar",
      ) as HTMLElement;
      const progressLabel = document.getElementById(
        "stabilizer-val",
      ) as HTMLElement;
      if (progressBar && progressLabel) {
        progressBar.style.width = `${progressInfo.progress}%`;
        progressLabel.innerText = `${progressInfo.progress}%`;
        progressBar.style.backgroundColor =
          progressInfo.progress >= 75 ? "#10b981" : "#3b82f6";
      }

      // Avaliação da Lição
      if (stableResult && stableResult.className === TARGET_GESTURE) {
        // Gesto validado com sucesso!
        avatar.setState("success", stableResult.className);
        successCooldown = true;

        setTimeout(() => {
          stabilizer.reset();
          successCooldown = false;
          avatar.setState("idle");
        }, 2500); // 2.5 segundos de comemoração antes do próximo sinal
      } else if (progressInfo.progress > 40 && progressInfo.className) {
        avatar.setState("stabilizing", progressInfo.className);
      } else {
        avatar.setState("idle");
      }
    }

    // 5. Desenhar caixas no Canvas Overlay
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
    const isTarget = det.className === TARGET_GESTURE;

    // Inverte a coordenada X para alinhar com o vídeo espelhado:
    const mirroredX = overlay.width - det.x2;

    overlayCtx.strokeStyle = isTarget ? "#10b981" : "#38bdf8";
    overlayCtx.lineWidth = 3;
    overlayCtx.strokeRect(mirroredX, det.y1, width, height);

    const label = `${det.className} (${(det.score * 100).toFixed(0)}%)`;
    overlayCtx.font = "bold 13px sans-serif";
    const textWidth = overlayCtx.measureText(label).width;

    overlayCtx.fillStyle = isTarget ? "#10b981" : "#38bdf8";
    overlayCtx.fillRect(
      mirroredX,
      Math.max(0, det.y1 - 22),
      textWidth + 10,
      22,
    );

    overlayCtx.fillStyle = "#0f172a";
    overlayCtx.fillText(label, mirroredX + 5, Math.max(16, det.y1 - 6));
  }
}

init();
