# ScreenshotOCR Testing Environment

## 🧪 Enhanced Testing Interface

This directory contains a comprehensive testing environment for the ScreenshotOCR system, featuring an advanced HTML interface with automated logging, error tracking, and performance benchmarking.

## 🚀 Quick Start

### Accessing the Testing Interface

1. **Start the ScreenshotOCR system**:
   ```bash
   ./rebuild.sh
   ```

2. **Open the testing interface**:
   ```
   https://web.korczewski.de/testing/
   ```
   or open `testing/index.html` directly in your browser

### First Time Setup

The testing environment is ready to use immediately. No additional setup required!

## 🎯 Features Overview

### Automatic Log Management
- **Auto-Clear Logs**: Logs automatically clear before each test execution
- **Session Tracking**: Each test session gets a unique identifier
- **Real-time Display**: Live log updates with color-coded severity levels

### Enhanced Error Tracking
- **Combined Error Log**: Persistent error tracking across browser sessions
- **Origin Identification**: Each error includes test name, session ID, and stack trace
- **Local Storage Persistence**: Error logs survive browser restarts
- **Export Functionality**: Export session logs and combined error reports

### Code Viewer
- **Live Code Display**: Shows the actual test code being executed
- **Syntax Highlighting**: JavaScript/Python syntax highlighting
- **Real-time Updates**: Code updates as tests run

### Performance Monitoring
- **Response Time Tracking**: Measures API response times
- **Concurrent Load Testing**: Tests system under various load conditions
- **Success Rate Monitoring**: Tracks test pass/fail rates
- **Performance Criteria Validation**: Automatic performance threshold checking

## 🧩 Test Categories

### 1. Unit Tests (Individual Functions)
- Password hashing and verification
- JWT token creation and validation
- Database connection testing
- OCR preprocessing and text extraction
- Utility function validation

### 2. Integration Tests (Component Interactions)
- Complete authentication flow
- CRUD operations for folders and responses
- OCR processing pipeline
- Redis queue management
- API endpoint integration

### 3. Component Tests (UI Components)
- React component rendering
- User interaction handling
- Authentication state management
- File upload functionality
- Navigation and routing

### 4. System Tests (End-to-End Workflows)
- **NEW**: Complete authentication flow test
- Screenshot upload and processing workflow
- Multi-user concurrent operations
- Data consistency validation
- Response organization and management

### 5. Performance Tests
- **NEW**: Comprehensive API performance benchmark
- Database query optimization
- OCR processing speed
- Load testing under various conditions
- Memory usage monitoring

### 6. Security Tests
- JWT token manipulation attempts
- SQL injection protection
- File upload security validation
- Access control verification
- Rate limiting enforcement

## 🔧 How to Use

### Running Individual Tests

1. **Select a Test**: Click any test button from the categories
2. **Monitor Progress**: Watch the code viewer and logs in real-time
3. **Review Results**: Check the status indicator and detailed logs
4. **Export Logs**: Use "Export Session Logs" for detailed reports

### Running Test Groups

1. **Choose a Group**: Click on test group buttons (Unit, Integration, etc.)
2. **Monitor Execution**: Tests run sequentially with progress indicators
3. **Review Summary**: Final report shows pass/fail counts and issues
4. **Export Reports**: Save comprehensive test reports

### Running All Tests

1. **Click "🚀 Run All Tests"**: Executes the complete test suite
2. **Monitor Progress**: Track overall progress and individual test results
3. **Review Summary**: Complete system health report
4. **Export Everything**: Full test suite results and performance metrics

## 📊 Understanding Test Results

### Status Indicators
- **🟢 Green**: Test passed successfully
- **🔴 Red**: Test failed with errors
- **🟡 Yellow**: Test running or warning conditions
- **⚪ Gray**: Test not yet executed

### Log Levels
- **INFO**: General information and progress updates
- **SUCCESS**: Test passed or positive outcomes
- **WARNING**: Non-critical issues or fallbacks
- **ERROR**: Test failures or critical issues

### Performance Metrics
- **Response Times**: Average, min, max response times
- **Success Rates**: Percentage of successful requests
- **Concurrent Performance**: Multi-request handling capabilities
- **Load Testing**: System performance under stress

## 🔍 Advanced Features

### System Information Export
Click "System Info" to export:
- Browser and system details
- Screen and viewport dimensions
- Current test session information
- Local storage statistics
- Performance metrics summary

### Combined Error Log
Click "Export Combined Error Log" to get:
- All errors across all testing sessions
- Complete stack traces and context
- Session correlation information
- System environment details

### Performance Benchmarking
The API Performance Benchmark test provides:
- Individual endpoint response times
- Concurrent request handling
- Sustained load testing over time
- Performance criteria validation
- Detailed metrics for optimization

## 🛠️ Configuration

### Network Settings
All tests are pre-configured to use:
- **Base URL**: `https://web.korczewski.de`
- **API Endpoints**: `/api/*`
- **Authentication**: Bearer token support
- **SSL**: Full HTTPS support

### Test Parameters
Default test configurations:
- **API Timeout**: 30 seconds
- **Concurrent Tests**: 3, 10, 20 requests
- **Sustained Load**: 10 seconds duration
- **Performance Criteria**: 5s max response, 95% success rate

### Error Logging
- **Storage**: Browser localStorage
- **Retention**: Last 1000 error entries
- **Export**: Automatic filename generation
- **Format**: Plain text with timestamps and context

## 📁 File Structure

```
testing/
├── index.html              # Main testing interface
├── test-runner.js          # Enhanced test execution engine
├── styles.css              # UI styling and layout
├── README.md              # This documentation
└── tests/                 # Test files directory
    ├── test_hash_password.js
    ├── test_login_flow.js
    ├── test_database_connection.js
    ├── test_preprocess_image.py
    ├── test_screenshot_upload_to_analysis.js
    ├── test_complete_authentication_flow.js  # NEW
    └── test_api_performance_benchmark.js     # NEW
```

## 🚨 Troubleshooting

### Common Issues

1. **Tests Fail to Load**
   - Ensure the ScreenshotOCR system is running
   - Check that you can access `https://web.korczewski.de`
   - Verify network connectivity

2. **Authentication Errors**
   - Default credentials: admin / admin123
   - Check API server status
   - Verify JWT configuration

3. **Performance Test Failures**
   - System may be under heavy load
   - Check other running containers
   - Review performance criteria in test code

4. **Code Viewer Empty**
   - Test files may be missing
   - Check tests/ directory
   - Fallback templates will be used

### Error Recovery

- **Clear Browser Cache**: Reload the page
- **Reset Local Storage**: Use browser dev tools
- **Export Error Logs**: Before clearing for debugging
- **Check System Info**: For environment diagnostics

## 🔄 Continuous Improvement

### Adding New Tests

1. Create test file in `tests/` directory
2. Follow existing test patterns
3. Add test to appropriate category in `index.html`
4. Update test groups mapping in `test-runner.js`

### Performance Tuning

1. Review performance benchmark results
2. Adjust criteria in test files as needed
3. Monitor system resources during testing
4. Optimize based on error log analysis

### Documentation Updates

Keep documentation current when:
- Adding new test categories
- Changing performance criteria
- Updating network configuration
- Modifying error handling

## 🎉 Success Metrics

The testing environment helps ensure:
- **95%+ test success rate**
- **< 5 second API response times**
- **Comprehensive error tracking**
- **Automated performance monitoring**
- **Complete system validation**

For more detailed information, see the comprehensive testing documentation in `/docs/testing_configuration.md`. 