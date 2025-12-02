document.addEventListener('DOMContentLoaded', function() {
    const grid = document.getElementById('seat-grid');
    const selectedDisplay = document.getElementById('selected-seats-display');
    const costDisplay = document.getElementById('total-cost-display');
    const input = document.getElementById('selected_seats_input');
    const bookBtn = document.getElementById('book-btn');
    
    let selectedSeats = [];

    // Generate Grid
    for (let r = 1; r <= venueRows; r++) {
        for (let c = 1; c <= venueCols; c++) {
            const seatId = `${String.fromCharCode(64 + r)}${c}`; // A1, A2, B1...
            const seat = document.createElement('div');
            seat.classList.add('seat');
            seat.textContent = seatId;
            seat.dataset.id = seatId;

            if (bookedSeats.includes(seatId)) {
                seat.classList.add('booked');
                seat.title = "Already Booked";
            } else {
                seat.addEventListener('click', () => toggleSeat(seat));
            }

            grid.appendChild(seat);
        }
    }

    function toggleSeat(seat) {
        const id = seat.dataset.id;
        if (selectedSeats.includes(id)) {
            selectedSeats = selectedSeats.filter(s => s !== id);
            seat.classList.remove('selected');
        } else {
            selectedSeats.push(id);
            seat.classList.add('selected');
        }
        updateUI();
    }

    function updateUI() {
        if (selectedSeats.length > 0) {
            selectedDisplay.textContent = selectedSeats.join(', ');
            const total = selectedSeats.length * ticketPrice;
            costDisplay.textContent = `$${total.toFixed(2)}`;
            input.value = selectedSeats.join(',');
            bookBtn.disabled = false;
        } else {
            selectedDisplay.textContent = '-';
            costDisplay.textContent = '$0.00';
            input.value = '';
            bookBtn.disabled = true;
        }
    }
});
