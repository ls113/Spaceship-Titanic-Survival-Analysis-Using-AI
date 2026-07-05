let chart; // global chart

function makePrediction() {
    const data = {
        age: parseFloat(document.getElementById("age").value),
        spending: parseFloat(document.getElementById("spending").value),
        cryosleep: document.getElementById("cryosleep").value === "yes" ? 1 : 0,
        vip: document.getElementById("vip").value === "yes" ? 1 : 0
    };

    fetch("/predict_api", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(res => {
        if (res.error) {
            document.getElementById("result").innerHTML =
                "❌ Error: " + res.error;
            return;
        }

        document.getElementById("result").innerHTML = `
            <h2>${res.result}</h2>
            <p>Risk Score: ${res.risk}%</p>
            <p>Confidence: ${res.confidence}</p>
        `;
    })
    .catch(err => {
        document.getElementById("result").innerHTML =
            "❌ Prediction Failed";
        console.error(err);
    });
}

function sendMessage() {
    let input = document.getElementById("userInput").value;
    let chatbox = document.getElementById("chatbox");

    let userMsg = `<p><b>You:</b> ${input}</p>`;
    chatbox.innerHTML += userMsg;

    let botReply = "🤖 AI: ";

    if(input.toLowerCase().includes("model"))
        botReply += "We use Random Forest for prediction.";
    else if(input.toLowerCase().includes("accuracy"))
        botReply += "Accuracy is around 85%.";
    else
        botReply += "Ask about prediction, model, or data.";

    chatbox.innerHTML += `<p>${botReply}</p>`;
}

function startVoice() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

    recognition.onresult = function(event) {
        let text = event.results[0][0].transcript;

        // simple number extraction
        let number = text.match(/\d+/);
        if (number) {
            document.getElementById("age").value = number[0];
        }
    };

    recognition.start();
}

// ================= FILE UPLOAD =================
function uploadFile() {
    const fileInput = document.getElementById("file");
    const status = document.getElementById("status");

    if (!fileInput.files.length) {
        status.innerText = "❌ Please select a file first";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    status.innerHTML = '<div class="loader"></div>';

    fetch('/upload_csv', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            status.innerText = "❌ " + data.error;
        } else {
            status.innerText = "✅ " + data.status;
        }
    })
    .catch(err => {
        status.innerText = "❌ Upload failed";
        console.log(err);
    });
}

// ================= CONFUSION MATRIX =================
fetch('/confusion_matrix')
.then(res => res.json())
.then(data => {
    const ctx = document.getElementById("confusionChart");

    if (ctx) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ["TP", "FP", "FN", "TN"],
                datasets: [{
                    label: "Confusion Matrix",
                    data: [data.tp, data.fp, data.fn, data.tn]
                }]
            }
        });
    }
});

// ================= PDF DOWNLOAD =================
function downloadReport() {
    // 1. Force a tiny delay to ensure all dynamic elements (like IEEE formatting) are rendered
    setTimeout(() => {
        const element = document.getElementById('report-content') || document.querySelector('.container');
        
        const options = {
            margin: 0.5,
            filename: `Research_Report_${new Date().getTime()}.pdf`, // Adding timestamp ensures a unique file
            html2canvas: { 
                scale: 2, 
                useCORS: true, 
                logging: true // This helps you see if it's capturing the wrong thing in the console
            },
            jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
        };

        html2pdf().set(options).from(element).save();
    }, 100); 
}

// ================= DEPLOY STEPS =================
function showDeploy() {
    document.getElementById("deploySteps").innerHTML = `
        <ul>
            <li>Push code to GitHub</li>
            <li>Go to Render.com</li>
            <li>Create Web Service</li>
            <li>Connect repo</li>
            <li>Click Deploy 🚀</li>
        </ul>
    `;
}