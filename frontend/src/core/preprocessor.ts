import * as ort from "onnxruntime-web";

export class FramePreprocessor {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private targetSize: number;

  constructor(targetSize = 640) {
    this.targetSize = targetSize;
    this.canvas = document.createElement("canvas");
    this.canvas.width = targetSize;
    this.canvas.height = targetSize;
    const context = this.canvas.getContext("2d", { willReadFrequently: true });
    if (!context)
      throw new Error("Não foi possível obter o contexto 2D do Canvas.");
    this.ctx = context;
  }

  /**
   * Converte o frame atual do elemento <video> no tensor [1, 3, 640, 640]
   */
  public process(video: HTMLVideoElement): ort.Tensor {
    // 1. Redimensiona o quadro do vídeo para 640x640
    this.ctx.drawImage(video, 0, 0, this.targetSize, this.targetSize);

    // 2. Extrai os pixels brutos (formato RGBA entrelaçado: [R, G, B, A, R, G, B, A, ...])
    const imgData = this.ctx.getImageData(
      0,
      0,
      this.targetSize,
      this.targetSize,
    );
    const { data } = imgData;

    const numPixels = this.targetSize * this.targetSize;
    // Buffer planar NCHW: 3 canais de tamanho 640*640
    const float32Data = new Float32Array(3 * numPixels);

    const rOffset = 0;
    const gOffset = numPixels;
    const bOffset = 2 * numPixels;

    // 3. Normalização [0, 255] -> [0.0, 1.0] e separação planar
    for (let i = 0; i < numPixels; i++) {
      const srcIdx = i * 4;
      float32Data[rOffset + i] = data[srcIdx] / 255.0; // Red
      float32Data[gOffset + i] = data[srcIdx + 1] / 255.0; // Green
      float32Data[bOffset + i] = data[srcIdx + 2] / 255.0; // Blue
    }

    return new ort.Tensor("float32", float32Data, [
      1,
      3,
      this.targetSize,
      this.targetSize,
    ]);
  }
}
