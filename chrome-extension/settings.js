// settings.js - Settings page functionality
document.addEventListener('DOMContentLoaded', async () => {
  const elements = {
    backendUrl: document.getElementById('backendUrl'),
    backendStatus: document.getElementById('backendStatus'),
    autoSummarize: document.getElementById('autoSummarize'),
    summaryLength: document.getElementById('summaryLength'),
    enableNotifications: document.getElementById('enableNotifications'),
    storageInfo: document.getElementById('storageInfo'),
    clearStorageBtn: document.getElementById('clearStorageBtn'),
    saveBtn: document.getElementById('saveBtn'),
    resetBtn: document.getElementById('resetBtn'),
    testBackendBtn: document.getElementById('testBackendBtn'),
    successMessage: document.getElementById('successMessage')
  };

  // Load current settings
  await loadSettings();
  
  // Update storage info
  await updateStorageInfo();
  
  // Test backend status on load
  await testBackendConnection();

  // Event listeners
  elements.saveBtn.addEventListener('click', saveSettings);
  elements.resetBtn.addEventListener('click', resetSettings);
  elements.testBackendBtn.addEventListener('click', testBackendConnection);
  elements.clearStorageBtn.addEventListener('click', clearStorage);
  elements.backendUrl.addEventListener('input', debounce(testBackendConnection, 1000));

  async function loadSettings() {
    try {
      const result = await chrome.storage.local.get('settings');
      const settings = result.settings || getDefaultSettings();

      elements.backendUrl.value = settings.backendUrl;
      elements.autoSummarize.checked = settings.autoSummarize;
      elements.summaryLength.value = settings.summaryLength;
      elements.enableNotifications.checked = settings.enableNotifications;
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  }

  async function saveSettings() {
    try {
      const settings = {
        backendUrl: elements.backendUrl.value.trim(),
        autoSummarize: elements.autoSummarize.checked,
        summaryLength: elements.summaryLength.value,
        enableNotifications: elements.enableNotifications.checked
      };

      await chrome.storage.local.set({ settings });
      showSuccessMessage();
      
      // Test backend after saving
      await testBackendConnection();
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Error saving settings. Please try again.');
    }
  }

  async function resetSettings() {
    if (confirm('Are you sure you want to reset all settings to defaults?')) {
      const defaultSettings = getDefaultSettings();
      
      elements.backendUrl.value = defaultSettings.backendUrl;
      elements.autoSummarize.checked = defaultSettings.autoSummarize;
      elements.summaryLength.value = defaultSettings.summaryLength;
      elements.enableNotifications.checked = defaultSettings.enableNotifications;

      await saveSettings();
    }
  }

  async function testBackendConnection() {
    const url = elements.backendUrl.value.trim();
    
    if (!url) {
      updateBackendStatus('offline', 'No URL specified');
      return;
    }

    updateBackendStatus('testing', 'Testing connection...');

    try {
      const response = await fetch(`${url}/health`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        updateBackendStatus('online', 'Connected successfully');
      } else {
        updateBackendStatus('offline', `HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Backend test error:', error);
      updateBackendStatus('offline', 'Connection failed');
    }
  }

  function updateBackendStatus(status, message) {
    const statusElement = elements.backendStatus;
    
    statusElement.className = 'status-indicator';
    
    switch (status) {
      case 'online':
        statusElement.classList.add('status-online');
        statusElement.textContent = `🟢 ${message}`;
        break;
      case 'testing':
        statusElement.classList.add('status-offline');
        statusElement.textContent = `🟡 ${message}`;
        break;
      case 'offline':
      default:
        statusElement.classList.add('status-offline');
        statusElement.textContent = `🔴 ${message}`;
        break;
    }
  }

  async function updateStorageInfo() {
    try {
      const allData = await chrome.storage.local.get();
      let summaryCount = 0;
      let transcriptionCount = 0;
      let totalSize = 0;

      for (const [key, value] of Object.entries(allData)) {
        if (key.startsWith('summarize_')) {
          summaryCount++;
          totalSize += JSON.stringify(value).length;
        } else if (key.startsWith('transcribe_')) {
          transcriptionCount++;
          totalSize += JSON.stringify(value).length;
        }
      }

      const sizeInKB = (totalSize / 1024).toFixed(2);
      
      elements.storageInfo.innerHTML = `
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
          <div><strong>Summaries:</strong> ${summaryCount}</div>
          <div><strong>Transcriptions:</strong> ${transcriptionCount}</div>
          <div><strong>Storage Used:</strong> ${sizeInKB} KB</div>
        </div>
      `;
    } catch (error) {
      console.error('Error updating storage info:', error);
      elements.storageInfo.textContent = 'Error loading storage information';
    }
  }

  async function clearStorage() {
    if (confirm('Are you sure you want to clear all stored summaries and transcriptions? This cannot be undone.')) {
      try {
        const allData = await chrome.storage.local.get();
        const keysToRemove = [];

        for (const key of Object.keys(allData)) {
          if (key.startsWith('summarize_') || key.startsWith('transcribe_')) {
            keysToRemove.push(key);
          }
        }

        if (keysToRemove.length > 0) {
          await chrome.storage.local.remove(keysToRemove);
          await updateStorageInfo();
          showSuccessMessage('Storage cleared successfully!');
        } else {
          alert('No data to clear.');
        }
      } catch (error) {
        console.error('Error clearing storage:', error);
        alert('Error clearing storage. Please try again.');
      }
    }
  }

  function getDefaultSettings() {
    return {
      backendUrl: 'http://localhost:8002',
      autoSummarize: false,
      summaryLength: 'medium',
      enableNotifications: true
    };
  }

  function showSuccessMessage(message = 'Settings saved successfully!') {
    elements.successMessage.textContent = message;
    elements.successMessage.style.display = 'block';
    
    setTimeout(() => {
      elements.successMessage.style.display = 'none';
    }, 3000);
  }

  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
});
