const API_BASE = "http://127.0.0.1:8000";

const $ = (sel) => document.querySelector(sel);

const form = $("#loan-form");
const submitBtn = $("#submit-btn");
const resetBtn = $("#reset-btn");
const refreshBtn = $("#refresh-btn");

const resultEl = $("#form-result");
const errorsEl = $("#form-errors");

const listEl = $("#loan-list");

const detailCard = $("#detail-card");
const detailEl = $("#loan-detail");
const scheduleBody = $("#schedule-body");

$("#api-base").textContent = API_BASE;

function money(x) {
  const n = Number(x);
  if (Number.isNaN(n)) return String(x);
  return n.toFixed(2);
}

function clearFormMessages() {
  resultEl.innerHTML = "";
  errorsEl.innerHTML = "";
}

function showErrors(messages) {
  if (!messages || messages.length === 0) {
    errorsEl.innerHTML = "";
    return;
  }
  errorsEl.innerHTML = `
    <div class="error-box">
      <strong>Please fix the following:</strong>
      <ul>${messages.map((m) => `<li>${m}</li>`).join("")}</ul>
    </div>
  `;
}

function parseFastApiValidation(errJson) {
  if (!errJson || !errJson.detail) return ["Request failed. Please try again."];
  if (typeof errJson.detail === "string") return [errJson.detail];

  if (Array.isArray(errJson.detail)) {
    return errJson.detail.map((e) => {
      const field = Array.isArray(e.loc) ? e.loc[e.loc.length - 1] : "field";
      return `${field}: ${e.msg}`;
    });
  }
  return ["Request failed. Please try again."];
}

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const contentType = res.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const data = isJson ? await res.json().catch(() => null) : await res.text().catch(() => null);

  if (!res.ok) {
    const err = new Error("API error");
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}

function renderLoanList(loans) {
  if (!loans || loans.length === 0) {
    listEl.innerHTML = `<p class="muted">No saved scenarios yet.</p>`;
    return;
  }

  listEl.innerHTML = loans
    .map((l) => {
      return `
        <button class="list-item" data-id="${l.id}">
          <div class="list-main">
            <div><strong>$${money(l.amount)}</strong> at <strong>${money(l.apr)}%</strong></div>
            <div class="muted small">Term: ${l.term_months} months</div>
          </div>
          <div class="pill">$${money(l.monthly_payment)}/mo</div>
        </button>
      `;
    })
    .join("");

  // click handlers
  document.querySelectorAll(".list-item").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.getAttribute("data-id");
      await loadLoanDetail(id);
    });
  });
}

function renderLoanDetail(d) {
  detailEl.innerHTML = `
    <div class="detail-grid">
      <div><span class="muted">Amount</span><div><strong>$${money(d.amount)}</strong></div></div>
      <div><span class="muted">APR</span><div><strong>${money(d.apr)}%</strong></div></div>
      <div><span class="muted">Term</span><div><strong>${d.term_months} months</strong></div></div>
      <div><span class="muted">Monthly Payment</span><div><strong>$${money(d.monthly_payment)}</strong></div></div>
    </div>
  `;

  const rows = d.schedule_preview || [];
  scheduleBody.innerHTML = rows
    .map((r) => {
      return `
        <tr>
          <td>${r.month}</td>
          <td>$${money(r.interest_paid)}</td>
          <td>$${money(r.principal_paid)}</td>
          <td>$${money(r.remaining_balance)}</td>
        </tr>
      `;
    })
    .join("");

  detailCard.hidden = false;
}

async function loadLoans() {
  try {
    const loans = await api("/loans");
    renderLoanList(loans);
  } catch (e) {
    listEl.innerHTML = `<p class="error">Failed to load loans. Is the backend running?</p>`;
  }
}

async function loadLoanDetail(id) {
  try {
    const d = await api(`/loans/${id}`);
    renderLoanDetail(d);
  } catch (e) {
    const msg = e.status === 404 ? "Loan not found (404)." : "Failed to load loan detail.";
    alert(msg);
  }
}

form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  clearFormMessages();

  const amount = Number($("#amount").value);
  const apr = Number($("#apr").value);
  const term_months = Number($("#term_months").value);

  submitBtn.disabled = true;
  submitBtn.textContent = "Saving...";

  try {
    const created = await api("/loans", {
      method: "POST",
      body: JSON.stringify({ amount, apr, term_months }),
    });

    resultEl.innerHTML = `
      <div class="success">
        Saved! Monthly payment: <strong>$${money(created.monthly_payment)}</strong>
      </div>
    `;

    await loadLoans();
    await loadLoanDetail(created.id);
  } catch (e) {
    const messages = parseFastApiValidation(e.data);
    showErrors(messages);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Calculate & Save";
  }
});

resetBtn.addEventListener("click", () => {
  form.reset();
  clearFormMessages();
});

refreshBtn.addEventListener("click", async () => {
  await loadLoans();
});
loadLoans();
