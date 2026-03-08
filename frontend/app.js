const API_URL = ''; // Relative to the served port

async function fetchProducts() {
    const loader = document.getElementById('main-loader');
    loader.style.display = 'flex';

    try {
        const response = await fetch(`${API_URL}/api/products`);
        const products = await response.json();
        renderProducts(products);
    } catch (error) {
        console.error('Failed to fetch products:', error);
    } finally {
        loader.style.display = 'none';
    }
}

async function triggerScan() {
    const btn = document.getElementById('scan-now-btn');
    if (!btn) return;

    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = '⏳ 스캔 중...';

    try {
        const response = await fetch(`${API_URL}/api/scan-now`, { method: 'POST' });
        const data = await response.json();

        if (response.ok) {
            alert(data.message || '스캔이 시작되었습니다.');
        } else {
            // Handle cases like 405 Method Not Allowed or 404
            const errorMsg = data.detail || '서버 오류가 발생했습니다.';
            alert(`⚠️ 오류: ${errorMsg}\n\n봇을 껐다 다시 켜보셨나요?`);
        }
    } catch (error) {
        console.error('Scan failed:', error);
        alert('요청에 실패했습니다. 네트워크 연결을 확인해 주세요.');
    } finally {
        btn.disabled = false;
        btn.innerText = originalText;
    }
}

function renderProducts(products) {
    const list = document.getElementById('product-list');
    const existingProducts = list.querySelectorAll('.product-card');
    existingProducts.forEach(el => el.remove());

    document.getElementById('product-count').innerText = `${products.length} items`;

    products.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card glass';
        card.innerHTML = `
            <img src="${product.thumbnail || 'https://via.placeholder.com/300x180?text=No+Image'}" alt="${product.name}" class="product-img">
            <div class="product-info">
                <h3>${product.name}</h3>
                <p class="price-tag">${product.current_price.toLocaleString()}원</p>
                <p style="font-size: 0.7rem; color: #8b949e; margin-top: 5px;">등록일: ${new Date(product.created_at).toLocaleDateString()}</p>
            </div>
            <div class="product-actions">
                <button class="btn-small" onclick="showHistory(${product.id}, '${product.name.replace(/'/g, "\\'")}')">기록 보기</button>
                <button class="btn-small btn-delete" onclick="deleteProduct(${product.id})">삭제</button>
            </div>
        `;
        list.appendChild(card);
    });
}

async function addProduct() {
    const urlInput = document.getElementById('product-url');
    const url = urlInput.value.trim();
    if (!url) return alert('URL을 입력해주세요.');

    const btn = document.getElementById('add-btn');
    const originalText = btn.innerText;
    btn.innerText = '추가 중...';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/api/products`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        if (response.ok) {
            urlInput.value = '';
            fetchProducts();
        } else {
            const err = await response.json();
            alert(`오류: ${err.detail}`);
        }
    } catch (error) {
        alert('상품 추가에 실패했습니다.');
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

async function deleteProduct(id) {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
        await fetch(`${API_URL}/api/products/${id}`, { method: 'DELETE' });
        fetchProducts();
    } catch (error) {
        alert('삭제 실패');
    }
}

async function showHistory(id, name) {
    const modal = document.getElementById('history-modal');
    const list = document.getElementById('history-list');
    document.getElementById('modal-title').innerText = `${name} - 가격 변동`;
    list.innerHTML = '<li>로딩 중...</li>';
    modal.style.display = 'block';

    try {
        const response = await fetch(`${API_URL}/api/history/${id}`);
        const history = await response.json();

        if (history.length === 0) {
            list.innerHTML = '<li>변동 기록이 없습니다.</li>';
        } else {
            list.innerHTML = history.map(h => `
                <li class="history-item">
                    <span>${new Date(h.timestamp).toLocaleString()}</span>
                    <span style="font-weight: bold; color: #58a6ff;">${h.price.toLocaleString()}원</span>
                </li>
            `).join('');
        }
    } catch (error) {
        list.innerHTML = '<li>데이터 로드 실패</li>';
    }
}

// Event Listeners
document.getElementById('add-btn').addEventListener('click', addProduct);
window.onclick = (event) => {
    const modal = document.getElementById('history-modal');
    if (event.target == modal) modal.style.display = "none";
}
document.querySelector('.close').onclick = () => {
    document.getElementById('history-modal').style.display = "none";
}

// Init
fetchProducts();
