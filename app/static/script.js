// Global değişkenler: Önceki değerleri saklamak için
let previousTopBarRates = {};
let previousTableRates = {};

// Üst bardaki oranları güncelleyen fonksiyon (güncellenmiş versiyon)
function updateTopBarRates(rates) {
  for (let key in rates) {
    // Her key için ilgili elementin ID'si: "rate_" + key
    let newValue = parseFloat(rates[key]);
    let element = document.getElementById("rate_" + key);
    if (element) {
      let valueSpan = element.querySelector(".rate-value");
      let indicatorSpan = element.querySelector(".rate-indicator");

      if (previousTopBarRates[key] !== undefined) {
        let prevValue = previousTopBarRates[key];
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
      valueSpan.textContent = rates[key];
      previousTopBarRates[key] = newValue;
    }
  }
}

// Döviz kurları tablosunu güncelleyen fonksiyon (varsa)
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
    tdRate.appendChild(indicatorSpan);

    row.appendChild(tdCurrency);
    row.appendChild(tdRate);
    tbody.appendChild(row);

    previousTableRates[currency] = newValue;
  }
}

let previousBitcoinPrice = null;
function updateBitcoinInfo(newPrice) {
  const bitcoinPriceElement = document.getElementById("bitcoin-price");
  const bitcoinIndicatorElement = document.getElementById("bitcoin-indicator");
  const newPriceFloat = parseFloat(newPrice);

  if (bitcoinPriceElement) {
    bitcoinPriceElement.textContent = newPrice;
  }

  if (bitcoinIndicatorElement && previousBitcoinPrice !== null) {
    if (newPriceFloat > previousBitcoinPrice) {
      bitcoinIndicatorElement.innerHTML = "&#9650;"; // Yeşil yukarı ok
      bitcoinIndicatorElement.className = "rate-indicator green";
    } else if (newPriceFloat < previousBitcoinPrice) {
      bitcoinIndicatorElement.innerHTML = "&#9660;"; // Kırmızı aşağı ok
      bitcoinIndicatorElement.className = "rate-indicator red";
    } else {
      bitcoinIndicatorElement.innerHTML = "";
      bitcoinIndicatorElement.className = "rate-indicator neutral";
    }
  }

  previousBitcoinPrice = newPriceFloat;
}

let previousCryptoPrices = {};
function updateOtherCryptoRates(cryptoData) {
  for (const crypto in cryptoData) {
    const details = cryptoData[crypto];
    const newPrice = details.price_try;
    const newPriceFloat = parseFloat(newPrice);
    const priceElement = document.getElementById("crypto-" + crypto + "-price");
    const indicatorElement = document.getElementById("crypto-" + crypto + "-indicator");

    if (priceElement && indicatorElement) {
      priceElement.textContent = newPrice;
      if (previousCryptoPrices[crypto] !== undefined) {
        const prevPrice = previousCryptoPrices[crypto];
        if (newPriceFloat > prevPrice) {
          indicatorElement.innerHTML = "&#9650;";
          indicatorElement.className = "rate-indicator green";
        } else if (newPriceFloat < prevPrice) {
          indicatorElement.innerHTML = "&#9660;";
          indicatorElement.className = "rate-indicator red";
        } else {
          indicatorElement.innerHTML = "";
          indicatorElement.className = "rate-indicator neutral";
        }
      }
      previousCryptoPrices[crypto] = newPriceFloat;
    }
  }
}

let previousAssetPrices = {};
function updateAssetRates(assetData) {
  for (const asset in assetData) {
    const newPrice = assetData[asset];
    const newPriceFloat = parseFloat(newPrice);
    const priceElement = document.getElementById("asset-" + asset);
    const indicatorElement = document.getElementById("asset-" + asset + "-indicator");

    if (priceElement && indicatorElement) {
      priceElement.textContent = newPrice;
      if (previousAssetPrices[asset] !== undefined) {
        const prevPrice = previousAssetPrices[asset];
        if (newPriceFloat > prevPrice) {
          indicatorElement.innerHTML = "&#9650;";
          indicatorElement.className = "rate-indicator green";
        } else if (newPriceFloat < prevPrice) {
          indicatorElement.innerHTML = "&#9660;";
          indicatorElement.className = "rate-indicator red";
        } else {
          indicatorElement.innerHTML = "";
          indicatorElement.className = "rate-indicator neutral";
        }
      }
      previousAssetPrices[asset] = newPriceFloat;
    }
  }
}

// Verileri çekip güncelleyen fonksiyon (örneğin her 60 saniyede)
function fetchData() {
  fetch("/api/data")
    .then(response => response.json())
    .then(data => {
      // Üst bar için tüm verileri birleştiriyoruz:
      let combinedRates = {};

      if (data.exchange_rates) {
        // exchange_rates'deki USD, EUR, GBP gibi değerler
        combinedRates = { ...data.exchange_rates };
      }

      if (data.asset_prices) {
        // asset_prices'deki değerler; context processor'da live_rates için
        // key isimleri üst bardaki elementlerle uyumlu olacak şekilde ayarlanmalı:
        combinedRates.GramAltin = data.asset_prices.gram_altin;
        combinedRates.OnsAltin = data.asset_prices.ons_altin;
        combinedRates.Gumus = data.asset_prices.gumus;
        combinedRates.BIST100 = data.asset_prices.bist100;
      }

      if (data.crypto_usd) {
        // crypto_usd'deki değerler; örneğin: bitcoin => BTCUSD
        combinedRates.BTCUSD = data.crypto_usd.bitcoin;
        combinedRates.ETHUSD = data.crypto_usd.ethereum;
        combinedRates.XRPUSD = data.crypto_usd.ripple;
      }

      // Üst barı güncelle
      updateTopBarRates(combinedRates);

      // Diğer bölümleri güncelle
      if (data.exchange_rates) {
        updateExchangeRates(data.exchange_rates);
      }
      if (data.bitcoin_price) {
        updateBitcoinInfo(data.bitcoin_price);
      }
      if (data.other_crypto) {
        updateOtherCryptoRates(data.other_crypto);
      }
      if (data.asset_prices) {
        updateAssetRates(data.asset_prices);
      }
      // updateAlarmStatus(data.alarm_triggered); // Eğer alarm sistemi varsa
    })
    .catch(error => console.error("Veri çekilirken hata:", error));
}

document.addEventListener("DOMContentLoaded", function() {
  if (
    document.querySelector("#rates-table") ||
    document.getElementById("rate_USD") ||
    document.getElementById("bitcoin-price")
  ) {
    fetchData();
    setInterval(fetchData, 60000);
  }
});
