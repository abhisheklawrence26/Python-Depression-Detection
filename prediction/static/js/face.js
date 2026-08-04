const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const time = document.getElementById("time");
const status = document.getElementById("status");
const nextBtn = document.getElementById("nextBtn");
const overlay = document.getElementById("overlay");
const overlayCtx = overlay.getContext("2d");

let stream;
let timer;
let analysisInterval;
let seconds = 30;
let isAnalyzing = false;
let accumulatedEmotions = {
    happy: 0,
    sad: 0,
    neutral: 0,
    count: 0
};

// Open camera
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
    .then(function(s) {
        stream = s;
        video.srcObject = s;
        video.onloadedmetadata = function () {
            overlay.width = video.videoWidth || 640;
            overlay.height = video.videoHeight || 480;
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;
        };
    })
    .catch(function(error) {
        console.error("Camera access error:", error);
        status.innerHTML = "Camera access denied or unavailable";
    });
}

function drawOverlay(x, y, w, h, emotionText) {
    overlayCtx.clearRect(0, 0, overlay.width, overlay.height);
    if (w > 0 && h > 0) {
        const scaleX = overlay.width / (video.videoWidth || overlay.width);
        const scaleY = overlay.height / (video.videoHeight || overlay.height);

        const rectX = x * scaleX;
        const rectY = y * scaleY;
        const rectW = w * scaleX;
        const rectH = h * scaleY;

        overlayCtx.strokeStyle = "#00FF00";
        overlayCtx.lineWidth = 3;
        overlayCtx.strokeRect(rectX, rectY, rectW, rectH);

        overlayCtx.fillStyle = "#00FF00";
        overlayCtx.font = "bold 20px Arial";
        overlayCtx.fillText(emotionText, rectX, Math.max(rectY - 10, 25));
    }
}

function processSingleFrame() {
    if (!isAnalyzing || !video.videoWidth) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL("image/jpeg", 0.8);

    fetch("/analyze-face/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            image: imageData
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!isAnalyzing) return;
        if (data.error) {
            console.warn("Analysis frame note:", data.error);
            return;
        }

        accumulatedEmotions.happy += data.happy || 0;
        accumulatedEmotions.sad += data.sad || 0;
        accumulatedEmotions.neutral += data.neutral || 0;
        accumulatedEmotions.count += 1;

        const label = `${data.emotion} (${data.confidence || 0}%)`;
        drawOverlay(data.x, data.y, data.w, data.h, label);
        status.innerHTML = `Analyzing... Detected: ${data.emotion}`;
    })
    .catch(error => {
        console.error("Frame analysis error:", error);
    });
}

startBtn.onclick = function() {
    if (isAnalyzing) return;

    seconds = 30;
    time.innerHTML = seconds;
    status.innerHTML = "Analysis Started...";
    isAnalyzing = true;
    accumulatedEmotions = { happy: 0, sad: 0, neutral: 0, count: 0 };
    overlayCtx.clearRect(0, 0, overlay.width, overlay.height);

    processSingleFrame();
    analysisInterval = setInterval(processSingleFrame, 2000);

    timer = setInterval(function() {
        seconds--;
        time.innerHTML = seconds;

        if (seconds <= 0) {
            finishAnalysis();
        }
    }, 1000);
};

function finishAnalysis() {
    isAnalyzing = false;
    clearInterval(timer);
    clearInterval(analysisInterval);
    overlayCtx.clearRect(0, 0, overlay.width, overlay.height);
    status.innerHTML = "Finalizing Results...";

    let finalHappy = 0;
    let finalSad = 0;
    let finalNeutral = 0;

    if (accumulatedEmotions.count > 0) {
        finalHappy = (accumulatedEmotions.happy / accumulatedEmotions.count);
        finalSad = (accumulatedEmotions.sad / accumulatedEmotions.count);
        finalNeutral = (accumulatedEmotions.neutral / accumulatedEmotions.count);
    } else {
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        ctx.drawImage(video, 0, 0);
        const imageData = canvas.toDataURL("image/jpeg", 0.8);

        fetch("/analyze-face/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: imageData })
        })
        .then(res => res.json())
        .then(data => {
            saveAndRedirect(data.happy || 0, data.sad || 0, data.neutral || 0, data.emotion || 'neutral');
        })
        .catch(() => {
            saveAndRedirect(0, 0, 100, 'neutral');
        });
        return;
    }

    const total = finalHappy + finalSad + finalNeutral || 1;
    finalHappy = Number(((finalHappy / total) * 100).toFixed(2));
    finalSad = Number(((finalSad / total) * 100).toFixed(2));
    finalNeutral = Number(((finalNeutral / total) * 100).toFixed(2));

    let domEmotion = "neutral";
    if (finalHappy >= finalSad && finalHappy >= finalNeutral) domEmotion = "happy";
    else if (finalSad >= finalHappy && finalSad >= finalNeutral) domEmotion = "sad";

    saveAndRedirect(finalHappy, finalSad, finalNeutral, domEmotion);
}

function saveAndRedirect(happy, sad, neutral, dominant_emotion) {
    fetch("/save-face-result/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            happy: happy,
            sad: sad,
            neutral: neutral,
            dominant_emotion: dominant_emotion
        })
    })
    .then(response => response.json())
    .then(() => {
        status.innerHTML = "Analysis Completed";
        window.location.href = "/result/";
    })
    .catch(error => {
        console.error("Save error:", error);
        status.innerHTML = "Analysis Failed";
    });
}

stopBtn.onclick = function() {
    isAnalyzing = false;
    clearInterval(timer);
    clearInterval(analysisInterval);
    overlayCtx.clearRect(0, 0, overlay.width, overlay.height);
    status.innerHTML = "Stopped";
};

function goNext() {
    window.location.href = "/result/";
}