        // Get player ID from URL
        const playerId = window.location.pathname.split('/').pop();
        let playerData = null;

        async function loadPlayerData() {
            try {
                const response = await fetch(`/api/players/${playerId}`);
                if (response.ok) {
                    playerData = await response.json();
                    displayPlayerData();
                } else {
                    showError();
                }
            } catch (error) {
                console.error('Error loading player data:', error);
                showError();
            }
        }

        function displayPlayerData() {
            // Hide loading, show dashboard
            document.getElementById('loading').style.display = 'none';
            document.getElementById('dashboard').style.display = 'grid';

            // Header
            document.getElementById('characterName').textContent = playerData.name;
            document.getElementById('characterTitle').textContent = playerData.title || 'Aucun titre';

            // Health
            document.getElementById('hpValue').textContent = `${playerData.current_hp}/${playerData.max_hp}`;
            document.getElementById('staminaValue').textContent = `${playerData.current_stam}/${playerData.max_stam}`;

            const hpPercent = (playerData.current_hp / playerData.max_hp) * 100;
            const staminaPercent = (playerData.current_stam / playerData.max_stam) * 100;
            document.getElementById('hpFill').style.width = `${hpPercent}%`;
            document.getElementById('staminaFill').style.width = `${staminaPercent}%`;

            // Character Info
            document.getElementById('age').textContent = playerData.age;
            document.getElementById('biology').textContent = playerData.biology;
            document.getElementById('feeling').textContent = playerData.general_feeling;
            document.getElementById('temperature').textContent = playerData.temperature || 'Normale';
            document.getElementById('saturation').textContent = playerData.saturation;
            document.getElementById('powerName').textContent = playerData.skill_name || 'Aucun';

            // Skill
            document.getElementById('skillName').textContent = playerData.skill_name || 'Aucun Pouvoir';
            document.getElementById('skillDescription').textContent = playerData.skill_description || 'Aucune description disponible.';

            // Set last dice result
            const lastRoll = getLastRollValue();
            if (lastRoll !== 'Aucun') {
                document.getElementById('diceResult').textContent = lastRoll;
            }
        }

        function getLastRollValue() {
            const rolls = [
                playerData.last_d5_roll,
                playerData.last_d10_roll,
                playerData.last_d20_roll,
                playerData.last_d100_roll
            ].filter(roll => roll !== null);

            return rolls.length > 0 ? rolls[rolls.length - 1] : 'Aucun';
        }

        function showError() {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('error').style.display = 'flex';
        }

        async function rollDice() {
            const diceType = document.getElementById('diceType').value;
            const diceKey = `d${diceType}`;

            try {
                const response = await fetch(`/api/players/${playerId}/roll/${diceKey}`, {
                    method: 'POST'
                });

                if (response.ok) {
                    const result = await response.json();
                    document.getElementById('diceResult').textContent = result.result;

                    // Update the player data
                    playerData[`last_${diceKey}_roll`] = result.result;
                } else {
                    console.error('Error rolling dice:', response.statusText);
                }
            } catch (error) {
                console.error('Error rolling dice:', error);
            }
        }

        function openPlayerDetails() {
            if (playerData) {
                populatePlayerDetails();
                document.getElementById('playerDetailsModal').style.display = 'block';
            }
        }

        function closePlayerDetails() {
            document.getElementById('playerDetailsModal').style.display = 'none';
        }

        function populatePlayerDetails() {
            // Basic Information
            document.getElementById('detailName').textContent = playerData.name || 'Non défini';
            document.getElementById('detailTitle').textContent = playerData.title || 'Aucun titre';
            document.getElementById('detailAge').textContent = playerData.age || 'Non défini';
            document.getElementById('detailGender').textContent = playerData.gender || 'Non défini';
            document.getElementById('detailBiology').textContent = playerData.biology || 'Non défini';
            document.getElementById('detailBackground').textContent = playerData.starter_background || 'Non défini';
            document.getElementById('detailMainStyle').textContent = playerData.main_style || 'Non défini';

            // Health & Status
            document.getElementById('detailHp').textContent = `${playerData.current_hp || 0}/${playerData.max_hp || 0}`;
            document.getElementById('detailStamina').textContent = `${playerData.current_stam || 0}/${playerData.max_stam || 0}`;
            document.getElementById('detailFeeling').textContent = playerData.general_feeling || 'Non défini';
            document.getElementById('detailTemperature').textContent = playerData.temperature || 'Non défini';
            document.getElementById('detailSaturation').textContent = playerData.saturation || 'Non défini';

            // Character Traits
            document.getElementById('detailSin').textContent = playerData.sin || 'Non défini';
            document.getElementById('detailVirtue').textContent = playerData.virtue || 'Non défini';

            // Dice Rolls
            document.getElementById('detailD5').textContent = playerData.last_d5_roll || 'Aucun';
            document.getElementById('detailD10').textContent = playerData.last_d10_roll || 'Aucun';
            document.getElementById('detailD20').textContent = playerData.last_d20_roll || 'Aucun';
            document.getElementById('detailD100').textContent = playerData.last_d100_roll || 'Aucun';

            // Skills
            document.getElementById('detailSkillName').textContent = playerData.skill_name || 'Aucun';
            document.getElementById('detailSkillDescription').textContent = playerData.skill_description || 'Aucune description disponible.';
            document.getElementById('detailPassiveName').textContent = playerData.passive_name || 'Aucun';
            document.getElementById('detailPassiveDescription').textContent = playerData.passive_description || 'Aucune description disponible.';
        }

        function savePlayerData() {
            // TODO: Implement save functionality
            console.log('Saving player data...');
            alert('Données sauvegardées! (TODO: Implémenter la fonctionnalité)');
        }

        function openAbilityCreator() {
            // TODO: Open popup to create new abilities
            console.log('Opening ability creator popup');
        }

        function sendMessage() {
            const message = document.getElementById('chatInput').value.trim();
            const voiceMode = document.getElementById('voiceMode').value;

            if (message) {
                // TODO: Implement message sending via WebSocket
                console.log('Sending message:', message, 'Voice mode:', voiceMode);

                // Add message to display (temporary local display)
                const chatMessages = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message';
                messageDiv.innerHTML = `<strong>Vous:</strong> ${message}`;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;

                document.getElementById('chatInput').value = '';
            }
        }

        // Allow Enter to send message (Shift+Enter for new line)
        document.getElementById('chatInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('playerDetailsModal');
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }

        // Load player data when page loads
        loadPlayerData();