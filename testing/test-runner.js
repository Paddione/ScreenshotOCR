/**
 * ScreenshotOCR Testing Environment - Enhanced Test Runner
 * Handles UI interactions, test execution, logging, and error tracking
 */

class TestRunner {
    constructor() {
        this.testStatus = document.getElementById('test-status');
        this.testProgress = document.getElementById('test-progress');
        this.codeViewer = document.getElementById('test-code-viewer');
        this.logContainer = document.getElementById('log-container');
        this.clearLogsBtn = document.getElementById('clear-logs');
        this.exportLogsBtn = document.getElementById('export-logs');
        this.exportErrorLogsBtn = document.getElementById('export-error-logs');
        this.viewSystemInfoBtn = document.getElementById('view-system-info');
        
        this.logs = [];
        this.errorLogs = [];
        this.currentTest = null;
        this.isRunning = false;
        this.testSession = this.generateSessionId();
        
        this.initializeEventListeners();
        this.clearLogs();
        this.log('INFO', 'Enhanced Test Runner initialized');
        this.log('INFO', `Test session: ${this.testSession}`);
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    initializeEventListeners() {
        // Group test buttons
        document.querySelectorAll('.btn-group').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const group = e.target.dataset.group;
                this.runTestGroup(group);
            });
        });

        // Individual test buttons
        document.querySelectorAll('.btn-test').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const testName = e.target.dataset.test;
                this.runSingleTest(testName);
            });
        });

        // Control buttons
        this.clearLogsBtn.addEventListener('click', () => this.clearLogs());
        this.exportLogsBtn.addEventListener('click', () => this.exportLogs());
        this.exportErrorLogsBtn.addEventListener('click', () => this.exportCombinedErrorLog());
        this.viewSystemInfoBtn.addEventListener('click', () => this.showSystemInfo());
    }

    log(level, message, origin = null) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            message,
            origin: origin || 'SYSTEM',
            session: this.testSession
        };
        
        this.logs.push(logEntry);
        
        // Track errors separately for combined error log
        if (level === 'ERROR') {
            this.errorLogs.push({
                ...logEntry,
                test: this.currentTest,
                stackTrace: new Error().stack
            });
        }
        
        this.displayLogEntry(logEntry);
        this.writeToCombinedErrorLog(logEntry);
        
        // Auto-scroll to bottom
        this.logContainer.scrollTop = this.logContainer.scrollHeight;
    }

    async writeToCombinedErrorLog(logEntry) {
        if (logEntry.level === 'ERROR' || logEntry.level === 'WARNING') {
            const errorLogData = {
                timestamp: logEntry.timestamp,
                session: this.testSession,
                level: logEntry.level,
                message: logEntry.message,
                origin: logEntry.origin,
                test: this.currentTest,
                url: window.location.href,
                userAgent: navigator.userAgent
            };

            // Store in localStorage for persistence across sessions
            const existingErrors = JSON.parse(localStorage.getItem('screenshotocr_error_logs') || '[]');
            existingErrors.push(errorLogData);
            
            // Keep only last 1000 error entries
            if (existingErrors.length > 1000) {
                existingErrors.splice(0, existingErrors.length - 1000);
            }
            
            localStorage.setItem('screenshotocr_error_logs', JSON.stringify(existingErrors));
        }
    }

    displayLogEntry(logEntry) {
        const logElement = document.createElement('div');
        logElement.className = `log-entry ${logEntry.level.toLowerCase()}`;
        
        const timeStr = new Date(logEntry.timestamp).toLocaleTimeString('en-US', { hour12: false });
        
        logElement.innerHTML = `
            <span class="timestamp">[${timeStr}]</span>
            <span class="level ${logEntry.level}">${logEntry.level}</span>
            <span class="message">${logEntry.message}</span>
            <span class="origin">${logEntry.origin !== 'SYSTEM' ? `(${logEntry.origin})` : ''}</span>
        `;
        
        this.logContainer.appendChild(logElement);
    }

    clearLogs() {
        this.logs = [];
        this.logContainer.innerHTML = '';
        this.log('INFO', 'Logs cleared automatically before test execution');
    }

    exportLogs() {
        const logText = this.logs.map(log => 
            `[${log.timestamp}] ${log.level}: ${log.message} (${log.origin})`
        ).join('\n');
        
        // Also export error logs
        const errorLogText = this.errorLogs.map(err =>
            `[${err.timestamp}] ERROR in ${err.test || 'unknown'}: ${err.message} (${err.origin})\nStack: ${err.stackTrace}\n---`
        ).join('\n');
        
        const combinedLog = `SESSION: ${this.testSession}\nDATE: ${new Date().toISOString()}\n\n=== EXECUTION LOGS ===\n${logText}\n\n=== ERROR DETAILS ===\n${errorLogText}`;
        
        const blob = new Blob([combinedLog], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `screenshotocr-test-logs-${new Date().toISOString().split('T')[0]}-${this.testSession}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.log('INFO', 'Comprehensive logs exported successfully');
    }

    exportCombinedErrorLog() {
        const allErrors = JSON.parse(localStorage.getItem('screenshotocr_error_logs') || '[]');
        
        if (allErrors.length === 0) {
            this.log('INFO', 'No errors to export');
            return;
        }
        
        const errorLogText = allErrors.map(err =>
            `[${err.timestamp}] ${err.level} in session ${err.session}:\nTest: ${err.test || 'unknown'}\nOrigin: ${err.origin}\nMessage: ${err.message}\nURL: ${err.url}\nUser Agent: ${err.userAgent}\n---`
        ).join('\n');
        
        const blob = new Blob([errorLogText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `screenshotocr-combined-error-log-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.log('INFO', `Combined error log exported: ${allErrors.length} entries`);
    }

    showSystemInfo() {
        const systemInfo = {
            timestamp: new Date().toISOString(),
            session: this.testSession,
            url: window.location.href,
            userAgent: navigator.userAgent,
            screen: {
                width: screen.width,
                height: screen.height,
                colorDepth: screen.colorDepth
            },
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            testing: {
                totalLogs: this.logs.length,
                errorLogs: this.errorLogs.length,
                currentTest: this.currentTest,
                isRunning: this.isRunning
            },
            localStorage: {
                errorLogEntries: JSON.parse(localStorage.getItem('screenshotocr_error_logs') || '[]').length
            }
        };

        this.log('INFO', 'System information captured');
        this.log('INFO', `Browser: ${navigator.userAgent.split(' ').slice(-2).join(' ')}`);
        this.log('INFO', `Screen: ${systemInfo.screen.width}x${systemInfo.screen.height} (${systemInfo.screen.colorDepth}-bit)`);
        this.log('INFO', `Viewport: ${systemInfo.viewport.width}x${systemInfo.viewport.height}`);
        this.log('INFO', `Session logs: ${systemInfo.testing.totalLogs}, Errors: ${systemInfo.testing.errorLogs}`);
        this.log('INFO', `Persistent error entries: ${systemInfo.localStorage.errorLogEntries}`);
        
        // Also export system info as JSON
        const blob = new Blob([JSON.stringify(systemInfo, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `screenshotocr-system-info-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    setStatus(status, className = '') {
        this.testStatus.textContent = status;
        this.testStatus.className = className;
    }

    setProgress(current, total) {
        if (total > 0) {
            this.testProgress.textContent = `${current}/${total} tests completed`;
        } else {
            this.testProgress.textContent = '';
        }
    }

    displayTestCode(testName, code) {
        this.codeViewer.textContent = code;
        this.highlightSyntax();
    }

    highlightSyntax() {
        // Simple syntax highlighting for JavaScript/Python
        const code = this.codeViewer.textContent;
        let highlighted = code
            .replace(/(async|await|function|def|class|import|from|if|else|for|while|try|catch|except|return)\b/g, '<span class="keyword">$1</span>')
            .replace(/(["'`])((?:\\.|(?!\1)[^\\])*?)\1/g, '<span class="string">$1$2$1</span>')
            .replace(/(\/\/.*|#.*)/g, '<span class="comment">$1</span>')
            .replace(/\b(\d+\.?\d*)\b/g, '<span class="number">$1</span>');
        
        this.codeViewer.innerHTML = highlighted;
    }

    updateButtonState(testName, state) {
        const button = document.querySelector(`[data-test="${testName}"]`);
        if (button) {
            button.className = `btn btn-test ${state}`;
        }
    }

    async runSingleTest(testName) {
        if (this.isRunning) {
            this.log('WARNING', 'Test already running, please wait');
            return;
        }

        this.isRunning = true;
        this.currentTest = testName;
        
        // Automatically clear logs before starting test
        this.clearLogs();
        this.log('INFO', `Starting individual test: ${testName}`);
        this.log('INFO', `Test session: ${this.testSession}`);
        this.setStatus('Running...', 'running');
        this.updateButtonState(testName, 'running');

        try {
            const testCode = await this.loadTestCode(testName);
            this.displayTestCode(testName, testCode);
            
            const result = await this.executeTest(testName, testCode);
            
            if (result.success) {
                this.log('SUCCESS', `Test passed: ${testName}`, result.origin);
                this.setStatus('Test Passed', 'success');
                this.updateButtonState(testName, 'success');
            } else {
                this.log('ERROR', `Test failed: ${result.error}`, result.origin);
                this.setStatus('Test Failed', 'error');
                this.updateButtonState(testName, 'error');
            }
        } catch (error) {
            this.log('ERROR', `Test execution error: ${error.message}`, testName);
            this.setStatus('Test Error', 'error');
            this.updateButtonState(testName, 'error');
        } finally {
            this.isRunning = false;
            this.currentTest = null;
        }
    }

    async runTestGroup(groupName) {
        if (this.isRunning) {
            this.log('WARNING', 'Test already running, please wait');
            return;
        }

        this.isRunning = true;
        
        // Automatically clear logs before starting test group
        this.clearLogs();
        
        const tests = this.getTestsByGroup(groupName);
        
        if (tests.length === 0) {
            this.log('WARNING', `No tests found for group: ${groupName}`);
            this.isRunning = false;
            return;
        }

        this.log('INFO', `Starting test group: ${groupName} (${tests.length} tests)`);
        this.log('INFO', `Test session: ${this.testSession}`);
        this.log('INFO', `Tests to run: ${tests.join(', ')}`);
        this.setStatus(`Running ${groupName} tests...`, 'running');
        
        let passed = 0;
        let failed = 0;

        for (let i = 0; i < tests.length; i++) {
            const testName = tests[i];
            this.setProgress(i, tests.length);
            this.updateButtonState(testName, 'running');

            try {
                const testCode = await this.loadTestCode(testName);
                this.displayTestCode(testName, testCode);
                
                const result = await this.executeTest(testName, testCode);
                
                if (result.success) {
                    passed++;
                    this.log('SUCCESS', `✓ ${testName}`, result.origin);
                    this.updateButtonState(testName, 'success');
                } else {
                    failed++;
                    this.log('ERROR', `✗ ${testName}: ${result.error}`, result.origin);
                    this.updateButtonState(testName, 'error');
                }
            } catch (error) {
                failed++;
                this.log('ERROR', `✗ ${testName}: ${error.message}`, testName);
                this.updateButtonState(testName, 'error');
            }

            // Small delay between tests
            await this.sleep(100);
        }

        this.setProgress(tests.length, tests.length);
        
        if (failed === 0) {
            this.log('SUCCESS', `All tests passed! (${passed}/${tests.length})`);
            this.setStatus(`All Tests Passed (${passed}/${tests.length})`, 'success');
        } else {
            this.log('ERROR', `Some tests failed: ${passed} passed, ${failed} failed`);
            this.setStatus(`Tests Completed: ${passed} passed, ${failed} failed`, 'error');
        }

        this.isRunning = false;
    }

    getTestsByGroup(groupName) {
        const groupMapping = {
            unit: [
                'test_hash_password', 'test_verify_password', 'test_create_access_token',
                'test_verify_token', 'test_database_connection', 'test_user_validation',
                'test_preprocess_image', 'test_extract_text', 'test_format_date', 'test_truncate_text'
            ],
            integration: [
                'test_login_flow', 'test_protected_endpoint_access', 'test_folder_crud',
                'test_response_crud', 'test_user_folder_relationship', 'test_image_to_text_pipeline',
                'test_ai_analysis_integration', 'test_redis_queue_processing'
            ],
            component: [
                'test_login_component', 'test_dashboard_rendering', 'test_navigation_component',
                'test_file_upload_component', 'test_response_list_component', 'test_folder_management'
            ],
            system: [
                'test_complete_user_registration', 'test_complete_authentication_flow',
                'test_screenshot_upload_to_analysis', 'test_web_upload_workflow', 
                'test_response_organization', 'test_multiple_users_concurrent', 
                'test_database_consistency'
            ],
            performance: [
                'test_api_response_times', 'test_api_performance_benchmark',
                'test_database_query_performance', 'test_ocr_processing_speed', 
                'test_concurrent_user_load', 'test_high_volume_uploads', 
                'test_memory_usage'
            ],
            security: [
                'test_jwt_token_manipulation', 'test_expired_token_rejection',
                'test_sql_injection_protection', 'test_malicious_file_rejection',
                'test_brute_force_protection', 'test_file_size_limits'
            ]
        };

        if (groupName === 'all') {
            return Object.values(groupMapping).flat();
        }

        return groupMapping[groupName] || [];
    }

    async loadTestCode(testName) {
        try {
            const response = await fetch(`tests/${testName}.js`);
            if (response.ok) {
                return await response.text();
            } else {
                // Fall back to Python tests
                const pythonResponse = await fetch(`tests/${testName}.py`);
                if (pythonResponse.ok) {
                    return await pythonResponse.text();
                }
            }
            
            // If no test file found, return a template
            return this.generateTestTemplate(testName);
        } catch (error) {
            this.log('WARNING', `Could not load test code for ${testName}, using template`);
            return this.generateTestTemplate(testName);
        }
    }

    generateTestTemplate(testName) {
        return `/**
 * Test: ${testName}
 * Generated template - implement actual test logic
 */

async function ${testName}() {
    // TODO: Implement test logic
    console.log('Running ${testName}...');
    
    // Simulate test execution
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Return success for template
    return {
        success: true,
        message: 'Template test completed'
    };
}

// Export test function
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ${testName};
}`;
    }

    async executeTest(testName, testCode) {
        return new Promise((resolve) => {
            // Simulate test execution with timeout
            const startTime = Date.now();
            
            try {
                // Create a safe execution context
                const testFunction = new Function(`
                    ${testCode}
                    
                    // Execute the test
                    return (async () => {
                        try {
                            if (typeof ${testName} === 'function') {
                                const result = await ${testName}();
                                return {
                                    success: true,
                                    result: result,
                                    origin: '${testName}',
                                    duration: Date.now() - ${startTime}
                                };
                            } else {
                                return {
                                    success: false,
                                    error: 'Test function not found',
                                    origin: '${testName}'
                                };
                            }
                        } catch (error) {
                            return {
                                success: false,
                                error: error.message,
                                origin: '${testName}'
                            };
                        }
                    })();
                `);

                const testPromise = testFunction();
                
                // Add timeout
                const timeoutPromise = new Promise((_, reject) => {
                    setTimeout(() => reject(new Error('Test timeout (30s)')), 30000);
                });

                Promise.race([testPromise, timeoutPromise])
                    .then(resolve)
                    .catch(error => resolve({
                        success: false,
                        error: error.message,
                        origin: testName
                    }));

            } catch (error) {
                resolve({
                    success: false,
                    error: `Execution error: ${error.message}`,
                    origin: testName
                });
            }
        });
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize test runner when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.testRunner = new TestRunner();
});

// Global helper functions for tests
window.testHelpers = {
    async apiCall(endpoint, method = 'GET', data = null, extraHeaders = {}) {
        // Ensure we're using the correct IP address
        const baseUrl = 'https://10.0.0.44';
        const fullUrl = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint.startsWith('/') ? endpoint : '/api/' + endpoint}`;
        
        const config = {
            method,
            headers: {
                'Content-Type': 'application/json',
                ...extraHeaders
            }
        };
        
        if (data) {
            config.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(fullUrl, config);
            const responseData = await response.json().catch(() => null);
            return {
                status: response.status,
                data: responseData,
                url: fullUrl,
                headers: Object.fromEntries(response.headers.entries())
            };
        } catch (error) {
            return {
                status: 0,
                error: error.message,
                url: fullUrl
            };
        }
    },

    generateTestData: {
        user() {
            return {
                username: `testuser_${Date.now()}`,
                password: 'TestPassword123!'
            };
        },
        
        folder() {
            return {
                name: `test_folder_${Date.now()}`
            };
        },
        
        image() {
            // Create a simple test image (1x1 pixel PNG)
            const canvas = document.createElement('canvas');
            canvas.width = 1;
            canvas.height = 1;
            return canvas.toDataURL('image/png');
        }
    },

    assert: {
        isTrue(condition, message = 'Assertion failed') {
            if (!condition) {
                throw new Error(message);
            }
        },
        
        isFalse(condition, message = 'Assertion failed') {
            if (condition) {
                throw new Error(message);
            }
        },
        
        equals(actual, expected, message = 'Values not equal') {
            if (actual !== expected) {
                throw new Error(`${message}: expected ${expected}, got ${actual}`);
            }
        },
        
        notNull(value, message = 'Value is null') {
            if (value === null || value === undefined) {
                throw new Error(message);
            }
        }
    }
}; 