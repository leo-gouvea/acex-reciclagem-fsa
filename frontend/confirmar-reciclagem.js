/* =========================================================
   EcoHora — confirmação de entrega por QR Code
   O backend valida sessão, perfil, validade e uso único.
========================================================= */

(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const token = new URLSearchParams(window.location.search).get("token");

  const alertBox = $("confirmAlert");
  const details = $("deliveryDetails");
  const confirmButton = $("confirmButton");
  const loginLink = $("loginLink");
  const panelLink = $("panelLink");
  const successPanel = $("successPanel");

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
      loginLink.href = `login.html?redirect=${encodeURIComponent(
        `confirmar-reciclagem.html?token=${token}`
      )}`;
      loginLink.hidden = false;
      return;
    }

    if (message.includes("Você não tem permissão")) {
      setAlert(
        "Esta confirmação só pode ser realizada por uma conta de aluno. Se você entrou como administrador, troque para sua conta de aluno e leia o QR Code novamente.",
        "error"
      );
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
    setAlert(
      "Confira os dados. Ao confirmar, os pontos serão adicionados à sua conta.",
      "info"
    );
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
    confirmButton.textContent = "Confirmando...";
    setAlert("Registrando a confirmação da entrega...", "info");

    try {
      const result = await apiRequest(
        `/recycling/qr/${encodeURIComponent(token)}/confirm`,
        { method: "POST" }
      );

      confirmButton.hidden = true;
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
      confirmButton.textContent = "Confirmar entrega";
      showApiError(error);
    }
  }

  confirmButton.addEventListener("click", confirmDelivery);
  loadDelivery();
})();
