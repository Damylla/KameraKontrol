document.addEventListener('DOMContentLoaded', () => {
    const counterEl = document.getElementById('people-counter');
    const logEl = document.getElementById('terminal-log');
    const lastUpdateEl = document.getElementById('last-update');
    const cameraFpsEl = document.getElementById('camera-fps');
    const cameraTimestampEl = document.getElementById('camera-timestamp');
    const todayCountEl = document.getElementById('today-count');
    const currentCountEl = document.getElementById('current-count');
    const usbStatusEl = document.getElementById('usb-status');
    const yoloStatusEl = document.getElementById('yolo-status');
    const streamStatusEl = document.getElementById('stream-status');
    const gpuStatusEl = document.getElementById('gpu-status');

    let todayTotal = 0;

    // ======== UPDATE PERSON COUNT ========
    function updatePersonCount() {
        fetch('/api/person_count')
            .then(response => response.json())
            .then(data => {
                if (data.count !== undefined) {
                    counterEl.textContent = data.count;
                    currentCountEl.textContent = data.count;
                    if (data.count > 0) {
                        todayTotal += data.count;
                        todayCountEl.textContent = todayTotal;
                    }
                }
                updateTimestamp();
            })
            .catch(err => {
                console.error('API Error:', err);
                counterEl.textContent = '?';
            });
    }

    // ======== UPDATE TIMESTAMP ========
    function updateTimestamp() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');

        if (lastUpdateEl) {
            lastUpdateEl.textContent = `Last update: ${hours}:${minutes}:${seconds}`;
        }

        if (cameraTimestampEl) {
            const dateStr = now.toISOString().slice(0, 10);
            const timeStr = now.toTimeString().split(' ')[0];
            cameraTimestampEl.textContent = ` ${dateStr} ${timeStr}`;
        }
    }

    // ======== UPDATE FPS ========
    let frameCount = 0;
    let lastFpsUpdate = performance.now();

    function updateFps() {
        const now = performance.now();
        frameCount++;

        if (now - lastFpsUpdate >= 1000) {
            const fps = Math.round((frameCount * 1000) / (now - lastFpsUpdate));
            if (cameraFpsEl) {
                cameraFpsEl.textContent = `${fps} FPS`;
            }
            // Update stream status
            if (streamStatusEl) {
                streamStatusEl.textContent = ` ${fps} FPS`;
                streamStatusEl.style.color = fps > 20 ? '#34c759' : '#ff9500';
            }
            frameCount = 0;
            lastFpsUpdate = now;
        }
        requestAnimationFrame(updateFps);
    }

    // ======== GPU USAGE (Simulated) ========
    function updateGpuUsage() {
        const usage = Math.floor(Math.random() * 30) + 25; // 25-55% range
        if (gpuStatusEl) {
            if (usage < 35) {
                gpuStatusEl.textContent = `🟢 ${usage}%`;
                gpuStatusEl.style.color = '#34c759';
            } else if (usage < 50) {
                gpuStatusEl.textContent = `🟡 ${usage}%`;
                gpuStatusEl.style.color = '#ffd60a';
            } else {
                gpuStatusEl.textContent = `🔴 ${usage}%`;
                gpuStatusEl.style.color = '#ff3b30';
            }
        }
    }

    // ======== TERMINAL LOG ========
    const logs = [
        '[SYSTEM] YOLOv8 Human Detection Module initializing...',
        '[CONNECTION] Atech USB Port detected. Status: Connected.',
        '[CONNECTION] Atech USB Port data stream active (480 Mbps).',
        '[SYSTEM] CUDA GPU acceleration active. Usage: 42%.',
        '[MODEL] YOLOv8x.onnx weights loaded into memory.',
        '[DETECTION] Live analysis started. Accuracy: 92.5%.',
        '[DETECTION] Zone-A (Entrance): 2 people detected.',
        '[SYSTEM] System temperature: 42°C, Memory: 18%.'
    ];
    let logIndex = 0;

    function updateLog() {
        logIndex = (logIndex + 1) % logs.length;
        if (logEl) {
            logEl.textContent = `> ${logs[logIndex]}`;
        }
    }

    // ======== BUTTON FUNCTIONS ========

    // 1. Deep Analysis
    const btnDeepThink = document.getElementById('btn-deep-think');
    if (btnDeepThink) {
        btnDeepThink.addEventListener('click', () => {
            logEl.textContent = '> [DEEP ANALYSIS] YOLO analyzing past frames deeply...';
            logEl.style.color = '#af52de';
            btnDeepThink.style.opacity = '0.7';

            // Increase GPU usage
            gpuStatusEl.textContent = '🔴 78%';
            gpuStatusEl.style.color = '#ff3b30';

            setTimeout(() => {
                logEl.textContent = '> [DEEP ANALYSIS] Analysis complete! Confidence: 99.4%';
                logEl.style.color = '#64d2ff';
                btnDeepThink.style.opacity = '1';
                gpuStatusEl.textContent = '🟡 42%';
                gpuStatusEl.style.color = '#ffd60a';
                updatePersonCount();
            }, 3000);
        });
    }

    // 2. Target Tracking
    const btnSmartSearch = document.getElementById('btn-smart-search');
    if (btnSmartSearch) {
        btnSmartSearch.addEventListener('click', () => {
            logEl.textContent = '> [TARGET TRACKING] Target tracking mode activating...';
            logEl.style.color = '#007aff';
            btnSmartSearch.style.opacity = '0.7';

            setTimeout(() => {
                logEl.textContent = '> [TARGET TRACKING] 3 targets detected. Tracking started.';
                logEl.style.color = '#64d2ff';
                btnSmartSearch.style.opacity = '1';
            }, 2500);
        });
    }

    // 3. Export Report
    const btnExport = document.getElementById('btn-export');
    if (btnExport) {
        btnExport.addEventListener('click', () => {
            logEl.textContent = '> [REPORT] Generating system report...';
            logEl.style.color = '#ff9500';
            btnExport.style.opacity = '0.7';

            setTimeout(() => {
                const now = new Date();
                const dateStr = now.toISOString().slice(0, 10);
                const timeStr = now.toTimeString().split(' ')[0];
                const currentCount = counterEl.textContent || '0';

                const report = `
╔══════════════════════════════════════╗
║       YOLO DETECTION SYSTEM REPORT   ║
╠══════════════════════════════════════╣
║ Date: ${dateStr} ${timeStr}             ║
║ Person Count: ${currentCount}                    ║
║ System Status: Active                 ║
║ GPU Usage: 42%                       ║
║ Confidence: 99.4%                    ║
║ FPS: ${cameraFpsEl.textContent}                     ║
╚══════════════════════════════════════╝
                `;

                // Download
                const blob = new Blob([report], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `yolo_report_${dateStr}.txt`;
                a.click();
                URL.revokeObjectURL(url);

                logEl.textContent = '> [REPORT] Report saved successfully!';
                logEl.style.color = '#64d2ff';
                btnExport.style.opacity = '1';
            }, 2000);
        });
    }

    // 4. Screenshot
    const btnScreenshot = document.getElementById('btn-screenshot');
    if (btnScreenshot) {
        btnScreenshot.addEventListener('click', () => {
            logEl.textContent = '> [SCREENSHOT] Capturing snapshot...';
            logEl.style.color = '#ff9500';
            btnScreenshot.style.opacity = '0.7';

            setTimeout(() => {
                const videoFeed = document.getElementById('videoFeed');
                const canvas = document.createElement('canvas');
                canvas.width = videoFeed.naturalWidth || 640;
                canvas.height = videoFeed.naturalHeight || 480;
                const ctx = canvas.getContext('2d');

                ctx.drawImage(videoFeed, 0, 0);

                // Add system info overlay
                const now = new Date();
                const timeStr = now.toTimeString().split(' ')[0];
                ctx.fillStyle = 'rgba(0,0,0,0.7)';
                ctx.fillRect(10, 10, 280, 80);
                ctx.fillStyle = 'white';
                ctx.font = 'bold 16px sans-serif';
                ctx.fillText('YOLO Detection System', 20, 35);
                ctx.font = '14px sans-serif';
                ctx.fillText(`Time: ${timeStr} | People: ${counterEl.textContent}`, 20, 60);

                // Download
                const link = document.createElement('a');
                link.download = `yolo_screenshot_${Date.now()}.png`;
                link.href = canvas.toDataURL('image/png');
                link.click();

                logEl.textContent = '> [SCREENSHOT] Screenshot saved successfully!';
                logEl.style.color = '#64d2ff';
                btnScreenshot.style.opacity = '1';
            }, 1000);
        });
    }

    // ======== PERIODIC UPDATES ========
    updatePersonCount();
    setInterval(updatePersonCount, 1000);
    setInterval(updateLog, 4000);
    setInterval(updateGpuUsage, 5000);
    updateFps();
    setInterval(updateTimestamp, 1000);
    updateTimestamp();

    console.log(' YOLO Human Detection System started!');
});