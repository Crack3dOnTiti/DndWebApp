        const form = document.getElementById('characterForm');
        const createBtn = document.getElementById('createBtn');
        const backgroundBtns = document.querySelectorAll('.background-btn');
        const backgroundDescriptions = document.querySelectorAll('.background-description');
        const emptyDescription = document.getElementById('emptyDescription');
        const starterBackgroundInput = document.getElementById('starterBackground');

        // Handle background selection
        backgroundBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove selected class from all buttons
                backgroundBtns.forEach(b => b.classList.remove('selected'));

                // Add selected class to clicked button
                btn.classList.add('selected');

                // Hide empty description and all descriptions
                emptyDescription.style.display = 'none';
                backgroundDescriptions.forEach(desc => desc.classList.remove('active'));

                // Show selected description
                const background = btn.dataset.background;
                document.getElementById(`desc-${background}`).classList.add('active');

                // Set hidden input value
                starterBackgroundInput.value = background;

                // Check form validity
                checkFormValidity();
            });
        });

        // Check form validity on input
        form.addEventListener('input', checkFormValidity);
        form.addEventListener('change', checkFormValidity);

        function checkFormValidity() {
            const requiredFields = form.querySelectorAll('[required]');
            let allFilled = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    allFilled = false;
                }
            });

            if (allFilled) {
                createBtn.classList.add('enabled');
            } else {
                createBtn.classList.remove('enabled');
            }
        }

        // Form submission
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (!createBtn.classList.contains('enabled')) {
                return;
            }

            const formData = new FormData(form);
            const characterData = {
                name: formData.get('name'),
                gender: formData.get('gender'),
                skill_name: formData.get('skillName'),
                skill_description: formData.get('skillDescription'),
                starter_background: formData.get('starterBackground')
            };

            try {
                const response = await fetch('/api/players', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(characterData)
                });

                if (response.ok) {
                    const result = await response.json();
                    // Redirect to player dashboard
                    window.location.href = `/player-dashboard/${result.id}`;
                } else {
                    const error = await response.json();
                    alert('Erreur lors de la création: ' + (error.message || 'Erreur inconnue'));
                }
            } catch (error) {
                alert('Erreur de connexion: ' + error.message);
            }
        });

        // Initial validity check
        checkFormValidity();