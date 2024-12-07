// Lấy các phần tử
const profileCircle = document.getElementById('profile-circle');
const dropdownMenu = document.getElementById('dropdown-menu');

// Hàm toggle hiển thị dropdown
profileCircle.addEventListener('click', () => {
    dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
    // Gửi yêu cầu tới Flask để ghi nhận sự kiện
    fetch('/handle_click', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ clicked_item: 'profile' })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message); // Kiểm tra phản hồi trong console
    })
    .catch(error => console.error('Error:', error));
});


// Lắng nghe sự kiện nhấn
document.getElementById('language-dropdown').addEventListener('click', () => sendClickEvent('language'));
document.getElementById('notification-icon').addEventListener('click', () => sendClickEvent('notification'));
document.getElementById('profile-circle').addEventListener('click', () => sendClickEvent('profile'));



// Hàm toggle hiển thị dropdown
profileCircle.addEventListener('click', () => {
    dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
});

document.getElementById('login').addEventListener('click', () => {
    fetch('/login', { method: 'POST' })
        .then(response => response.json())
        .then(data => alert(data.message))
        .catch(error => console.error('Error:', error));
});

document.getElementById('logout').addEventListener('click', () => {
    fetch('/logout', { method: 'POST' })
        .then(response => response.json())
        .then(data => alert(data.message))
        .catch(error => console.error('Error:', error));
});

// Ẩn dropdown nếu click bên ngoài
window.addEventListener('click', (event) => {
    if (!profileCircle.contains(event.target) && !dropdownMenu.contains(event.target)) {
        dropdownMenu.style.display = 'none';
    }
});

