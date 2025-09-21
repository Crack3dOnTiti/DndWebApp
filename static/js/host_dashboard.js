        let currentPlayerId = null;
        let players = [];
        let enemies = [];

        // Slider value mappings
        const sliderValues = {
            saturation: ['Full', 'Fine', 'Peckish', 'Hungry', 'Starving'],
            feeling: ['Terrible', 'Bad', 'Good', 'Great', 'Excellent'],
            temperature: ['Freezing', 'Cold', 'Normal', 'Warm', 'Hot']
        };

        // Load initial data
        async function loadPlayers() {
            try {
                const response = await fetch('/api/players');
                players = await response.json();
                updatePlayersList();
                updatePlayerCheckboxes();
            } catch (error) {
                console.error('Error loading players:', error);
            }
        }

        async function loadEnemies() {
            try {
                const response = await fetch('/api/enemies');
                enemies = await response.json();
                updateEnemiesList();
            } catch (error) {
                console.error('Error loading enemies:', error);
            }
        }

        function updatePlayersList() {
            const playersList = document.getElementById('playersList');
            playersList.innerHTML = '';

            players.forEach(player => {
                const lastRoll = getLastRollValue(player);
                const card = document.createElement('div');
                card.className = 'character-card';
                card.onclick = () => openPlayerModal(player);
                card.innerHTML = `
                    <div class="character-header">
                        <span class="character-name">${player.name}</span>
                        <span class="character-id">ID: ${player.id}</span>
                    </div>
                    <div class="character-stats">HP: ${player.current_hp}/${player.max_hp} | Stamina: ${player.current_stam}/${player.max_stam}</div>
                    <div class="character-roll">Last Roll: ${lastRoll}</div>
                `;
                playersList.appendChild(card);
            });
        }

        function updateEnemiesList() {
            const enemiesList = document.getElementById('enemiesList');
            enemiesList.innerHTML = '';

            enemies.forEach(enemy => {
                const lastRoll = getLastRollValue(enemy);
                const card = document.createElement('div');
                card.className = 'character-card';
                card.onclick = () => openEnemyModal(enemy);
                card.innerHTML = `
                    <div class="character-header">
                        <span class="character-name">${enemy.name}</span>
                        <span class="character-id">ID: ${enemy.id}</span>
                    </div>
                    <div class="character-stats">HP: ${enemy.current_hp}/${enemy.max_hp} | Stamina: ${enemy.current_stam}/${enemy.max_stam}</div>
                    <div class="character-roll">Last Roll: ${lastRoll}</div>
                `;
                enemiesList.appendChild(card);
            });
        }

        function updatePlayerCheckboxes() {
            const container = document.getElementById('playerCheckboxes');
            container.innerHTML = '';

            players.forEach(player => {
                const checkboxItem = document.createElement('div');
                checkboxItem.className = 'checkbox-item';
                checkboxItem.innerHTML = `
                    <input type="checkbox" id="player-${player.id}" value="${player.id}">
                    <label for="player-${player.id}">${player.name}</label>
                `;
                container.appendChild(checkboxItem);
            });
        }

        function getLastRollValue(character) {
            const rolls = [
                character.last_d5_roll,
                character.last_d10_roll,
                character.last_d20_roll,
                character.last_d100_roll
            ].filter(roll => roll !== null);

            return rolls.length > 0 ? rolls[rolls.length - 1] : 'None';
        }

        function openPlayerModal(player) {
            currentPlayerId = player.id;
            document.getElementById('modalTitle').textContent = `Edit ${player.name}`;
            document.getElementById('editName').value = player.name;
            document.getElementById('editCurrentHP').value = player.current_hp;
            document.getElementById('editMaxHP').value = player.max_hp;
            document.getElementById('editCurrentStam').value = player.current_stam;
            document.getElementById('editMaxStam').value = player.max_stam;
            document.getElementById('editSkillDesc').value = player.skill_description || '';

            document.getElementById('playerModal').style.display = 'block';
        }

        function openEnemyModal(enemy) {
            // TODO: Implement enemy editing modal
            console.log('Edit enemy:', enemy);
        }

        async function savePlayerChanges() {
            const data = {
                name: document.getElementById('editName').value,
                current_hp: parseFloat(document.getElementById('editCurrentHP').value),
                max_hp: parseFloat(document.getElementById('editMaxHP').value),
                current_stam: parseFloat(document.getElementById('editCurrentStam').value),
                max_stam: parseFloat(document.getElementById('editMaxStam').value),
                skill_description: document.getElementById('editSkillDesc').value
            };

            try {
                const response = await fetch(`/api/players/${currentPlayerId}/host-update`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    document.getElementById('playerModal').style.display = 'none';
                    loadPlayers(); // Refresh the list
                }
            } catch (error) {
                console.error('Error saving player:', error);
            }
        }

        function openCombatManager() {
            document.getElementById('combatModal').style.display = 'block';
            updateCombatLists();
        }

        function closeCombatManager() {
            document.getElementById('combatModal').style.display = 'none';
        }

        function updateCombatLists() {
            updateCombatPlayersList();
            updateCombatEnemiesList();
        }

        function updateCombatPlayersList() {
            const combatPlayersList = document.getElementById('combatPlayersList');
            combatPlayersList.innerHTML = '';

            players.forEach(player => {
                const card = document.createElement('div');
                card.style.cssText = `
                    background: #2a2a2a;
                    padding: 12px;
                    margin-bottom: 10px;
                    border-radius: 6px;
                    border: 1px solid #444;
                `;
                card.innerHTML = `
                    <div style="font-weight: 600; margin-bottom: 8px; color: #e0e0e0;">
                        ${player.name} <span style="color: #aaa; font-size: 0.9rem;">ID: ${player.id}</span>
                    </div>

                    <div style="margin-bottom: 8px;">
                        <label style="display: block; font-size: 0.8rem; color: #aaa; margin-bottom: 3px;">
                            HP: <span id="combatPlayerHP-${player.id}">${player.current_hp}</span>/${player.max_hp}
                        </label>
                        <input type="range"
                               min="0"
                               max="${player.max_hp}"
                               value="${player.current_hp}"
                               style="width: 100%; height: 4px; background: #555; border-radius: 2px;"
                               oninput="updateCombatPlayerHP(${player.id}, this.value)">
                    </div>

                    <div>
                        <label style="display: block; font-size: 0.8rem; color: #aaa; margin-bottom: 3px;">
                            Stamina: <span id="combatPlayerStam-${player.id}">${player.current_stam}</span>/${player.max_stam}
                        </label>
                        <input type="range"
                               min="0"
                               max="${player.max_stam}"
                               value="${player.current_stam}"
                               style="width: 100%; height: 4px; background: #555; border-radius: 2px;"
                               oninput="updateCombatPlayerStam(${player.id}, this.value)">
                    </div>
                `;
                combatPlayersList.appendChild(card);
            });
        }

        function updateCombatEnemiesList() {
            const combatEnemiesList = document.getElementById('combatEnemiesList');
            combatEnemiesList.innerHTML = '';

            enemies.forEach(enemy => {
                const card = document.createElement('div');
                card.style.cssText = `
                    background: #2a2a2a;
                    padding: 12px;
                    margin-bottom: 10px;
                    border-radius: 6px;
                    border: 1px solid #444;
                `;
                card.innerHTML = `
                    <div style="font-weight: 600; margin-bottom: 8px; color: #e0e0e0;">
                        ${enemy.name} <span style="color: #aaa; font-size: 0.9rem;">ID: ${enemy.id}</span>
                    </div>

                    <div style="margin-bottom: 8px;">
                        <label style="display: block; font-size: 0.8rem; color: #aaa; margin-bottom: 3px;">
                            HP: <span id="combatEnemyHP-${enemy.id}">${enemy.current_hp}</span>/${enemy.max_hp}
                        </label>
                        <input type="range"
                               min="0"
                               max="${enemy.max_hp}"
                               value="${enemy.current_hp}"
                               style="width: 100%; height: 4px; background: #555; border-radius: 2px;"
                               oninput="updateCombatEnemyHP(${enemy.id}, this.value)">
                    </div>

                    <div>
                        <label style="display: block; font-size: 0.8rem; color: #aaa; margin-bottom: 3px;">
                            Stamina: <span id="combatEnemyStam-${enemy.id}">${enemy.current_stam}</span>/${enemy.max_stam}
                        </label>
                        <input type="range"
                               min="0"
                               max="${enemy.max_stam}"
                               value="${enemy.current_stam}"
                               style="width: 100%; height: 4px; background: #555; border-radius: 2px;"
                               oninput="updateCombatEnemyStam(${enemy.id}, this.value)">
                    </div>
                `;
                combatEnemiesList.appendChild(card);
            });
        }

        function updateCombatPlayerHP(playerId, value) {
            document.getElementById(`combatPlayerHP-${playerId}`).textContent = value;
            // TODO: Update player HP in backend
            const player = players.find(p => p.id === playerId);
            if (player) {
                player.current_hp = parseFloat(value);
            }
        }

        function updateCombatPlayerStam(playerId, value) {
            document.getElementById(`combatPlayerStam-${playerId}`).textContent = value;
            // TODO: Update player stamina in backend
            const player = players.find(p => p.id === playerId);
            if (player) {
                player.current_stam = parseFloat(value);
            }
        }

        function updateCombatEnemyHP(enemyId, value) {
            document.getElementById(`combatEnemyHP-${enemyId}`).textContent = value;
            // TODO: Update enemy HP in backend
            const enemy = enemies.find(e => e.id === enemyId);
            if (enemy) {
                enemy.current_hp = parseFloat(value);
            }
        }

        function updateCombatEnemyStam(enemyId, value) {
            document.getElementById(`combatEnemyStam-${enemyId}`).textContent = value;
            // TODO: Update enemy stamina in backend
            const enemy = enemies.find(e => e.id === enemyId);
            if (enemy) {
                enemy.current_stam = parseFloat(value);
            }
        }

        function rollCombatDice() {
            const diceType = parseInt(document.getElementById('combatDiceType').value);
            const result = Math.floor(Math.random() * diceType) + 1;
            document.getElementById('combatDiceResult').textContent = result;
        }

        function updateSliderValue(type, value) {
            const displayValue = sliderValues[type][value];
            document.getElementById(`${type}Value`).textContent = displayValue;
        }

        function rollHostDice() {
            const diceType = parseInt(document.getElementById('hostDiceType').value);
            const result = Math.floor(Math.random() * diceType) + 1;
            document.getElementById('hostDiceResult').textContent = result;
        }

        function sendMessage() {
            const message = document.getElementById('chatInputBottom').value;
            const selectedPlayers = Array.from(document.querySelectorAll('#playerCheckboxes input:checked'))
                .map(cb => cb.value);

            if (message && selectedPlayers.length > 0) {
                // TODO: Implement message sending via WebSocket
                console.log('Sending message:', message, 'to players:', selectedPlayers);

                // Add message to display
                const messageDisplay = document.getElementById('messageDisplay');
                const messageDiv = document.createElement('div');
                messageDiv.style.marginBottom = '5px';
                messageDiv.style.fontSize = '0.8rem';
                messageDiv.innerHTML = `<strong>Host:</strong> ${message}`;
                messageDisplay.appendChild(messageDiv);
                messageDisplay.scrollTop = messageDisplay.scrollHeight;

                document.getElementById('chatInputBottom').value = '';
            }
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            const playerModal = document.getElementById('playerModal');
            const combatModal = document.getElementById('combatModal');
            if (event.target == playerModal) {
                playerModal.style.display = 'none';
            } else if (event.target == combatModal) {
                combatModal.style.display = 'none';
            }
        }

        // Load data on page load
        loadPlayers();
        loadEnemies();