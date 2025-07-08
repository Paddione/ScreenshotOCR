/**
 * Performance Test: API Response Times and Load Testing
 * Tests API performance under various load conditions
 */

async function test_api_performance_benchmark() {
    console.log('⚡ Testing API performance and response times...');
    
    try {
        const startTime = Date.now();
        const performanceMetrics = {
            endpoints: {},
            concurrent: {},
            summary: {}
        };
        
        // Step 1: Test individual endpoint response times
        console.log('Step 1: Measuring individual endpoint response times...');
        
        const endpoints = [
            { name: 'health_check', path: '/health', method: 'GET' },
            { name: 'login', path: '/auth/login', method: 'POST', data: { username: 'admin', password: 'admin123' } },
            { name: 'folders', path: '/folders', method: 'GET' },
            { name: 'responses', path: '/responses', method: 'GET' }
        ];
        
        let authToken = null;
        
        for (const endpoint of endpoints) {
            console.log(`Testing ${endpoint.name} endpoint...`);
            
            const measurements = [];
            const attempts = 5;
            
            for (let i = 0; i < attempts; i++) {
                const testStart = performance.now();
                
                const headers = {};
                if (authToken && endpoint.name !== 'login') {
                    headers['Authorization'] = `Bearer ${authToken}`;
                }
                
                const response = await testHelpers.apiCall(
                    endpoint.path,
                    endpoint.method,
                    endpoint.data || null,
                    headers
                );
                
                const testEnd = performance.now();
                const responseTime = testEnd - testStart;
                
                measurements.push({
                    responseTime,
                    status: response.status,
                    success: response.status >= 200 && response.status < 300
                });
                
                // Store auth token from login for subsequent requests
                if (endpoint.name === 'login' && response.status === 200) {
                    authToken = response.data?.access_token || response.data?.token;
                }
                
                // Small delay between requests
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            
            const responseTimes = measurements.map(m => m.responseTime);
            const successCount = measurements.filter(m => m.success).length;
            
            performanceMetrics.endpoints[endpoint.name] = {
                attempts,
                successCount,
                successRate: (successCount / attempts) * 100,
                responseTime: {
                    min: Math.min(...responseTimes),
                    max: Math.max(...responseTimes),
                    avg: responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length,
                    median: responseTimes.sort((a, b) => a - b)[Math.floor(responseTimes.length / 2)]
                }
            };
            
            console.log(`✓ ${endpoint.name}: ${performanceMetrics.endpoints[endpoint.name].responseTime.avg.toFixed(2)}ms avg`);
        }
        
        // Step 2: Test concurrent requests
        console.log('Step 2: Testing concurrent request handling...');
        
        const concurrentTests = [
            { name: 'low_load', concurrent: 3 },
            { name: 'medium_load', concurrent: 10 },
            { name: 'high_load', concurrent: 20 }
        ];
        
        for (const test of concurrentTests) {
            console.log(`Testing ${test.name} (${test.concurrent} concurrent requests)...`);
            
            const concurrentStart = performance.now();
            const promises = [];
            
            for (let i = 0; i < test.concurrent; i++) {
                const promise = testHelpers.apiCall('/health', 'GET').then(response => ({
                    status: response.status,
                    success: response.status === 200,
                    responseTime: performance.now() - concurrentStart
                }));
                promises.push(promise);
            }
            
            const results = await Promise.all(promises);
            const concurrentEnd = performance.now();
            
            const successCount = results.filter(r => r.success).length;
            const responseTimes = results.map(r => r.responseTime);
            
            performanceMetrics.concurrent[test.name] = {
                requestCount: test.concurrent,
                successCount,
                successRate: (successCount / test.concurrent) * 100,
                totalTime: concurrentEnd - concurrentStart,
                responseTime: {
                    min: Math.min(...responseTimes),
                    max: Math.max(...responseTimes),
                    avg: responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length
                }
            };
            
            console.log(`✓ ${test.name}: ${successCount}/${test.concurrent} successful in ${(concurrentEnd - concurrentStart).toFixed(2)}ms`);
        }
        
        // Step 3: Test sustained load
        console.log('Step 3: Testing sustained load over time...');
        
        const sustainedTest = {
            duration: 10000, // 10 seconds
            interval: 500,   // Request every 500ms
            results: []
        };
        
        const sustainedStart = performance.now();
        const endTime = sustainedStart + sustainedTest.duration;
        
        while (performance.now() < endTime) {
            const requestStart = performance.now();
            const response = await testHelpers.apiCall('/health', 'GET');
            const requestEnd = performance.now();
            
            sustainedTest.results.push({
                timestamp: requestStart - sustainedStart,
                responseTime: requestEnd - requestStart,
                status: response.status,
                success: response.status === 200
            });
            
            // Wait for next interval
            const nextRequest = requestStart + sustainedTest.interval;
            const waitTime = Math.max(0, nextRequest - performance.now());
            if (waitTime > 0) {
                await new Promise(resolve => setTimeout(resolve, waitTime));
            }
        }
        
        const sustainedSuccessCount = sustainedTest.results.filter(r => r.success).length;
        const sustainedResponseTimes = sustainedTest.results.map(r => r.responseTime);
        
        performanceMetrics.sustained = {
            duration: sustainedTest.duration,
            requestCount: sustainedTest.results.length,
            successCount: sustainedSuccessCount,
            successRate: (sustainedSuccessCount / sustainedTest.results.length) * 100,
            responseTime: {
                min: Math.min(...sustainedResponseTimes),
                max: Math.max(...sustainedResponseTimes),
                avg: sustainedResponseTimes.reduce((a, b) => a + b, 0) / sustainedResponseTimes.length
            }
        };
        
        console.log(`✓ Sustained load: ${sustainedSuccessCount}/${sustainedTest.results.length} successful over ${sustainedTest.duration}ms`);
        
        // Step 4: Performance validation
        console.log('Step 4: Validating performance criteria...');
        
        const criteria = {
            maxResponseTime: 5000, // 5 seconds max
            minSuccessRate: 95,    // 95% success rate
            maxConcurrentResponseTime: 10000 // 10 seconds for concurrent
        };
        
        let performanceIssues = [];
        
        // Check individual endpoint performance
        for (const [name, metrics] of Object.entries(performanceMetrics.endpoints)) {
            if (metrics.responseTime.avg > criteria.maxResponseTime) {
                performanceIssues.push(`${name} average response time too high: ${metrics.responseTime.avg.toFixed(2)}ms`);
            }
            if (metrics.successRate < criteria.minSuccessRate) {
                performanceIssues.push(`${name} success rate too low: ${metrics.successRate.toFixed(1)}%`);
            }
        }
        
        // Check concurrent performance
        for (const [name, metrics] of Object.entries(performanceMetrics.concurrent)) {
            if (metrics.responseTime.max > criteria.maxConcurrentResponseTime) {
                performanceIssues.push(`${name} max concurrent response time too high: ${metrics.responseTime.max.toFixed(2)}ms`);
            }
            if (metrics.successRate < criteria.minSuccessRate) {
                performanceIssues.push(`${name} concurrent success rate too low: ${metrics.successRate.toFixed(1)}%`);
            }
        }
        
        // Check sustained performance
        if (performanceMetrics.sustained.successRate < criteria.minSuccessRate) {
            performanceIssues.push(`Sustained load success rate too low: ${performanceMetrics.sustained.successRate.toFixed(1)}%`);
        }
        
        // Summary
        const totalTime = (Date.now() - startTime) / 1000;
        performanceMetrics.summary = {
            totalTestTime: totalTime,
            performanceIssues: performanceIssues.length,
            overallHealthy: performanceIssues.length === 0
        };
        
        if (performanceIssues.length > 0) {
            console.log('⚠ Performance issues detected:');
            performanceIssues.forEach(issue => console.log(`  - ${issue}`));
        } else {
            console.log('✓ All performance criteria met');
        }
        
        console.log('🎉 API performance benchmark completed');
        
        return {
            success: true,
            message: `Performance test completed with ${performanceIssues.length} issues`,
            details: {
                metrics: performanceMetrics,
                criteria,
                performanceIssues,
                overallHealth: performanceIssues.length === 0 ? 'GOOD' : 'NEEDS_ATTENTION'
            }
        };
        
    } catch (error) {
        console.error('❌ API performance test failed:', error.message);
        return {
            success: false,
            error: error.message,
            details: {
                testPhase: 'api_performance',
                errorType: error.constructor.name,
                stack: error.stack
            }
        };
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = test_api_performance_benchmark;
} 