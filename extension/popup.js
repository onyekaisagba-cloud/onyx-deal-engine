const API_URL = "https://onyx-deal-engine.onrender.com/deals.json";

document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("deals-container");
  const loader = document.getElementById("loader");
  const countBadge = document.getElementById("deal-count");

  try {
    const response = await fetch(API_URL);
    if (!response.ok) throw new Error("Network error fetching deals");
    
    const data = await response.json();
    const deals = data.deals || [];

    loader.style.display = "none";
    countBadge.textContent = `${deals.length} Live`;

    if (deals.length === 0) {
      container.innerHTML = '<div id="loader">No deals active currently. Check back soon!</div>';
      return;
    }

    // Render top deals
    deals.slice(0, 10).forEach(deal => {
      const card = document.createElement("div");
      card.className = "deal-card";
      
      const priceText = deal.price || "$0.00";
      const origPrice = deal.original_price ? `<span style="text-decoration:line-through;color:#64748b;font-size:0.75rem;margin-left:4px;">${deal.original_price}</span>` : "";

      card.innerHTML = `
        <img src="${deal.image_url || 'icons/icon48.png'}" alt="Deal">
        <div class="deal-info">
          <h4>${deal.title || 'Tech Deal'}</h4>
          <div class="deal-price">${priceText}${origPrice}</div>
          <a href="${deal.affiliate_url}" target="_blank" class="btn-claim">⚡ Get Deal</a>
        </div>
      `;
      container.appendChild(card);
    });

  } catch (error) {
    console.error("Error loading Onyx deals:", error);
    loader.textContent = "Unable to load deals. Please check your connection.";
  }
});
