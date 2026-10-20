export interface Detection {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  score: number;
  classId: number;
  className: string;
}

export class Postprocessor {
  private confThreshold: number;
  private iouThreshold: number;
  private classes: string[];

  constructor(classes: string[], confThreshold = 0.5, iouThreshold = 0.45) {
    this.classes = classes;
    this.confThreshold = confThreshold;
    this.iouThreshold = iouThreshold;
  }

  /**
   * Decodifica a matriz bruta [1, 84, 8400] e devolve as caixas finais
   */
  public process(
    outputData: Float32Array,
    videoWidth: number,
    videoHeight: number,
  ): Detection[] {
    const numAnchors = 8400;
    const numClasses = this.classes.length;
    const detections: Detection[] = [];

    // Fator de escala para mapear de 640x640 de volta para o tamanho real da tela
    const scaleX = videoWidth / 640;
    const scaleY = videoHeight / 640;

    for (let i = 0; i < numAnchors; i++) {
      // Procura a classe com maior probabilidade para esta caixa
      let maxScore = -Infinity;
      let bestClass = -1;

      for (let c = 0; c < numClasses; c++) {
        const score = outputData[(4 + c) * numAnchors + i];
        if (score > maxScore) {
          maxScore = score;
          bestClass = c;
        }
      }

      if (maxScore >= this.confThreshold) {
        // Coordenadas centrais e dimensões da caixa
        const cx = outputData[0 * numAnchors + i];
        const cy = outputData[1 * numAnchors + i];
        const w = outputData[2 * numAnchors + i];
        const h = outputData[3 * numAnchors + i];

        // Converte de (center_x, center_y, w, h) para coordenadas dos cantos (x1, y1, x2, y2)
        const x1 = Math.max(0, (cx - w / 2) * scaleX);
        const y1 = Math.max(0, (cy - h / 2) * scaleY);
        const x2 = Math.min(videoWidth, (cx + w / 2) * scaleX);
        const y2 = Math.min(videoHeight, (cy + h / 2) * scaleY);

        detections.push({
          x1,
          y1,
          x2,
          y2,
          score: maxScore,
          classId: bestClass,
          className: this.classes[bestClass] ?? `Classe ${bestClass}`,
        });
      }
    }

    // Aplica Supressão Não-Máxima para descartar sobreposições
    return this.applyNMS(detections);
  }

  private applyNMS(boxes: Detection[]): Detection[] {
    boxes.sort((a, b) => b.score - a.score);
    const selected: Detection[] = [];

    for (const box of boxes) {
      let keep = true;
      for (const sel of selected) {
        if (this.calculateIoU(box, sel) > this.iouThreshold) {
          keep = false;
          break;
        }
      }
      if (keep) {
        selected.push(box);
      }
    }

    return selected;
  }

  private calculateIoU(a: Detection, b: Detection): number {
    const interX1 = Math.max(a.x1, b.x1);
    const interY1 = Math.max(a.y1, b.y1);
    const interX2 = Math.min(a.x2, b.x2);
    const interY2 = Math.min(a.y2, b.y2);

    const interArea =
      Math.max(0, interX2 - interX1) * Math.max(0, interY2 - interY1);
    const areaA = (a.x2 - a.x1) * (a.y2 - a.y1);
    const areaB = (b.x2 - b.x1) * (b.y2 - b.y1);

    const unionArea = areaA + areaB - interArea;
    return unionArea > 0 ? interArea / unionArea : 0;
  }
}
