document.addEventListener('DOMContentLoaded', () => {
    const inputPage = document.getElementById('input-page');
    const loadingPage = document.getElementById('loading-page');
    const resultsPage = document.getElementById('results-page');
    const resultsContainer = document.getElementById('results-container');
    const recommendBtn = document.getElementById('recommend-btn');
    const backBtn = document.getElementById('back-btn');

    // ── Modal elements ──────────────────────────────────────
    const modal = document.getElementById('steps-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalSteps = document.getElementById('modal-steps');
    const modalClose = document.getElementById('modal-close');

    modalClose.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });

    function openModal(menuName, steps) {
        modalTitle.textContent = `📋 วิธีทำ: ${menuName}`;
        modalSteps.innerHTML = '';
        if (!steps || steps.length === 0) {
            modalSteps.innerHTML = '<p class="no-steps">ไม่มีข้อมูลขั้นตอน</p>';
        } else {
            steps.forEach((step, i) => {
                const li = document.createElement('li');
                li.className = 'step-item';
                // strip prefix like "ขั้นตอนที่ 1: " if Gemini already added it
                const text = step.replace(/^ขั้นตอนที่\s*\d+\s*:\s*/i, '').trim();
                li.innerHTML = `<span class="step-num">${i + 1}</span><span class="step-text">${text}</span>`;
                modalSteps.appendChild(li);
            });
        }
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }

    // ── Recommend button ─────────────────────────────────────
    recommendBtn.addEventListener('click', async () => {
        const ingredients = document.getElementById('ingredients').value;
        const equipment = document.getElementById('equipment').value;

        if (!ingredients) {
            alert('กรุณาบอกวัตถุดิบที่มีก่อนนะคะ');
            return;
        }

        inputPage.classList.add('hidden');
        loadingPage.classList.remove('hidden');

        try {
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ingredients, equipment })
            });

            if (!response.ok) throw new Error('Failed to get recommendations');

            const data = await response.json();
            displayResults(data.recommendations);

            loadingPage.classList.add('hidden');
            resultsPage.classList.remove('hidden');
        } catch (error) {
            console.error(error);
            alert('โอย ป้าศรีเวียนหัวนิดหน่อยจ้า ลองใหม่อีกทีนะ');
            loadingPage.classList.add('hidden');
            inputPage.classList.remove('hidden');
        }
    });

    backBtn.addEventListener('click', () => {
        resultsPage.classList.add('hidden');
        inputPage.classList.remove('hidden');
        resultsContainer.innerHTML = '';
    });

    // ── Render cards ─────────────────────────────────────────
    function displayResults(menus) {
        resultsContainer.innerHTML = '';
        menus.forEach(menu => {
            const diffClass = menu.difficulty === 'ยาก' ? 'diff-hard'
                            : menu.difficulty === 'ปานกลาง' ? 'diff-medium'
                            : 'diff-easy';

            const recId = menu.recommendation_id || '';
            const steps = menu.steps || [];

            const card = document.createElement('div');
            card.className = 'menu-card';
            card.dataset.recommendationId = recId;
            card.dataset.steps = JSON.stringify(steps);
            card.dataset.menuName = menu.menu_name;

            card.innerHTML = `
                <span class="tag ${diffClass}">${menu.difficulty}</span>
                <h3>${menu.menu_name}</h3>
                <div class="missing-tags">
                    ${(menu.missing_ingredients || []).map(item => `<span class="missing-item">+ ${item}</span>`).join('')}
                </div>
                <p class="reason-text">${menu.reason || ''}</p>
                <div class="card-actions">
                    <button class="btn-steps" onclick="showSteps(this)">📋 วิธีทำ</button>
                    <button class="btn-select" onclick="selectMenu('${menu.menu_name}', this)">เลือกเมนูนี้</button>
                    <button class="btn-reject" onclick="rejectMenu('${menu.menu_name}', this)">ไม่เหมาะสม</button>
                </div>
            `;
            resultsContainer.appendChild(card);
        });
    }

    // ── Helpers ───────────────────────────────────────────────
    function getCard(btn) {
        return btn.closest('.menu-card');
    }

    function getRecommendationId(btn) {
        const card = getCard(btn);
        return card ? card.dataset.recommendationId : null;
    }

    // ── Show steps modal ──────────────────────────────────────
    window.showSteps = (btn) => {
        const card = getCard(btn);
        const menuName = card.dataset.menuName || '';
        const steps = JSON.parse(card.dataset.steps || '[]');
        openModal(menuName, steps);
    };

    // ── Select menu ───────────────────────────────────────────
    window.selectMenu = async (menuName, btn) => {
        const recommendationId = getRecommendationId(btn);
        if (!recommendationId) {
            alert('เกิดข้อผิดพลาด: ไม่พบ ID ของเมนูนี้ กรุณาลองขอคำแนะนำใหม่อีกครั้ง');
            return;
        }

        const origText = btn.innerText;
        btn.innerText = 'กำลังบันทึก...';
        btn.disabled = true;

        try {
            const res = await fetch('/api/select-menu', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ recommendation_id: recommendationId, menu_name: menuName })
            });
            if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Server error'); }

            btn.innerText = 'บันทึกแล้ว! ✓';
            btn.style.background = '#0984e3';
        } catch (error) {
            console.error('selectMenu error:', error);
            alert('บันทึกไม่สำเร็จ: ' + error.message);
            btn.innerText = origText;
            btn.disabled = false;
        }
    };

    // ── Reject menu ───────────────────────────────────────────
    window.rejectMenu = async (menuName, btn) => {
        const recommendationId = getRecommendationId(btn);
        if (!recommendationId) {
            alert('เกิดข้อผิดพลาด: ไม่พบ ID ของเมนูนี้ กรุณาลองขอคำแนะนำใหม่อีกครั้ง');
            return;
        }

        const origText = btn.innerText;
        btn.innerText = '...';
        btn.disabled = true;

        try {
            const res = await fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    recommendation_id: recommendationId,
                    rating: 2,
                    comment: `ไม่เหมาะสม: ${menuName}`
                })
            });
            if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Server error'); }

            btn.innerText = 'ส่งแล้ว ✓';
            btn.style.opacity = '0.5';
        } catch (error) {
            console.error('rejectMenu error:', error);
            alert('ส่ง feedback ไม่สำเร็จ: ' + error.message);
            btn.innerText = origText;
            btn.disabled = false;
        }
    };
});
