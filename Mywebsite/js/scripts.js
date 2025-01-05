document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    const links = document.querySelectorAll('a[href^="#"]');
    for (const link of links) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    }

    // Parallax effect
    document.addEventListener('scroll', function() {
        const parallax = document.querySelector('.parallax-section');
        let scrollPosition = window.pageYOffset;
        parallax.style.backgroundPositionY = scrollPosition * 0.5 + 'px';
    });

    // Slider functionality
    const sliderContainer = document.querySelector('.slider-container');
    const slider = document.querySelector('.expertise-list');
    const prevButton = document.querySelector('.slider-button.prev');
    const nextButton = document.querySelector('.slider-button.next');
    let scrollAmount = 0;

    nextButton.addEventListener('click', function() {
        const maxScroll = slider.scrollWidth - sliderContainer.clientWidth;
        if (scrollAmount < maxScroll) {
            scrollAmount += sliderContainer.clientWidth;
            slider.style.transform = `translateX(-${scrollAmount}px)`;
        }
    });

    prevButton.addEventListener('click', function() {
        if (scrollAmount > 0) {
            scrollAmount -= sliderContainer.clientWidth;
            slider.style.transform = `translateX(-${scrollAmount}px)`;
        }
    });

    // Stock ticker functionality
    const apiKey = 'FFQQPZQ5LRINPNWZ'; // Your Alpha Vantage API key
    const symbols = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA']; // Individual stocks
    const tickerMove = document.getElementById('ticker-move');

    function fetchStockData(symbol) {
        return fetch(`https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${apiKey}`)
            .then(response => response.json())
            .then(data => {
                console.log(data); // Log the response to check if it's correct
                if (data['Global Quote']) {
                    const quote = data['Global Quote'];
                    const price = quote['05. price'];
                    const change = quote['09. change'];
                    const trend = parseFloat(change) >= 0 ? '▲' : '▼';
                    return `${symbol}: $${parseFloat(price).toFixed(2)} ${trend}`;
                } else {
                    console.error(`No data found for symbol: ${symbol}`, data);
                    return `${symbol}: Data not available`;
                }
            })
            .catch(error => {
                console.error('Error fetching data for symbol:', symbol, error);
                return `${symbol}: Error fetching data`;
            });
    }

    async function updateTicker() {
        tickerMove.innerHTML = ''; // Clear existing ticker items
        for (const symbol of symbols) {
            const tickerItem = document.createElement('div');
            tickerItem.className = 'ticker-item';
            tickerItem.textContent = await fetchStockData(symbol);
            tickerMove.appendChild(tickerItem);
        }
    }

    updateTicker();
    setInterval(updateTicker, 60000); // Update every 60 seconds
});