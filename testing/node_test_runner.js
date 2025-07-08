#!/usr/bin/env node
/**
 * ScreenshotOCR Comprehensive Test Runner
 * Node.js implementation to run all tests programmatically
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

class NodeTestRunner {
    constructor() {
        this.baseUrl = 'https://10.0.0.44';
        this.testResults = [];
        this.errorLogs = [];
        this.sessionId = `node_session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.httpsAgent = new https.Agent({
            rejectUnauthorized: false // Allow self-signed certificates
        });
        
        this.log('INFO', 'Node Test Runner initialized');
        this.log('INFO', `Session ID: ${this.sessionId}`);
    }

    log(level, message, origin = 'SYSTEM') {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            message,
            origin,
            session: this.sessionId
        };
        
        if (level === 'ERROR') {
            this.errorLogs.push(logEntry);
        }
        
        const timeStr = new Date().toLocaleTimeString('en-US', { hour12: false });
        console.log(`[${timeStr}] ${level}: ${message} (${origin})`);
    }

    async apiCall(endpoint, method = 'GET', data = null, extraHeaders = {}) {
        return new Promise((resolve) => {
            const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}/api${endpoint}`;
            const parsedUrl = new URL(url);
            
            const options = {
                hostname: parsedUrl.hostname,
                port: parsedUrl.port || (parsedUrl.protocol === 'https:' ? 443 : 80),
                path: parsedUrl.pathname + parsedUrl.search,
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'User-Agent': 'ScreenshotOCR-TestRunner/1.0',
                    ...extraHeaders
                },
                agent: this.httpsAgent
            };

            if (data && method !== 'GET') {
                const postData = JSON.stringify(data);
                options.headers['Content-Length'] = Buffer.byteLength(postData);
            }

            const req = https.request(options, (res) => {
                let responseData = '';

                res.on('data', (chunk) => {
                    responseData += chunk;
                });

                res.on('end', () => {
                    try {
                        const parsedData = responseData ? JSON.parse(responseData) : {};
                        resolve({
                            status: res.statusCode,
                            data: parsedData,
                            headers: res.headers
                        });
                    } catch (parseError) {
                        resolve({
                            status: res.statusCode,
                            data: responseData,
                            error: 'Failed to parse JSON response'
                        });
                    }
                });
            });

            req.on('error', (error) => {
                resolve({
                    status: 0,
                    error: error.message,
                    data: null
                });
            });

            req.setTimeout(30000, () => {
                req.destroy();
                resolve({
                    status: 0,
                    error: 'Request timeout',
                    data: null
                });
            });

            if (data && method !== 'GET') {
                req.write(JSON.stringify(data));
            }

            req.end();
        });
    }

    createTestHelpers() {
        return {
            apiCall: this.apiCall.bind(this),
            assert: {
                isTrue: (condition, message = 'Assertion failed') => {
                    if (!condition) {
                        throw new Error(message);
                    }
                },
                isFalse: (condition, message = 'Assertion failed') => {
                    if (condition) {
                        throw new Error(message);
                    }
                },
                equals: (actual, expected, message = 'Values not equal') => {
                    if (actual !== expected) {
                        throw new Error(`${message}: expected ${expected}, got ${actual}`);
                    }
                },
                notNull: (value, message = 'Value is null') => {
                    if (value === null || value === undefined) {
                        throw new Error(message);
                    }
                }
            },
            generators: {
                user: () => ({
                    username: `testuser_${Date.now()}`,
                    password: 'TestPassword123!'
                }),
                folder: () => ({
                    name: `TestFolder_${Date.now()}`
                })
            }
        };
    }

    async loadAndExecuteTest(testFile) {
        const testName = path.basename(testFile, '.js');
        this.log('INFO', `Loading test: ${testName}`, testName);
        
        try {
            const testPath = path.join(__dirname, 'tests', testFile);
            
            if (!fs.existsSync(testPath)) {
                throw new Error(`Test file not found: ${testPath}`);
            }
            
            // Read and evaluate the test file
            const testCode = fs.readFileSync(testPath, 'utf8');
            
            // Create a safe execution context
            const testHelpers = this.createTestHelpers();
            const testFunction = new Function('testHelpers', 'console', `
                ${testCode}
                return ${testName};
            `);
            
            const testFunc = testFunction(testHelpers, console);
            
            if (typeof testFunc !== 'function') {
                throw new Error(`Test ${testName} does not export a function`);
            }
            
            this.log('INFO', `Executing test: ${testName}`, testName);
            const result = await testFunc();
            
            this.testResults.push({
                name: testName,
                success: result.success,
                message: result.message,
                details: result.details,
                timestamp: new Date().toISOString()
            });
            
            if (result.success) {
                this.log('SUCCESS', `Test passed: ${result.message}`, testName);
            } else {
                this.log('ERROR', `Test failed: ${result.error || result.message}`, testName);
            }
            
            return result;
            
        } catch (error) {
            this.log('ERROR', `Test execution failed: ${error.message}`, testName);
            this.testResults.push({
                name: testName,
                success: false,
                error: error.message,
                timestamp: new Date().toISOString()
            });
            
            return {
                success: false,
                error: error.message,
                testName
            };
        }
    }

    async runTestGroup(groupName) {
        const testGroups = {
            unit: [
                'test_hash_password.js',
                'test_database_connection.js'
            ],
            integration: [
                'test_login_flow.js'
            ],
            system: [
                'test_complete_authentication_flow.js',
                'test_screenshot_upload_to_analysis.js'
            ],
            performance: [
                'test_api_performance_benchmark.js'
            ]
        };
        
        const tests = testGroups[groupName] || [];
        
        if (tests.length === 0) {
            this.log('WARNING', `No tests found for group: ${groupName}`);
            return [];
        }
        
        this.log('INFO', `Running ${groupName} tests: ${tests.length} tests`);
        
        const results = [];
        for (const test of tests) {
            const result = await this.loadAndExecuteTest(test);
            results.push(result);
        }
        
        return results;
    }

    async runAllTests() {
        this.log('INFO', '🚀 Starting comprehensive test execution');
        
        const startTime = Date.now();
        
        // Get all JavaScript test files
        const testDir = path.join(__dirname, 'tests');
        const testFiles = fs.readdirSync(testDir)
            .filter(file => file.endsWith('.js'))
            .sort();
        
        this.log('INFO', `Found ${testFiles.length} test files`);
        
        // Run all tests
        for (const testFile of testFiles) {
            await this.loadAndExecuteTest(testFile);
            
            // Small delay between tests
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        const totalTime = (Date.now() - startTime) / 1000;
        
        // Generate summary
        this.generateSummary(totalTime);
        
        return this.testResults;
    }

    generateSummary(totalTime) {
        const passed = this.testResults.filter(r => r.success).length;
        const failed = this.testResults.filter(r => !r.success).length;
        const total = this.testResults.length;
        
        this.log('INFO', '📊 TEST EXECUTION SUMMARY');
        this.log('INFO', `Total tests: ${total}`);
        this.log('INFO', `Passed: ${passed}`);
        this.log('INFO', `Failed: ${failed}`);
        this.log('INFO', `Success rate: ${((passed / total) * 100).toFixed(1)}%`);
        this.log('INFO', `Total time: ${totalTime}s`);
        
        if (failed > 0) {
            this.log('ERROR', 'FAILED TESTS:');
            this.testResults
                .filter(r => !r.success)
                .forEach(r => {
                    this.log('ERROR', `- ${r.name}: ${r.error || r.message}`);
                });
        }
        
        this.log('INFO', '✅ Test execution completed');
    }

    exportResults() {
        const timestamp = new Date().toISOString().split('T')[0];
        const filename = `test-results-${timestamp}-${this.sessionId}.json`;
        
        const report = {
            session: this.sessionId,
            timestamp: new Date().toISOString(),
            summary: {
                total: this.testResults.length,
                passed: this.testResults.filter(r => r.success).length,
                failed: this.testResults.filter(r => !r.success).length
            },
            results: this.testResults,
            errors: this.errorLogs
        };
        
        fs.writeFileSync(filename, JSON.stringify(report, null, 2));
        this.log('INFO', `Results exported to: ${filename}`);
        
        return filename;
    }
}

// Main execution
async function main() {
    const runner = new NodeTestRunner();
    
    try {
        // Check command line arguments
        const args = process.argv.slice(2);
        
        if (args.length > 0 && args[0] !== 'all') {
            // Run specific test group
            const groupName = args[0];
            await runner.runTestGroup(groupName);
        } else {
            // Run all tests
            await runner.runAllTests();
        }
        
        // Export results
        runner.exportResults();
        
        // Exit with appropriate code
        const failed = runner.testResults.filter(r => !r.success).length;
        process.exit(failed > 0 ? 1 : 0);
        
    } catch (error) {
        console.error('Fatal error:', error.message);
        process.exit(1);
    }
}

// Run if called directly
if (require.main === module) {
    main();
}

module.exports = NodeTestRunner; 