        // Host form handling
        document.getElementById('hostForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const hostName = formData.get('hostName');
            const hostPassword = formData.get('hostPassword');

            try {
                const response = await fetch('/host-login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: hostName, password: hostPassword })
                });

                if (response.ok) {
                    window.location.href = '/host-dashboard';
                } else {
                    showError('hostError', 'Invalid credentials');
                }
            } catch (error) {
                showError('hostError', 'Connection error');
            }
        });

        // Create new player button
        document.getElementById('createPlayerBtn').addEventListener('click', () => {
            window.location.href = '/character-creation';
        });

        // File upload handling
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            handleFile(e.dataTransfer.files[0]);
        });

        fileInput.addEventListener('change', (e) => {
            handleFile(e.target.files[0]);
        });

        async function handleFile(file) {
            if (!file) return;

            if (!file.name.endsWith('.json')) {
                showError('uploadError', 'Please select a valid JSON file');
                return;
            }

            try {
                const text = await file.text();
                const characterData = JSON.parse(text);

                // TODO: Validate character data structure and upload to API
                console.log('Character data:', characterData);
                showSuccess('uploadSuccess', `Character "${characterData.name || 'Unknown'}" loaded successfully`);

            } catch (error) {
                showError('uploadError', 'Invalid JSON file format');
            }
        }

        function showError(elementId, message) {
            const element = document.getElementById(elementId);
            element.textContent = message;
            element.classList.remove('hidden');
            setTimeout(() => element.classList.add('hidden'), 5000);
        }

        function showSuccess(elementId, message) {
            const element = document.getElementById(elementId);
            element.textContent = message;
            element.classList.remove('hidden');
            setTimeout(() => element.classList.add('hidden'), 5000);
        }