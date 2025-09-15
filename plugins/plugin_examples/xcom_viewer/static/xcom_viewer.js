// 📦 XCom Viewer JavaScript
class XComViewer {
    constructor() {
        this.xcomData = null;
        this.expandedEntries = new Set();
        this.init();
    }
    
    async init() {
        try {
            await this.loadXComData();
            this.renderTaskInfo();
            this.renderXComStats();
            this.renderXComEntries();
            this.showContent();
        } catch (error) {
            console.error('Failed to initialize XCom viewer:', error);
            this.showError(error.message);
        }
    }
    
    async loadXComData() {
        const apiUrl = `/xcom-viewer/api/xcom/${DAG_ID}/${encodeURIComponent(RUN_ID)}/${TASK_ID}/${MAP_INDEX}`;
        
        try {
            const response = await fetch(apiUrl);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.xcomData = await response.json();
            console.log('XCom data loaded:', this.xcomData);
            
        } catch (error) {
            console.error('Failed to load XCom data:', error);
            throw error;
        }
    }
    
    renderTaskInfo() {
        const taskInfo = this.xcomData.task_info;
        const container = document.getElementById('taskInstanceInfo');
        
        const mapIndexDisplay = taskInfo.map_index === "-1" ? "Non-mapped Task" : `Map Index ${taskInfo.map_index}`;
        
        const items = [
            { label: 'DAG ID', value: taskInfo.dag_id },
            { label: 'Task ID', value: taskInfo.task_id },
            { label: 'Run ID', value: taskInfo.run_id },
            { label: 'Map Index', value: mapIndexDisplay },
            { label: 'State', value: taskInfo.state || 'Unknown' },
            { label: 'Operator', value: taskInfo.operator || 'Unknown' },
            { label: 'Start Date', value: this.formatDate(taskInfo.start_date) },
            { label: 'End Date', value: this.formatDate(taskInfo.end_date) }
        ];
        
        container.innerHTML = items.map(item => `
            <div class="info-item">
                <div class="info-label">${item.label}</div>
                <div class="info-value">${this.escapeHtml(item.value)}</div>
            </div>
        `).join('');
    }
    
    renderXComStats() {
        const xcomEntries = this.xcomData.xcom_entries;
        const container = document.getElementById('xcomStats');
        
        // Calculate statistics
        const totalEntries = xcomEntries.length;
        const typeCounts = {};
        let totalSize = 0;
        
        xcomEntries.forEach(entry => {
            const type = entry.value_type;
            typeCounts[type] = (typeCounts[type] || 0) + 1;
            totalSize += entry.value_size || 0;
        });
        
        const mostCommonType = Object.keys(typeCounts).reduce((a, b) => 
            typeCounts[a] > typeCounts[b] ? a : b, 'none'
        );
        
        const stats = [
            { label: 'Total Entries', value: totalEntries },
            { label: 'Total Data Size', value: this.formatBytes(totalSize) },
            { label: 'Most Common Type', value: mostCommonType },
            { label: 'Unique Keys', value: new Set(xcomEntries.map(e => e.key)).size },
            { label: 'Last Updated', value: this.formatDate(this.xcomData.timestamp) }
        ];
        
        container.innerHTML = stats.map(stat => `
            <div class="stat-item">
                <div class="stat-label">${stat.label}</div>
                <div class="stat-value">${this.escapeHtml(stat.value)}</div>
            </div>
        `).join('');
    }
    
    renderXComEntries() {
        const xcomEntries = this.xcomData.xcom_entries;
        const container = document.getElementById('xcomsList');
        const noXComsMessage = document.getElementById('noXComsMessage');
        
        if (xcomEntries.length === 0) {
            container.style.display = 'none';
            noXComsMessage.style.display = 'block';
            return;
        }
        
        container.innerHTML = xcomEntries.map((entry, index) => `
            <div class="xcom-entry" id="xcom-entry-${index}">
                <div class="xcom-header-entry" onclick="toggleXComEntry(${index})">
                    <div class="xcom-key-info">
                        <div class="xcom-key">${this.escapeHtml(entry.key)}</div>
                        <div class="xcom-type-badge ${entry.value_type}">${entry.value_type}</div>
                    </div>
                    <div class="xcom-meta">
                        <div class="xcom-size">${this.formatBytes(entry.value_size)}</div>
                        <div class="xcom-timestamp">${this.formatDate(entry.timestamp)}</div>
                        <div class="xcom-expand-icon">▶</div>
                    </div>
                </div>
                <div class="xcom-content-entry">
                    <div class="xcom-value-container">
                        <div class="xcom-value">
                            <pre><code class="language-json">${this.formatXComValue(entry.value, entry.value_type)}</code></pre>
                        </div>
                        <div class="xcom-metadata">
                            <div class="meta-item">
                                <span class="meta-label">Key:</span> ${this.escapeHtml(entry.key)}
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Type:</span> ${this.escapeHtml(entry.value_type)}
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Size:</span> ${this.formatBytes(entry.value_size)}
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Timestamp:</span> ${this.formatDate(entry.timestamp)}
                            </div>
                            ${entry.map_index >= 0 ? `
                                <div class="meta-item">
                                    <span class="meta-label">Map Index:</span> ${entry.map_index}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Apply syntax highlighting
        setTimeout(() => {
            if (window.Prism) {
                Prism.highlightAll();
            }
        }, 100);
    }
    
    toggleXComEntry(index) {
        const entry = document.getElementById(`xcom-entry-${index}`);
        const isExpanded = entry.classList.contains('expanded');
        
        if (isExpanded) {
            entry.classList.remove('expanded');
            this.expandedEntries.delete(index);
        } else {
            entry.classList.add('expanded');
            this.expandedEntries.add(index);
            
            // Re-run syntax highlighting for the newly visible code
            setTimeout(() => {
                if (window.Prism) {
                    const codeBlocks = entry.querySelectorAll('code[class*="language-"]');
                    codeBlocks.forEach(block => Prism.highlightElement(block));
                }
            }, 50);
        }
    }
    
    expandAllXComs() {
        const entries = document.querySelectorAll('.xcom-entry');
        entries.forEach((entry, index) => {
            entry.classList.add('expanded');
            this.expandedEntries.add(index);
        });
        
        // Re-run syntax highlighting
        setTimeout(() => {
            if (window.Prism) {
                Prism.highlightAll();
            }
        }, 100);
    }
    
    collapseAllXComs() {
        const entries = document.querySelectorAll('.xcom-entry');
        entries.forEach((entry, index) => {
            entry.classList.remove('expanded');
            this.expandedEntries.delete(index);
        });
    }
    
    formatXComValue(value, type) {
        if (value === null || value === undefined) {
            return 'null';
        }
        
        try {
            if (type === 'string') {
                return JSON.stringify(value, null, 2);
            } else if (typeof value === 'object') {
                return JSON.stringify(value, null, 2);
            } else {
                return JSON.stringify(value, null, 2);
            }
        } catch (error) {
            return String(value);
        }
    }
    
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) return dateString;
            
            return date.toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        } catch (error) {
            return dateString;
        }
    }
    
    formatBytes(bytes) {
        if (bytes === 0 || !bytes) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showContent() {
        document.getElementById('loadingContainer').style.display = 'none';
        document.getElementById('errorContainer').style.display = 'none';
        document.getElementById('xcomContent').style.display = 'block';
    }
    
    showError(message) {
        document.getElementById('loadingContainer').style.display = 'none';
        document.getElementById('xcomContent').style.display = 'none';
        document.getElementById('errorMessage').textContent = message;
        document.getElementById('errorContainer').style.display = 'block';
    }
    
    async refreshData() {
        // Show loading state
        document.getElementById('xcomContent').style.display = 'none';
        document.getElementById('errorContainer').style.display = 'none';
        document.getElementById('loadingContainer').style.display = 'block';
        
        // Disable refresh button
        const refreshButton = document.getElementById('refreshButton');
        refreshButton.disabled = true;
        refreshButton.textContent = '🔄 Refreshing...';
        
        try {
            await this.loadXComData();
            this.renderTaskInfo();
            this.renderXComStats();
            this.renderXComEntries();
            this.showContent();
        } catch (error) {
            console.error('Failed to refresh XCom data:', error);
            this.showError(error.message);
        } finally {
            // Re-enable refresh button
            refreshButton.disabled = false;
            refreshButton.textContent = '🔄 Refresh';
        }
    }
    
    exportData() {
        if (!this.xcomData) {
            alert('No data to export');
            return;
        }
        
        const exportData = {
            task_info: this.xcomData.task_info,
            xcom_entries: this.xcomData.xcom_entries,
            export_timestamp: new Date().toISOString(),
            export_metadata: {
                dag_id: DAG_ID,
                run_id: RUN_ID,
                task_id: TASK_ID,
                map_index: MAP_INDEX
            }
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `xcom_${DAG_ID}_${TASK_ID}_${RUN_ID}.json`;
        link.click();
        
        URL.revokeObjectURL(link.href);
    }
}

// Global functions for button handlers
let xcomViewer;

function toggleXComEntry(index) {
    if (xcomViewer) {
        xcomViewer.toggleXComEntry(index);
    }
}

function expandAllXComs() {
    if (xcomViewer) {
        xcomViewer.expandAllXComs();
    }
}

function collapseAllXComs() {
    if (xcomViewer) {
        xcomViewer.collapseAllXComs();
    }
}

function refreshXComData() {
    if (xcomViewer) {
        xcomViewer.refreshData();
    }
}

function exportXComData() {
    if (xcomViewer) {
        xcomViewer.exportData();
    }
}

// Initialize XCom viewer when page loads
document.addEventListener('DOMContentLoaded', () => {
    xcomViewer = new XComViewer();
});
