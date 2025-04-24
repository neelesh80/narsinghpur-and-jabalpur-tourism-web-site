// API base URL
const API_BASE_URL = 'http://localhost:5000/api';

// Booking form submission
document.querySelector('#booking form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        service: document.querySelector('#service').value,
        destination: document.querySelector('#destination').value,
        date: document.querySelector('#date').value,
        name: document.querySelector('#name').value,
        email: document.querySelector('#email').value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/book`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Booking successful!');
            e.target.reset();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert('Error submitting booking. Please try again.');
    }
});

// Contact form submission
document.querySelector('#contact form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        name: e.target.querySelector('input[placeholder="Your Name"]').value,
        email: e.target.querySelector('input[placeholder="Your Email"]').value,
        message: e.target.querySelector('textarea').value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/contact`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Message sent successfully!');
            e.target.reset();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert('Error sending message. Please try again.');
    }
});

// Language toggle functionality
document.getElementById('toggle-language').addEventListener('click', function() {
    const currentLang = this.textContent;
    if (currentLang === 'EN | हिंदी') {
        this.textContent = 'हिंदी | EN';
        // Add Hindi translation logic here
    } else {
        this.textContent = 'EN | हिंदी';
        // Add English translation logic here
    }
});