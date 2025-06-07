document.addEventListener("DOMContentLoaded", () => {
  const payNowBtn = document.getElementById("payNowBtn");
  const loadingSpinner = document.getElementById("loadingSpinner");

  if (!payNowBtn) return; // If no Pay Now button, do nothing

  payNowBtn.addEventListener("click", async () => {
    const orderId = getOrderIdFromDOM();
    const userEmail = getUserEmailFromDOM();
    if (!orderId || !userEmail) {
      console.error("Missing orderId or userEmail in the DOM attributes.");
      alert("Unable to proceed with payment. Contact support.");
      return;
    }

    // Show the spinner and change the button text to "Processing..."
    loadingSpinner.style.display = "inline-block";
    payNowBtn.innerHTML = 'Processing... <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';

    try {
      // Call our Paystack init route
      const response = await fetch("/api/paystack/init", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order_id: orderId, email: userEmail })
      });

      // Parse the response once
      let data;
      try {
        data = await response.json();
      } catch (parseErr) {
        throw new Error("Could not parse server response as JSON.");
      }

      // Check HTTP status
      if (!response.ok) {
        const errorMsg = data.detail || data.message || "An error occurred contacting Paystack.";
        throw new Error(errorMsg);
      }

      // Ensure we have the authorization_url
      if (!data.authorization_url) {
        throw new Error("No authorization_url received from server.");
      }

      // Redirect user to Paystack checkout
      window.location.href = data.authorization_url;
    } catch (error) {
      alert("Error: " + error.message);
      console.error("Paystack init error:", error);

      // Hide the spinner and reset button text
      loadingSpinner.style.display = "none";
      payNowBtn.innerHTML = "Pay Now";
    }
  });

  function getOrderIdFromDOM() {
    const orderInfoEl = document.getElementById("orderInfo");
    if (orderInfoEl) {
      return orderInfoEl.dataset.orderId;
    }
    const params = new URLSearchParams(window.location.search);
    return parseInt(params.get("order"), 10);
  }

  function getUserEmailFromDOM() {
    const orderInfoEl = document.getElementById("orderInfo");
    if (orderInfoEl) {
      return orderInfoEl.dataset.userEmail;
    }
    return null;
  }
});