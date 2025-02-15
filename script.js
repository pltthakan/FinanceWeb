// Global değişkenler: Önceki değerleri saklamak için
let previousTopBarRates = {};
let previousTableRates = {};

// Üst bardaki oranları güncelleyen fonksiyon (zaten mevcut olanı kullanıyoruz)
function updateTopBarRates(rates) {
  for (let currency in rates) {
    let newValue = parseFloat(rates[currency]);
    let element = document.getElementById("rate_" + currency);
    if (element) {
      let valueSpan = element.querySelector(".rate-value");
      let indicatorSpan = element.querySelector(".rate-indicator");

      if (previousTopBarRates[currency] !== undefined) {
        let prevValue = previousTopBarRates[currency];
        if (newValue > prevValue) {
          indicatorSpan.innerHTML = "&#9650;"; // ▲
          indicatorSpan.className = "rate-indicator green";
        } else if (newValue < prevValue) {
          indicatorSpan.innerHTML = "&#9660;"; // ▼
          indicatorSpan.className = "rate-indicator red";
        } else {
          indicatorSpan.innerHTML = "";
          indicatorSpan.className = "rate-indicator neutral";
        }
      }
      valueSpan.textContent = rates[currency];
      previousTopBarRates[currency] = newValue;
    }
  }
}

// Döviz kurları tablosunu güncelleyen fonksiyonu, artış/azalış simgesi ekleyerek güncelliyoruz
function updateExchangeRates(rates) {
  let tbody = document.querySelector("#rates-table tbody");
  if (!tbody) return;
  tbody.innerHTML = "";
  for (const currency in rates) {
    let row = document.createElement("tr");

    // Para birimi adı hücresi
    let tdCurrency = document.createElement("td");
    tdCurrency.textContent = currency;

    // Döviz kuru hücresi
    let tdRate = document.createElement("td");
    let rateValue = rates[currency];
    tdRate.textContent = rateValue;

    // Karşılaştırma yaparak simge ekle
    let indicatorSpan = document.createElement("span");
    indicatorSpan.classList.add("rate-indicator");

    let newValue = parseFloat(rateValue);
    if (previousTableRates[currency] !== undefined && !isNaN(newValue)) {
      let prevValue = previousTableRates[currency];
      if (newValue > prevValue) {
        indicatorSpan.innerHTML = " &#9650;"; // yeşil yukarı ok
        indicatorSpan.classList.add("green");
      } else if (newValue < prevValue) {
        indicatorSpan.innerHTML = " &#9660;"; // kırmızı aşağı ok
        indicatorSpan.classList.add("red");
      }
    }
    // Hücreye simgeyi ekle
    tdRate.appendChild(indicatorSpan);

    row.appendChild(tdCurrency);
    row.appendChild(tdRate);
    tbody.appendChild(row);

    // Önceki değeri güncelle
    previousTableRates[currency] = newValue;
  }
}

// Verileri çekip güncelleyen fonksiyon (örneğin her 60 saniyede)
function fetchData() {
  fetch("/api/data")
    .then(response => response.json())
    .then(data => {
      if (data.exchange_rates) {
        updateExchangeRates(data.exchange_rates);
        updateTopBarRates(data.exchange_rates);
      }
      updateAlarmStatus(data.alarm_triggered);
    })
    .catch(error => console.error("Veri çekilirken hata:", error));
}

document.addEventListener("DOMContentLoaded", function() {
  if (document.querySelector("#rates-table") || document.getElementById("rate_USD")) {
    fetchData();
    setInterval(fetchData, 60000);
  }
});
