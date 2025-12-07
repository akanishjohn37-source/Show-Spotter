document.addEventListener('DOMContentLoaded', function () {
    const grid = document.getElementById('seat-grid');
    const selectedDisplay = document.getElementById('selected-seats-display');
    const costDisplay = document.getElementById('total-cost-display');
    const input = document.getElementById('selected_seats_input');
    const bookBtn = document.getElementById('book-btn');

    let selectedSeatIds = [];
    let selectedSeatLabels = [];

    // Attach listeners to existing seats
    const seats = grid.querySelectorAll('.seat');
    seats.forEach(seat => {
        if (!seat.classList.contains('booked')) {
            seat.addEventListener('click', () => toggleSeat(seat));
        }
    });

    function toggleSeat(seat) {
        const id = seat.dataset.id;
        const label = seat.dataset.label;

        if (selectedSeatIds.includes(id)) {
            selectedSeatIds = selectedSeatIds.filter(s => s !== id);
            selectedSeatLabels = selectedSeatLabels.filter(l => l !== label);
            seat.classList.remove('selected');
        } else {
            selectedSeatIds.push(id);
            selectedSeatLabels.push(label);
            seat.classList.add('selected');
        }
        updateUI();
    }

    function updateUI() {
        if (selectedSeatIds.length > 0) {
            selectedDisplay.textContent = selectedSeatLabels.join(', ');
            const total = selectedSeatIds.length * ticketPrice;
            costDisplay.textContent = `$${total.toFixed(2)}`;
            input.value = selectedSeatIds.join(',');
            if (bookBtn) bookBtn.disabled = false;
        } else {
            selectedDisplay.textContent = '-';
            costDisplay.textContent = '$0.00';
            input.value = '';
            if (bookBtn) bookBtn.disabled = true;
        }
    }
});
