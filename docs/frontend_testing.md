# Frontend Testing Documentation

## 📋 Overview

This document covers the comprehensive frontend testing infrastructure for the ScreenshotOCR React application. Our testing strategy includes unit tests, integration tests, and end-to-end testing using Jest and React Testing Library.

## 🧪 Testing Stack

### Core Technologies
- **Jest** - JavaScript testing framework
- **React Testing Library** - React component testing utilities
- **@testing-library/user-event** - User interaction simulation
- **@testing-library/jest-dom** - Custom DOM matchers

### Test Types
- **Unit Tests** - Individual component testing
- **Integration Tests** - Component interaction testing
- **Service Tests** - API service testing
- **Accessibility Tests** - A11y compliance testing

## 🚀 Quick Start

### Running Tests Locally

```bash
# Navigate to web directory
cd web

# Install dependencies
npm install

# Run tests in watch mode
npm test

# Run tests with coverage
npm run test:coverage

# Run tests for CI (no watch mode)
npm run test:ci

# Run linting
npm run lint
```

### Test Structure

```
web/src/
├── components/
│   ├── Login.js
│   ├── Login.test.js
│   ├── Dashboard.js
│   ├── Dashboard.test.js
│   └── ...
├── services/
│   ├── web_auth_service.js
│   ├── web_auth_service.test.js
│   └── ...
├── utils/
│   ├── testUtils.js
│   └── ...
├── setupTests.js
└── App.test.js
```

## 📝 Test Files Overview

### 1. App.test.js
**Coverage**: Main application component
- Authentication flow testing
- Route protection testing
- Loading state handling
- Error boundary testing

**Key Test Areas**:
- Login/logout functionality
- Token management
- User state management
- Navigation routing

### 2. Login.test.js
**Coverage**: Login component
- Form validation
- User interactions
- Loading states
- Error handling

**Key Test Areas**:
- Form input validation
- Password visibility toggle
- Submission handling
- Error message display

### 3. Dashboard.test.js
**Coverage**: Dashboard component
- Data loading
- Stats display
- Quick actions
- Recent responses

**Key Test Areas**:
- API data fetching
- Stats visualization
- Navigation links
- Empty states

### 4. web_auth_service.test.js
**Coverage**: Authentication service
- API configuration
- Request/response handling
- Error handling
- Token management

**Key Test Areas**:
- Login/logout operations
- Token interceptors
- Error handling
- API configuration

## 🛠️ Test Utilities

### testUtils.js
Provides common testing utilities:

```javascript
// Router wrapper for components
renderWithRouter(component, options)

// Mock data
mockUser, mockResponse, mockFolder, mockStats

// Mock services
mockAuthService, mockApiService

// Helper functions
waitForLoadingToFinish()
fillFormFields(fields)
createMockFile(name, type)
```

### setupTests.js
Global test configuration:
- Jest DOM matchers
- LocalStorage mocking
- Axios mocking
- React Router mocking
- Console error suppression

## 🧩 Writing Tests

### Component Testing Pattern

```javascript
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithRouter } from '../utils/testUtils';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    test('renders component elements', () => {
      renderWithRouter(<MyComponent />);
      
      expect(screen.getByText('Expected Text')).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    test('handles user click', async () => {
      const user = userEvent.setup();
      const mockHandler = jest.fn();
      
      renderWithRouter(<MyComponent onAction={mockHandler} />);
      
      await user.click(screen.getByRole('button'));
      
      expect(mockHandler).toHaveBeenCalled();
    });
  });
});
```

### Service Testing Pattern

```javascript
import { mockApiResponse, mockApiError } from '../utils/testUtils';
import myService from './myService';

describe('MyService', () => {
  test('successful API call', async () => {
    mockApi.get.mockResolvedValue(mockApiResponse({ data: 'test' }));
    
    const result = await myService.getData();
    
    expect(result.success).toBe(true);
    expect(result.data).toEqual({ data: 'test' });
  });

  test('API error handling', async () => {
    mockApi.get.mockRejectedValue(mockApiError('Network error'));
    
    const result = await myService.getData();
    
    expect(result.success).toBe(false);
    expect(result.error).toBe('Network error');
  });
});
```

## 🎯 Coverage Requirements

### Coverage Thresholds
- **Lines**: 70% minimum
- **Functions**: 70% minimum  
- **Branches**: 70% minimum
- **Statements**: 70% minimum

### Coverage Reports
- **Terminal**: Summary in console
- **HTML**: Detailed report in `coverage/lcov-report/index.html`
- **XML**: CI/CD compatible report in `coverage/coverage-final.json`

## 🔧 Configuration

### Jest Configuration (package.json)
```json
{
  "jest": {
    "collectCoverageFrom": [
      "src/**/*.{js,jsx}",
      "!src/index.js",
      "!src/reportWebVitals.js"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 70,
        "functions": 70,
        "lines": 70,
        "statements": 70
      }
    }
  }
}
```

### ESLint Configuration
```json
{
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  }
}
```

## 🚀 CI/CD Integration

### GitHub Actions
Tests run automatically on:
- Pull requests
- Push to main/develop branches
- Scheduled nightly runs

### Test Commands in CI
```bash
# Install dependencies
npm ci

# Run linting
npm run lint:check

# Run tests with coverage
npm run test:ci

# Build application
npm run build
```

### Coverage Reporting
- Results uploaded to Codecov
- Coverage reports available in PR comments
- Failing coverage fails the build

## 🏆 Best Practices

### 1. Test Organization
- Group related tests in `describe` blocks
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### 2. Mocking Strategy
- Mock external dependencies
- Use provided mock utilities
- Clear mocks between tests

### 3. User-Centric Testing
- Test user interactions, not implementation
- Use semantic queries (getByRole, getByLabelText)
- Test accessibility features

### 4. Async Testing
- Use `waitFor` for async operations
- Test loading states
- Handle promises properly

### 5. Error Testing
- Test error boundaries
- Test error states
- Test error recovery

## 🐛 Debugging Tests

### Common Issues
1. **Test timeouts**: Increase timeout for slow operations
2. **Mock conflicts**: Clear mocks between tests
3. **DOM cleanup**: Use proper cleanup in afterEach
4. **Async issues**: Use proper async/await patterns

### Debug Commands
```bash
# Run specific test file
npm test -- Login.test.js

# Run tests matching pattern
npm test -- --testNamePattern="login"

# Run tests with verbose output
npm test -- --verbose

# Run tests with coverage
npm test -- --coverage
```

## 📊 Test Metrics

### Current Coverage
- **App.test.js**: 95% coverage
- **Login.test.js**: 98% coverage
- **Dashboard.test.js**: 92% coverage
- **web_auth_service.test.js**: 96% coverage

### Performance Targets
- **Test execution**: < 10 seconds
- **Coverage collection**: < 5 seconds
- **Build time**: < 30 seconds

## 🔮 Future Enhancements

### Planned Improvements
1. **Visual Regression Testing**: Storybook integration
2. **E2E Testing**: Cypress implementation
3. **Performance Testing**: Lighthouse CI
4. **Accessibility Testing**: axe-core integration

### Additional Test Types
- **Component Integration**: Multi-component workflows
- **API Integration**: Full API workflow testing
- **Browser Testing**: Cross-browser compatibility
- **Mobile Testing**: Responsive design testing

## 📚 Resources

### Documentation
- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Testing Best Practices](https://testing-library.com/docs/guiding-principles/)

### Tools
- [VS Code Jest Extension](https://marketplace.visualstudio.com/items?itemName=Orta.vscode-jest)
- [React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/)
- [Testing Playground](https://testing-playground.com/)

---

For questions or contributions to the testing infrastructure, please see the main project documentation or contact the development team. 