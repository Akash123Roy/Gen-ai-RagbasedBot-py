document.getElementById('loginForm').addEventListener('submit', function(event) {
            event.preventDefault();
            
            const predefinedUsername = 'admin';
            const predefinedPassword = 'password123';
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            if (username === predefinedUsername && password === predefinedPassword) {
                document.getElementById('message').textContent = 'Login successful!';
                document.getElementById('message').classList.remove('text-red-500');
                document.getElementById('message').classList.add('text-green-500');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            } else {
                document.getElementById('message').textContent = 'Invalid username or password.';
                document.getElementById('message').classList.remove('text-green-500');
                document.getElementById('message').classList.add('text-red-500');
            }
        });