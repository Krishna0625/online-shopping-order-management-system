/* ==========================================================================
   Online Shopping & Order Management System - Frontend Script (Vanilla JS)
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {

    // 1. Live Digital Clock & Formatted Date in Top Navbar
    const clockElement = document.getElementById("live-clock");
    const dateElement = document.getElementById("current-date");

    function updateClockAndDate() {
        const now = new Date();

        if (clockElement) {
            clockElement.textContent = now.toLocaleTimeString("en-US", {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                hour12: true
            });
        }

        if (dateElement) {
            dateElement.textContent = now.toLocaleDateString("en-US", {
                weekday: "short",
                year: "numeric",
                month: "short",
                day: "numeric"
            });
        }
    }

    if (clockElement || dateElement) {
        updateClockAndDate();
        setInterval(updateClockAndDate, 1000);
    }

    // 2. Show / Hide Password Toggle on Login & Registration Pages
    const togglePasswordBtns = document.querySelectorAll(".password-toggle-btn");

    togglePasswordBtns.forEach(function (btn) {
        btn.addEventListener("click", function () {
            const wrapper = btn.closest(".input-icon-wrapper");
            const passwordInput = wrapper ? wrapper.querySelector("input") : document.getElementById("password");
            if (!passwordInput) return;

            const isPassword = passwordInput.getAttribute("type") === "password";
            passwordInput.setAttribute("type", isPassword ? "text" : "password");

            const icon = btn.querySelector("i");
            if (icon) {
                icon.className = isPassword ? "fa-regular fa-eye-slash" : "fa-regular fa-eye";
            }
            btn.setAttribute("aria-label", isPassword ? "Hide password" : "Show password");
        });
    });

    // 3. Instant Product Card Search & Filtering (Customer Homepage & Catalogue)
    const cardSearchInputs = document.querySelectorAll("[data-card-search-target]");

    cardSearchInputs.forEach(function (input) {
        const gridId = input.getAttribute("data-card-search-target");
        const grid = document.getElementById(gridId);
        const noMatchBox = document.getElementById(gridId + "-empty");
        if (!grid) return;

        input.addEventListener("input", function () {
            const query = input.value.toLowerCase().trim();
            const cards = grid.querySelectorAll(".product-card");
            let visibleCount = 0;

            cards.forEach(function (card) {
                const text = card.textContent.toLowerCase();
                if (text.includes(query)) {
                    card.style.display = "";
                    visibleCount++;
                } else {
                    card.style.display = "none";
                }
            });

            if (noMatchBox) {
                noMatchBox.style.display = (cards.length > 0 && visibleCount === 0) ? "block" : "none";
            }
        });
    });

    // 4. Instant Table Search & Filtering (Admin Products, Orders, History)
    const tableSearchInputs = document.querySelectorAll("[data-search-target]");

    tableSearchInputs.forEach(function (input) {
        const targetTableId = input.getAttribute("data-search-target");
        const table = document.getElementById(targetTableId);
        if (!table) return;

        const tbody = table.querySelector("tbody");
        const noMatchRow = table.querySelector(".no-search-results");

        input.addEventListener("input", function () {
            const query = input.value.toLowerCase().trim();
            const rows = tbody.querySelectorAll("tr.data-row");
            let visibleCount = 0;

            rows.forEach(function (row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(query)) {
                    row.style.display = "";
                    visibleCount++;
                } else {
                    row.style.display = "none";
                }
            });

            if (noMatchRow) {
                noMatchRow.style.display = (rows.length > 0 && visibleCount === 0) ? "" : "none";
            }
        });
    });

    // 5. Quantity Input Stock Cap Enforcement
    const qtyInputs = document.querySelectorAll(".qty-input-small");
    qtyInputs.forEach(function (qtyInput) {
        qtyInput.addEventListener("change", function () {
            const maxStock = parseInt(qtyInput.getAttribute("max"), 10);
            const minQty = parseInt(qtyInput.getAttribute("min") || "1", 10);
            let val = parseInt(qtyInput.value, 10);

            if (isNaN(val) || val < minQty) {
                qtyInput.value = minQty;
            } else if (!isNaN(maxStock) && val > maxStock) {
                qtyInput.value = maxStock;
            }
        });
    });

    // 6. Responsive Mobile Sidebar Toggle
    const mobileMenuBtn = document.getElementById("mobile-menu-btn");
    const sidebar = document.getElementById("sidebar");

    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener("click", function () {
            sidebar.classList.toggle("open");
        });
    }

    // 7. Dismissible Alert Notifications
    const closeButtons = document.querySelectorAll(".alert-close-btn");
    closeButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            const alertBox = btn.closest(".alert-banner, .success, .error");
            if (alertBox) {
                alertBox.style.display = "none";
            }
        });
    });
});
