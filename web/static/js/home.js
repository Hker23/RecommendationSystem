document.addEventListener('DOMContentLoaded', () => {
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

    // document.getElementById('login').addEventListener('click', () => {
    //     fetch('/login', { method: 'POST' })
    //         .then(response => response.json())
    //         .then(data => alert(data.message))
    //         .catch(error => console.error('Error:', error));
    // });

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
    const courseLinks = document.querySelectorAll('.course-card a');

    courseLinks.forEach(link => {
        const courseId = link.getAttribute('data-course-id');
        const courseUrl = link.getAttribute('href');

        link.addEventListener('click', (event) => {
            event.preventDefault(); // Ngăn điều hướng mặc định
            logCourseClick(courseId, courseUrl);
        });
    });

    // Hàm log khi nhấn vào khóa học

    window.logCourseClick = function (course_id, course_url) {
        const username = "{{ session.get('username', '') }}";
        if (!username) {
            console.log("User not logged in. Skipping save to MongoDB.");
            window.open(course_url, "_blank");
            return;
        }

        const payload = {
            course_id: course_id,
            username: username,
            time: new Date().toISOString()
        };

        fetch('/log_course_click', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
            .then(response => {
                console.log("Course click logged successfully.");
                window.open(course_url, "_blank");
            })
            .catch(error => {
                console.error('Error logging course click:', error);
                window.open(course_url, "_blank");
            });
    }
});
