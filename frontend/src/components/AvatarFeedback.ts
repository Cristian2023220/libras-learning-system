export type AvatarState = "idle" | "stabilizing" | "success";

export class AvatarFeedback {
  private container: HTMLElement;
  private state: AvatarState = "idle";

  constructor(targetElement: HTMLElement) {
    this.container = targetElement;
    this.render();
  }

  public setState(state: AvatarState, gestureName = "") {
    if (this.state === state && state !== "success") return;
    this.state = state;
    this.render(gestureName);
  }

  private render(gestureName = "") {
    let glowColor = "#3b82f6"; // Azul neutro
    let badgeText = "Posicione sua mão";
    let badgeBg = "#1e293b";
    let armRotationLeft = "rotate(0deg)";
    let armRotationRight = "rotate(0deg)";
    let faceExpression = `
      <circle cx="90" cy="85" r="5" fill="#0f172a" />
      <circle cx="110" cy="85" r="5" fill="#0f172a" />
      <path d="M 92 100 Q 100 108 108 100" stroke="#0f172a" stroke-width="3" fill="none" stroke-linecap="round"/>
    `;

    if (this.state === "stabilizing") {
      glowColor = "#f59e0b"; // Amarelo de foco
      badgeText = `Mantendo sinal: ${gestureName}...`;
      badgeBg = "#78350f";
    } else if (this.state === "success") {
      glowColor = "#10b981"; // Verde sucesso
      badgeText = `Sinal Correto: ${gestureName.toUpperCase()}!`;
      badgeBg = "#064e3b";
      armRotationLeft = "rotate(-35deg)";
      armRotationRight = "rotate(35deg)";
      faceExpression = `
        <path d="M 85 85 Q 90 78 95 85" stroke="#0f172a" stroke-width="3" fill="none" stroke-linecap="round"/>
        <path d="M 105 85 Q 110 78 115 85" stroke="#0f172a" stroke-width="3" fill="none" stroke-linecap="round"/>
        <path d="M 88 98 Q 100 115 112 98 Z" fill="#0f172a"/>
      `;
    }

    this.container.innerHTML = `
      <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; height: 100%; transition: all 0.3s ease;">
        <div style="
          width: 200px;
          height: 200px;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(30,41,59,0.8) 0%, rgba(15,23,42,1) 100%);
          border: 3px solid ${glowColor};
          box-shadow: 0 0 25px ${glowColor}55;
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
          overflow: hidden;
          transition: border-color 0.3s, box-shadow 0.3s;
        ">
          <!-- SVG Mascote Robô / Humanoide -->
          <svg viewBox="0 0 200 200" width="180" height="180" style="overflow: visible;">
            <!-- Tronco -->
            <rect x="75" y="115" width="50" height="55" rx="15" fill="#e2e8f0" stroke="#94a3b8" stroke-width="3"/>
            <!-- Cabeça -->
            <circle cx="100" cy="90" r="32" fill="#f8fafc" stroke="#94a3b8" stroke-width="3"/>
            <!-- Expressão Facial -->
            ${faceExpression}
            <!-- Braço Esquerdo -->
            <g style="transform-origin: 75px 125px; transform: ${armRotationLeft}; transition: transform 0.25s ease;">
              <rect x="50" y="120" width="22" height="12" rx="6" fill="#cbd5e1" stroke="#94a3b8" stroke-width="2"/>
              <circle cx="45" cy="126" r="10" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
            </g>
            <!-- Braço Direito -->
            <g style="transform-origin: 125px 125px; transform: ${armRotationRight}; transition: transform 0.25s ease;">
              <rect x="128" y="120" width="22" height="12" rx="6" fill="#cbd5e1" stroke="#94a3b8" stroke-width="2"/>
              <circle cx="155" cy="126" r="10" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
            </g>
          </svg>
        </div>

        <div style="
          margin-top: 15px;
          padding: 6px 16px;
          border-radius: 20px;
          background-color: ${badgeBg};
          color: #f8fafc;
          font-weight: 600;
          font-size: 13px;
          letter-spacing: 0.5px;
          border: 1px solid ${glowColor}66;
          transition: all 0.3s;
        ">
          ${badgeText}
        </div>
      </div>
    `;
  }
}
