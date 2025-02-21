document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (file) {
        const allowedExtensions = ['pdf', 'txt', 'docx'];
        const fileExtension = file.name.split('.').pop().toLowerCase();
        if (allowedExtensions.includes(fileExtension)) {
            document.getElementById('uploadMessage').textContent = 'File uploaded successfully!';
            document.getElementById('uploadMessage').classList.remove('text-red-500');
            document.getElementById('uploadMessage').classList.add('text-green-500');
            
            // Send file to backend
            const formData = new FormData();
            formData.append('file', file);
            fetch('http://127.0.0.1:5000/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log('File upload response:', data);
            })
            .catch(error => {
                console.error('Error uploading file:', error);
            });
        } else {
            document.getElementById('uploadMessage').textContent = 'Invalid file type. Please upload a PDF, TXT, or DOCX file.';
            document.getElementById('uploadMessage').classList.remove('text-green-500');
            document.getElementById('uploadMessage').classList.add('text-red-500');
        }
    } else {
        document.getElementById('uploadMessage').textContent = 'No file selected. Please choose a file to upload.';
        document.getElementById('uploadMessage').classList.remove('text-green-500');
        document.getElementById('uploadMessage').classList.add('text-red-500');
    }
});

document.getElementById('queryForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const queryInput = document.getElementById('queryInput').value;
    if (queryInput) {
        const queryOutput = document.getElementById('responseContainer');
        queryOutput.textContent = '';
        
        // Send query to backend
        fetch('http://127.0.0.1:5000/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: queryInput })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Query response:', data);
            // $('#responseContainer').html(`<h2>${data.Response}</h2>`)
            // const apiResponseElement= document.querySelector('#responseContainer');
            // apiResponseElement.innerHTML = `<h2>${data.Response}</h2>`
            let i = 0;
            const typingEffect = setInterval(() => {
                if (i < data.Response.length) {
                    queryOutput.textContent += data.Response.charAt(i);
                    i++;
                } else {
                    clearInterval(typingEffect);
                }
            }, 100);
        })
        .catch(error => {
            console.error('Error sending query:', error);
        });
    }
});

function logout() {
    window.location.href = '/';
}