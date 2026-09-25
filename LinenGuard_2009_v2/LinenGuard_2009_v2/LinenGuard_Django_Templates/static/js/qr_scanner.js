// LINENGUARD - Browser QR Scanner & Audio Feedback Service

// Audio Synthesizer for instant scanning feedback without external audio files
const AudioFeedback = {
  ctx: null,
  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.ctx = new AudioContext();
      }
    }
  },
  playSuccess() {
    try {
      this.init();
      if (!this.ctx) return;
      if (this.ctx.state === 'suspended') this.ctx.resume();

      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(880, this.ctx.currentTime); // A5 note
      osc.frequency.exponentialRampToValueAtTime(1320, this.ctx.currentTime + 0.15); // E6 note

      gain.gain.setValueAtTime(0.3, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.25);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.25);
    } catch (e) {
      console.warn("Audio error:", e);
    }
  },
  playWarning() {
    try {
      this.init();
      if (!this.ctx) return;
      if (this.ctx.state === 'suspended') this.ctx.resume();

      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(220, this.ctx.currentTime);
      osc.frequency.setValueAtTime(180, this.ctx.currentTime + 0.15);

      gain.gain.setValueAtTime(0.35, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.35);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.35);
    } catch (e) {
      console.warn("Audio error:", e);
    }
  }
};

class LinenQRScanner {
  constructor(config) {
    this.sessionId = config.sessionId;
    this.csrfToken = config.csrfToken;
    this.scanApiUrl = config.scanApiUrl || '/api/collection/scan/';
    this.returnApiUrl = config.returnApiUrl || '/api/collection/return/';
    this.html5QrCode = null;
    this.isScanning = false;
    this.lastScannedCode = null;
    this.isProcessing = false;
  }

  initScanner() {
    if (!document.getElementById('reader')) return;

    this.html5QrCode = new Html5Qrcode("reader");

    Html5Qrcode.getCameras().then(cameras => {
      if (cameras && cameras.length) {
        const cameraId = cameras[cameras.length - 1].id; // Prefer back camera if mobile
        this.startCamera(cameraId);
      } else {
        this.showCameraNotice("No camera detected. Please use manual entry below.");
      }
    }).catch(err => {
      console.warn("Camera enumeration error:", err);
      this.showCameraNotice("Camera permission denied or camera unavailable. You can use manual QR ID entry.");
    });
  }

  startCamera(cameraId) {
    const config = {
      fps: 10,
      qrbox: { width: 250, height: 250 },
      aspectRatio: 1.0
    };

    this.html5QrCode.start(
      cameraId,
      config,
      (decodedText) => {
        this.onScanSuccess(decodedText);
      },
      (errorMessage) => {
        // Continuous parse errors are normal while seeking QR
      }
    ).then(() => {
      this.isScanning = true;
      const statusEl = document.getElementById('camera-status');
      if (statusEl) {
        statusEl.innerHTML = '<span class="badge bg-success"><i class="bi bi-camera-video me-1"></i>Camera Active</span>';
      }
    }).catch(err => {
      console.warn("Camera start error:", err);
      this.showCameraNotice("Could not access camera feed. Manual entry is ready below.");
    });
  }

  showCameraNotice(msg) {
    const el = document.getElementById('camera-status');
    if (el) {
      el.innerHTML = `<div class="alert alert-warning py-2 small mb-2"><i class="bi bi-exclamation-triangle me-1"></i>${msg}</div>`;
    }
  }

  onScanSuccess(decodedText) {
    if (this.isProcessing) return;
    const cleanCode = decodedText.trim();
    if (cleanCode === this.lastScannedCode && Date.now() - this.lastScanTime < 3000) {
      return; // Debounce rapid rescanning of identical code
    }

    this.lastScannedCode = cleanCode;
    this.lastScanTime = Date.now();
    this.processCode(cleanCode);
  }

  processCode(code) {
    if (!code) return;
    this.isProcessing = true;

    // Show loading state
    const resultBox = document.getElementById('scan-result-container');
    if (resultBox) {
      resultBox.innerHTML = `
        <div class="card border-primary p-3 text-center my-3">
          <div class="spinner-border text-primary mx-auto mb-2" role="status"></div>
          <div class="fw-semibold">Verifying Linen QR: <span class="font-monospace">${code}</span>...</div>
        </div>
      `;
    }

    fetch(this.scanApiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.csrfToken
      },
      body: JSON.stringify({
        session_id: this.sessionId,
        qr_code: code
      })
    })
    .then(res => res.json())
    .then(data => {
      this.renderScanResult(data);
      this.isProcessing = false;
    })
    .catch(err => {
      console.error("Scan API Error:", err);
      this.renderScanResult({
        valid: false,
        result: 'ERROR',
        message: 'Network error communicating with server. Please try again.'
      });
      this.isProcessing = false;
    });
  }

  renderScanResult(data) {
    const container = document.getElementById('scan-result-container');
    if (!container) return;

    if (data.valid && data.result === 'SUCCESS') {
      AudioFeedback.playSuccess();

      container.innerHTML = `
        <div class="card border-success shadow-sm my-3 animate__animated animate__fadeIn">
          <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
            <span class="fw-bold"><i class="bi bi-check-circle-fill me-1"></i> LINEN VERIFIED</span>
            <span class="badge bg-white text-success font-monospace">${data.linen_code}</span>
          </div>
          <div class="card-body">
            <div class="row g-2 mb-3">
              <div class="col-6">
                <div class="small text-muted">Linen Type</div>
                <div class="fw-bold fs-5 text-dark">${data.linen_type}</div>
              </div>
              <div class="col-6">
                <div class="small text-muted">Status</div>
                <div><span class="badge bg-primary">${data.status}</span></div>
              </div>
              <div class="col-4">
                <div class="small text-muted">Train</div>
                <div class="fw-semibold">${data.train}</div>
              </div>
              <div class="col-4">
                <div class="small text-muted">Coach</div>
                <div class="fw-semibold text-primary">${data.coach}</div>
              </div>
              <div class="col-4">
                <div class="small text-muted">Berth</div>
                <div class="fw-bold text-success fs-5">${data.berth}</div>
              </div>
            </div>
            
            <div class="d-grid gap-2">
              <button id="btn-mark-returned" class="btn btn-success btn-lg fw-bold shadow">
                <i class="bi bi-arrow-down-circle me-1"></i> MARK AS RETURNED
              </button>
            </div>
          </div>
        </div>
      `;

      // Attach return handler
      const btnReturn = document.getElementById('btn-mark-returned');
      if (btnReturn) {
        btnReturn.addEventListener('click', () => {
          this.executeMarkReturned(data.linen_code);
        });
      }

    } else {
      AudioFeedback.playWarning();

      let alertClass = 'alert-warning';
      let title = '⚠ VERIFICATION NOTICE';
      let icon = 'bi-exclamation-triangle-fill';

      if (data.result === 'WRONG_COACH') {
        title = '⚠ WRONG COACH DETECTED';
        alertClass = 'alert-warning';
      } else if (data.result === 'ALREADY_RETURNED') {
        title = '⚠ ALREADY RETURNED';
        alertClass = 'alert-info';
        icon = 'bi-info-circle-fill';
      } else if (data.result === 'UNKNOWN_QR') {
        title = '❌ UNKNOWN LINEN QR';
        alertClass = 'alert-danger';
        icon = 'bi-x-circle-fill';
      }

      container.innerHTML = `
        <div class="alert ${alertClass} shadow-sm my-3 animate__animated animate__shakeX">
          <div class="d-flex align-items-center mb-2">
            <i class="bi ${icon} fs-4 me-2"></i>
            <h5 class="alert-heading mb-0 fw-bold">${title}</h5>
          </div>
          <p class="mb-2">${data.message}</p>
          ${data.coach ? `<div class="small fw-semibold">Assigned Location: Train ${data.train || ''} / Coach ${data.coach} / Berth ${data.berth || ''}</div>` : ''}
          <hr class="my-2">
          <div class="d-flex justify-content-between align-items-center">
            <span class="small text-muted">Attempt recorded in audit log.</span>
            <button class="btn btn-sm btn-outline-secondary" onclick="document.getElementById('manual-qr-input').focus();">Try Another QR</button>
          </div>
        </div>
      `;
    }
  }

  executeMarkReturned(linenCode) {
    const btn = document.getElementById('btn-mark-returned');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Recording Return...';
    }

    fetch(this.returnApiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.csrfToken
      },
      body: JSON.stringify({
        session_id: this.sessionId,
        linen_code: linenCode
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        AudioFeedback.playSuccess();
        const container = document.getElementById('scan-result-container');
        if (container) {
          container.innerHTML = `
            <div class="card border-success bg-light shadow my-3 text-center p-4">
              <div class="display-6 text-success mb-2"><i class="bi bi-check2-circle"></i></div>
              <h4 class="fw-bold text-success">✓ LINEN COLLECTED</h4>
              <div class="fs-4 font-monospace fw-bold text-dark my-1">${data.linen_code}</div>
              <div class="text-muted mb-2">${data.linen_type} • Collected at ${data.timestamp}</div>
              <div class="alert alert-success py-2 d-inline-block mx-auto mb-3">
                Scanned: <strong>${data.scanned_quantity}</strong> / ${data.expected_quantity}
                (Remaining: <strong>${data.remaining_quantity}</strong>)
              </div>
              <div>
                <button class="btn btn-primary px-4" onclick="document.getElementById('manual-qr-input').value=''; document.getElementById('manual-qr-input').focus();">
                  <i class="bi bi-qr-code-scan me-1"></i> SCAN NEXT LINEN
                </button>
              </div>
            </div>
          `;
        }

        // Dynamically update counter widgets on the page if present
        const scannedEl = document.getElementById('stat-scanned-qty');
        const remainingEl = document.getElementById('stat-remaining-qty');
        if (scannedEl) scannedEl.innerText = data.scanned_quantity;
        if (remainingEl) remainingEl.innerText = data.remaining_quantity;

      } else {
        alert(data.message || "Failed to mark returned.");
      }
    })
    .catch(err => {
      console.error("Return error:", err);
      alert("Error recording return. Please check server.");
    });
  }
}
