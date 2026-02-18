(function () {
    "use strict";

    const form = document.getElementById("upload-form");
    const fileInput = document.getElementById("file-input");
    const dropZone = document.getElementById("drop-zone");
    const dropLabel = document.getElementById("drop-label");
    const fileName = document.getElementById("file-name");
    const analyzeBtn = document.getElementById("analyze-btn");
    const btnLoader = document.getElementById("btn-loader");
    const errorBanner = document.getElementById("error-banner");
    const errorText = document.getElementById("error-text");
    const errorClose = document.getElementById("error-close");
    const resultsSection = document.getElementById("results-section");
    const totalCount = document.getElementById("total-count");
    const highCount = document.getElementById("high-count");
    const mediumCount = document.getElementById("medium-count");
    const lowCount = document.getElementById("low-count");
    const barHigh = document.getElementById("bar-high");
    const barMedium = document.getElementById("bar-medium");
    const barLow = document.getElementById("bar-low");
    const resultsBody = document.getElementById("results-body");

    fileInput.addEventListener("change", handleFileSelect);

    function handleFileSelect() {
        const file = fileInput.files[0];
        if (file) {
            fileName.textContent = file.name;
            dropLabel.innerHTML = "File selected:";
            analyzeBtn.disabled = false;
            dropZone.classList.add("dragover");
            setTimeout(() => dropZone.classList.remove("dragover"), 600);
        } else {
            resetFileUI();
        }
    }

    function resetFileUI() {
        fileName.textContent = "";
        dropLabel.innerHTML = 'Drag & drop your CSV here or <strong>browse</strong>';
        analyzeBtn.disabled = true;
    }

    ["dragenter", "dragover"].forEach((evt) => {
        dropZone.addEventListener(evt, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add("dragover");
        });
    });

    ["dragleave", "drop"].forEach((evt) => {
        dropZone.addEventListener(evt, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove("dragover");
        });
    });

    dropZone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        if (dt.files.length) {
            fileInput.files = dt.files;
            handleFileSelect();
        }
    });

    function showError(msg) {
        errorText.textContent = msg;
        errorBanner.classList.remove("hidden");
        errorBanner.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    function hideError() {
        errorBanner.classList.add("hidden");
    }

    errorClose.addEventListener("click", hideError);

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        hideError();

        const file = fileInput.files[0];
        if (!file) {
            showError("Please select a CSV file first.");
            return;
        }

        if (!file.name.toLowerCase().endsWith(".csv")) {
            showError("Invalid file format. Only .csv files are accepted.");
            return;
        }
        
        analyzeBtn.classList.add("loading");
        analyzeBtn.disabled = true;

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("/analyze", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (!response.ok || data.error) {
                showError(data.error || "An unexpected error occurred.");
                return;
            }

            renderResults(data);
        } catch (err) {
            showError("Network error. Please ensure the server is running and try again.");
            console.error(err);
        } finally {
            analyzeBtn.classList.remove("loading");
            analyzeBtn.disabled = false;
        }
    });

    function renderResults(data) {
        const { total_projects, summary, projects } = data;

        animateCount(totalCount, total_projects);
        animateCount(highCount, summary.high);
        animateCount(mediumCount, summary.medium);
        animateCount(lowCount, summary.low);

       
        const total = total_projects || 1;
        barHigh.style.width = `${(summary.high / total) * 100}%`;
        barMedium.style.width = `${(summary.medium / total) * 100}%`;
        barLow.style.width = `${(summary.low / total) * 100}%`;

       
        resultsBody.innerHTML = "";
        projects.forEach((p) => {
            const tr = document.createElement("tr");

            
            let rankClass = "rank-other";
            if (p.rank === 1) rankClass = "rank-1";
            else if (p.rank === 2) rankClass = "rank-2";
            else if (p.rank === 3) rankClass = "rank-3";

            
            let scoreClass = "score-medium";
            if (p.priority_category === "High") scoreClass = "score-high";
            else if (p.priority_category === "Low") scoreClass = "score-low";

            const badgeClass =
                p.priority_category === "High"
                    ? "badge-high"
                    : p.priority_category === "Medium"
                        ? "badge-medium"
                        : "badge-low";

            tr.innerHTML = `
        <td><span class="rank-badge ${rankClass}">${p.rank}</span></td>
        <td class="project-name">${escapeHtml(p.project_name)}</td>
        <td>${p.impact}</td>
        <td>${p.urgency}</td>
        <td>${p.effort}</td>
        <td>${p.cost}</td>
        <td><span class="score-value ${scoreClass}">${p.priority_score}</span></td>
        <td><span class="priority-badge ${badgeClass}">${p.priority_category}</span></td>
        <td class="explanation-tag">${escapeHtml(p.explanation)}</td>
      `;
            resultsBody.appendChild(tr);
        });

        // Show results
        resultsSection.classList.remove("hidden");
        resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function animateCount(el, target) {
        const duration = 800;
        const start = 0;
        const startTime = performance.now();

        function update(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
            el.textContent = Math.round(start + (target - start) * eased);
            if (progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }
})();

