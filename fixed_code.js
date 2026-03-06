// Handle project selection from URL parameter
    const projectFromUrl = getProjectFromUrl();
    if (projectFromUrl) {
        document.getElementById('current-server').textContent = 'Loading...';
        loadServers().then(() => {
            const select = document.getElementById('project-select');
            if (select) {
                const options = Array.from(select.options);
                const found = options.find(opt => opt.text.includes(projectFromUrl) || opt.value.includes(projectFromUrl));
                if (found) {
                    select.value = found.value;
                    selectProjectFromDropdown();
                } else {
                    fetch('/api/servers')
                        .then(r => r.json())
                        .then(servers => {
                            const server = servers.find(s => s.project === projectFromUrl);
                            if (server) {
                                selectServer(server.cccip, server.ccc_dispatch_port, server.project);
                            } else {
                                alert('Project not found: ' + projectFromUrl);
                            }
                        });
                }
            } else {
                // Element not found, fallback to direct server selection
                fetch('/api/servers')
                    .then(r => r.json())
                    .then(servers => {
                        const server = servers.find(s => s.project === projectFromUrl);
                        if (server) {
                            selectServer(server.cccip, server.ccc_dispatch_port, server.project);
                        } else {
                            alert('Project not found: ' + projectFromUrl);
                        }
                    });
            }
        });
        // Update project display with the project from URL
        updateProjectDisplay();
    } else {
        loadServers();
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.querySelector('.tab[data-tab="connect"]').classList.add('active');
        document.getElementById('connect-tab').classList.add('active');
    }