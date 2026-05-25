/**
 * DERMAVISION_CORE v5.0 - ADVANCED NEURAL INTERFACE
 * Logic: Multi-layer Forensic HUD, Async Diagnostic Pipeline, & UI State Synchronization
 */

class DermaScanner {
    constructor() {
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('overlay');
        this.ctx = this.canvas.getContext('2d');
        
        this.isScanning = false;
        this.stream = null;
        this.scanLineY = 0;
        this.scanDirection = 1;

        // Neural Mesh State for "luxurious" look
        this.points = [];
        this.themeColor = "#00f2ff";
        this.accentColor = "#E25822";
        this.glowColor = "rgba(0, 242, 255, 0.5)";
    }

    async boot() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: "user", width: 1280, height: 720 },
                audio: false
            });
            this.video.srcObject = this.stream;
            
            this.video.onloadedmetadata = () => {
                this.canvas.width = this.video.videoWidth;
                this.canvas.height = this.video.videoHeight;
                this._initNeuralPoints(); // Generate background mesh points
                this.renderHUD();
            };
        } catch (err) {
            this.handleError("LINK_FAILURE", err);
        }
    }

    /**
     * INTERNAL: Initializes floating points for a "neural network" visual effect
     */
    _initNeuralPoints() {
        for (let i = 0; i < 20; i++) {
            this.points.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 2,
                vy: (Math.random() - 0.5) * 2
            });
        }
    }

    renderHUD() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // 1. Draw Forensic Brackets & Digital Frame
        this.drawBrackets();
        
        // 2. Draw Neural Background Mesh (Luxurious Floating Points)
        this.drawNeuralMesh();

        // 3. Draw Scan Effects
        if (this.isScanning) {
            this.drawScanLine();
            this.drawActiveDiagnosticOverlay();
        }

        // 4. Telemetry Stream
        this.drawMetadata();

        requestAnimationFrame(() => this.renderHUD());
    }

    drawBrackets() {
        const { width: w, height: h } = this.canvas;
        const s = 60, p = 100;
        
        this.ctx.save();
        this.ctx.strokeStyle = this.isScanning ? this.accentColor : this.themeColor;
        this.ctx.lineWidth = 2;
        this.ctx.shadowBlur = 12;
        this.ctx.shadowColor = this.ctx.strokeStyle;

        // Dynamic Brackets
        const corners = [
            [p, p, s, s], [w-p, p, -s, s], 
            [p, h-p, s, -s], [w-p, h-p, -s, -s]
        ];

        corners.forEach(([x, y, dx, dy]) => {
            this.ctx.beginPath();
            this.ctx.moveTo(x, y + dy);
            this.ctx.lineTo(x, y);
            this.ctx.lineTo(x + dx, y);
            this.ctx.stroke();
        });
        this.ctx.restore();
    }

    drawNeuralMesh() {
        this.ctx.strokeStyle = "rgba(0, 242, 255, 0.1)";
        this.ctx.lineWidth = 1;
        
        this.points.forEach(p => {
            p.x += p.vx; p.y += p.vy;
            if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;
            
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }

    drawScanLine() {
        const gradient = this.ctx.createLinearGradient(0, this.scanLineY - 50, 0, this.scanLineY);
        gradient.addColorStop(0, "transparent");
        gradient.addColorStop(1, this.accentColor);

        this.ctx.fillStyle = gradient;
        this.ctx.globalAlpha = 0.3;
        this.ctx.fillRect(100, this.scanLineY - 40, this.canvas.width - 200, 40);
        this.ctx.globalAlpha = 1.0;
        
        this.ctx.strokeStyle = this.accentColor;
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.moveTo(100, this.scanLineY);
        this.ctx.lineTo(this.canvas.width - 100, this.scanLineY);
        this.ctx.stroke();

        this.scanLineY += 5 * this.scanDirection;
        if (this.scanLineY > this.canvas.height - 100 || this.scanLineY < 100) this.scanDirection *= -1;
    }

    drawActiveDiagnosticOverlay() {
        this.ctx.fillStyle = "rgba(226, 88, 34, 0.05)";
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = this.accentColor;
        this.ctx.font = "bold 14px 'JetBrains Mono'";
        this.ctx.fillText(">> ANALYZING_DERMAL_LAYERS...", 120, this.canvas.height - 120);
    }

    drawMetadata() {
        this.ctx.fillStyle = "rgba(0, 242, 255, 0.7)";
        this.ctx.font = "10px 'JetBrains Mono'";
        const timestamp = new Date().toISOString().split('T')[1];
        this.ctx.fillText(`UTC_REF: ${timestamp}`, 120, 130);
        this.ctx.fillText(`SENSOR_ISO: 400`, 120, 145);
        this.ctx.fillText(`NEURAL_ENGINE: V5.0_STABLE`, 120, 160);
    }

    async runDiagnostic() {
        if (this.isScanning) return;
        this.isScanning = true;
        
        const statusEl = document.getElementById('ai-status');
        statusEl.innerText = "● SYSTEM_ANALYZING";
        statusEl.classList.add('pulse-text'); // Add a CSS pulse class

        const captureCanvas = document.createElement('canvas');
        captureCanvas.width = this.video.videoWidth;
        captureCanvas.height = this.video.videoHeight;
        captureCanvas.getContext('2d').drawImage(this.video, 0, 0);

        const imageBlob = await new Promise(res => captureCanvas.toBlob(res, 'image/jpeg', 0.95));
        const formData = new FormData();
        formData.append('image', imageBlob);

        try {
            const response = await fetch('/api/analyze', { method: 'POST', body: formData });
            const result = await response.json();
            
            if (result.status === "SUCCESS") {
                this.updateUI(result.telemetry);
                this._playCompletionAnim();
            }
        } catch (error) {
            this.handleError("CORE_TIMEOUT", error);
        } finally {
            this.isScanning = false;
            statusEl.innerText = "● CORE_READY";
            statusEl.classList.remove('pulse-text');
        }
    }

    _playCompletionAnim() {
        // High-end shutter flash effect
        const flash = document.createElement('div');
        flash.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:white;z-index:9999;opacity:0.3;pointer-events:none;";
        document.body.appendChild(flash);
        setTimeout(() => flash.remove(), 100);
    }

    updateUI(data) {
        Object.entries(data).forEach(([key, value]) => {
            const bar = document.getElementById(`${key}-bar`);
            const label = document.getElementById(`${key}-val`);
            
            if (bar) {
                // Use CSS transitions for smoothness
                bar.style.transition = "width 1.5s cubic-bezier(0.1, 1, 0.1, 1)";
                bar.style.width = `${value}%`;
            }
            if (label) {
                this._animateValue(label, 0, value, 1500);
            }
        });

        const healthCircle = document.getElementById('health-index');
        if (healthCircle) this._animateValue(healthCircle, 0, data.health_index, 2000);
    }

    _animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerText = Math.floor(progress * (end - start) + start) + (obj.id.includes('val') ? "%" : "");
            if (progress < 1) window.requestAnimationFrame(step);
        };
        window.requestAnimationFrame(step);
    }

    handleError(code, err) {
        console.error(`[${code}]:`, err);
        const statusEl = document.getElementById('ai-status');
        statusEl.innerText = `● ERROR: ${code}`;
        statusEl.style.color = "#ff3b3b";
    }
}

const Scanner = new DermaScanner();
window.addEventListener('load', () => Scanner.boot());

function startScan() {
    Scanner.runDiagnostic();
}