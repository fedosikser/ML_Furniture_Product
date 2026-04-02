const form = document.getElementById("extract-form");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");

const setList = (id, values, fallback) => {
  const node = document.getElementById(id);
  node.innerHTML = "";
  const items = values.length ? values : [fallback];
  items.forEach((value) => {
    const li = document.createElement("li");
    li.textContent = value;
    node.appendChild(li);
  });
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const url = document.getElementById("url").value.trim();
  statusEl.textContent = "Fetching page and extracting candidates...";
  resultEl.classList.add("hidden");

  try {
    const response = await fetch("/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    const payload = await response.json();

    document.getElementById("result-status").textContent = payload.status || "-";
    document.getElementById("result-page-type").textContent = payload.page_type || "-";
    document.getElementById("result-top-product").textContent =
      payload.top_product || "Not found";
    document.getElementById("result-processing").textContent = payload.processing_ms
      ? `${payload.processing_ms} ms`
      : "-";
    document.getElementById("result-message").textContent =
      payload.message || "Extraction completed.";

    setList("result-products", payload.products || [], "No products detected");
    setList("result-sources", payload.sources || [], "No sources recorded");

    statusEl.textContent =
      payload.status === "ok"
        ? "Extraction completed successfully."
        : "Extraction failed.";
    resultEl.classList.remove("hidden");
  } catch (error) {
    statusEl.textContent = "Request failed. Make sure the server is running.";
    document.getElementById("result-message").textContent =
      error instanceof Error ? error.message : "Unknown error";
    resultEl.classList.remove("hidden");
  }
});
