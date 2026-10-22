export interface StabilizerConfig {
  windowSize?: number; // Número de frames no buffer deslizante (padrão: 8)
  thresholdRatio?: number; // Percentual mínimo de persistência (padrão: 0.75 = 75%)
}

export class TemporalStabilizer {
  private windowSize: number;
  private thresholdRatio: number;
  private buffer: (string | null)[];

  constructor(config: StabilizerConfig = {}) {
    this.windowSize = config.windowSize ?? 8;
    this.thresholdRatio = config.thresholdRatio ?? 0.75;
    this.buffer = [];
  }

  /**
   * Adiciona a predição do frame atual à fila deslizante
   */
  public push(className: string | null): void {
    this.buffer.push(className);
    if (this.buffer.length > this.windowSize) {
      this.buffer.shift();
    }
  }

  /**
   * Retorna a classe estável dominante ou null se houver oscilação
   */
  public getStableClass(): {
    className: string;
    confidenceRatio: number;
  } | null {
    if (this.buffer.length < this.windowSize) {
      return null;
    }

    const counts = new Map<string, number>();
    for (const item of this.buffer) {
      if (item) {
        counts.set(item, (counts.get(item) ?? 0) + 1);
      }
    }

    let dominantClass: string | null = null;
    let maxCount = 0;

    for (const [cls, count] of counts.entries()) {
      if (count > maxCount) {
        maxCount = count;
        dominantClass = cls;
      }
    }

    if (dominantClass) {
      const ratio = maxCount / this.windowSize;
      if (ratio >= this.thresholdRatio) {
        return { className: dominantClass, confidenceRatio: ratio };
      }
    }

    return null;
  }

  /**
   * Retorna o progresso atual de estabilização (0% a 100%) da classe mais frequente
   */
  public getStabilizationProgress(): {
    className: string | null;
    progress: number;
  } {
    if (this.buffer.length === 0) return { className: null, progress: 0 };

    const counts = new Map<string, number>();
    for (const item of this.buffer) {
      if (item) {
        counts.set(item, (counts.get(item) ?? 0) + 1);
      }
    }

    let dominantClass: string | null = null;
    let maxCount = 0;

    for (const [cls, count] of counts.entries()) {
      if (count > maxCount) {
        maxCount = count;
        dominantClass = cls;
      }
    }

    const progress = dominantClass
      ? Math.min(100, Math.round((maxCount / this.windowSize) * 100))
      : 0;
    return { className: dominantClass, progress };
  }

  public reset(): void {
    this.buffer = [];
  }
}
