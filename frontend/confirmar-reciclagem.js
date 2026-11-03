/* =========================================================
   EcoHora — confirmação de entrega por QR Code
   O backend valida sessão, perfil, validade e uso único.
========================================================= */

(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const token = new URLSearchParams(window.location.search).get("token");
  const BRANCH_FRONTEND_URL = "https://acex-reciclagem-kluhcio40-leogouvea.vercel.app";
  const HOLD_DURATION_MS = 1200;

  const alertBox = $("confirmAlert");
  const details = $("deliveryDetails");
  const confirmButton = $("confirmButton");
  const loginLink = $("loginLink");
  const panelLink = $("panelLink");
  const successPanel = $("successPanel");
  const holdLabel = $("confirmButtonLabel");
  const holdHint = $("confirmHoldHint");
  let holdTimer = null;

  const numberFormat = new Intl.NumberFormat("pt-BR", {
    maximumFractionDigits: 2,
  });

  function formatNumber(value) {
    const number = Number(value);
    return Number.isFinite(number) ? numberFormat.format(number) : "—";
  }

  function setAlert(message, kind = "info") {
    alertBox.textContent = message;
    alertBox.dataset.kind = kind;
    alertBox.hidden = false;
  }

  function hideActions() {
    confirmButton.hidden = true;
    loginLink.hidden = true;
    panelLink.hidden = true;
    holdHint.hidden = true;
  }

  function showApiError(error) {
    const message = error?.message || "Não foi possível consultar esta entrega.";

    hideActions();
    details.hidden = true;
    $("deliveryExpiration").hidden = true;

    if (
      message.includes("Acesso negado") ||
      message.includes("login expirado") ||
      message.includes("token falso") ||
      message.includes("realize login")
    ) {
      setAlert(
        "Para confirmar esta entrega, entre na sua conta de aluno e abra novamente o QR Code.",
        "error"
      );
      loginLink.href = `${BRANCH_FRONTEND_URL}/login.html?redirect=${encodeURIComponent(
        `${BRANCH_FRONTEND_URL}/confirmar-reciclagem.html?token=${token}`
      )}`;
      loginLink.hidden = false;
      return;
    }

    if (message.includes("Você não tem permissão")) {
      setAlert(
        "Esta confirmação só pode ser realizada por uma conta de aluno. Se você entrou como administrador, troque para sua conta de aluno e leia o QR Code novamente.",
        "error"
      );
      panelLink.href = `${BRANCH_FRONTEND_URL}/index.html`;
      panelLink.hidden = false;
      return;
    }

    if (message.includes("já foi confirmada")) {
      setAlert("Este QR Code já foi utilizado. Cada entrega pode ser confirmada uma única vez.", "error");
      return;
    }

    if (message.includes("expirou")) {
      setAlert("Este QR Code expirou. Solicite ao responsável um novo código para a entrega.", "error");
      return;
    }

    if (message.includes("inválido") || message.includes("não encontrado")) {
      setAlert("Não encontramos uma entrega válida para este QR Code. Confira o link ou solicite um novo código.", "error");
      return;
    }

    setAlert(
      "Não foi possível comunicar com o EcoHora neste momento. Verifique sua conexão e tente novamente.",
      "error"
    );
  }

  function renderDelivery(delivery) {
    $("deliveryMaterial").textContent = delivery.material || "Material não informado";
    $("deliveryWeight").textContent = `${formatNumber(delivery.weight)} kg`;
    $("deliveryPoints").textContent = `${formatNumber(delivery.points)} pontos`;

    const expiration = new Date(delivery.expires_at);
    if (Number.isFinite(expiration.getTime())) {
      $("deliveryExpiration").textContent =
        `Este QR Code é válido até ${expiration.toLocaleString("pt-BR")}.`;
      $("deliveryExpiration").hidden = false;
    }

    details.hidden = false;
    confirmButton.disabled = false;
    confirmButton.hidden = false;
    setAlert("Confira os dados da entrega.", "info");
    holdHint.hidden = false;
  }

  async function loadDelivery() {
    if (!token) {
      hideActions();
      setAlert("O link não contém um código de confirmação. Leia novamente o QR Code recebido.", "error");
      return;
    }

    try {
      const delivery = await apiRequest(
        `/recycling/qr/${encodeURIComponent(token)}`
      );
      renderDelivery(delivery);
    } catch (error) {
      showApiError(error);
    }
  }

  async function confirmDelivery() {
    if (!token || confirmButton.disabled) return;

    confirmButton.disabled = true;
    holdLabel.textContent = "Confirmando...";
    setAlert("Registrando a confirmação da entrega...", "info");

    try {
      const result = await apiRequest(
        `/recycling/qr/${encodeURIComponent(token)}/confirm`,
        { method: "POST" }
      );

      confirmButton.hidden = true;
      holdHint.hidden = true;
      $("successMessage").textContent =
        result.detail || "A entrega foi confirmada e os pontos foram creditados.";
      $("earnedPoints").textContent =
        `${formatNumber(result.points_earned)} pontos`;
      $("totalPoints").textContent =
        `${formatNumber(result.total_points)} pontos`;
      successPanel.hidden = false;
      setAlert("Entrega confirmada com sucesso.", "success");
    } catch (error) {
      confirmButton.disabled = false;
      holdLabel.textContent = "Segure para confirmar entrega";
      showApiError(error);
    }
  }

  function cancelHold() {
    if (holdTimer !== null) {
      window.clearTimeout(holdTimer);
      holdTimer = null;
      confirmButton.classList.remove("is-holding");
      if (!confirmButton.disabled) {
        holdLabel.textContent = "Segure para confirmar entrega";
      }
    }
  }

  function beginHold() {
    if (confirmButton.disabled || confirmButton.hidden || holdTimer !== null) return;

    confirmButton.classList.add("is-holding");
    holdLabel.textContent = "Continue segurando...";
    holdTimer = window.setTimeout(() => {
      holdTimer = null;
      confirmButton.classList.remove("is-holding");
      holdLabel.textContent = "Confirmando...";
      confirmDelivery();
    }, HOLD_DURATION_MS);
  }

  confirmButton.addEventListener("pointerdown", (event) => {
    if (event.pointerType === "mouse" && event.button !== 0) return;
    try {
      confirmButton.setPointerCapture(event.pointerId);
    } catch {
      // Alguns navegadores não oferecem captura para todos os tipos de ponteiro.
    }
    beginHold();
  });

  ["pointerup", "pointercancel", "lostpointercapture"].forEach((eventName) => {
    confirmButton.addEventListener(eventName, cancelHold);
  });

  confirmButton.addEventListener("keydown", (event) => {
    if (event.key === " " || event.key === "Enter") {
      event.preventDefault();
      if (!event.repeat) beginHold();
    }
  });

  confirmButton.addEventListener("keyup", (event) => {
    if (event.key === " " || event.key === "Enter") {
      event.preventDefault();
      cancelHold();
    }
  });

  confirmButton.addEventListener("blur", cancelHold);

  // Ativação por tecnologia assistiva, sem evento físico de ponteiro/tecla.
  confirmButton.addEventListener("click", (event) => {
    if (event.detail === 0 && holdTimer === null && !confirmButton.disabled) {
      confirmDelivery();
    }
  });

  loadDelivery();
})();
