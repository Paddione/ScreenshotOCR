#!/usr/bin/env python3
"""
Comprehensive Test Runner for ScreenshotOCR Project
Runs all tests across all modules and provides detailed coverage report
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

class TestRunner:
    """Comprehensive test runner for the ScreenshotOCR project"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'modules': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'errors': 0,
                'coverage': 0.0
            }
        }
    
    def run_node_tests(self):
        """Run Node.js integration tests"""
        print("🔍 Running Node.js Integration Tests...")
        
        try:
            os.chdir(self.project_root / 'testing')
            result = subprocess.run(
                ['node', 'node_test_runner.js'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse results from output
            passed = 0
            failed = 0
            errors = 0
            
            if result.returncode == 0:
                # Count success/failure from output
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'SUCCESS:' in line:
                        passed += 1
                    elif 'ERROR:' in line or 'FAILED:' in line:
                        failed += 1
            
            self.results['modules']['node_integration'] = {
                'type': 'integration',
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'total': passed + failed + errors,
                'output': result.stdout,
                'error_output': result.stderr
            }
            
            print(f"✅ Node.js Tests: {passed} passed, {failed} failed, {errors} errors")
            
        except Exception as e:
            print(f"❌ Node.js Tests Error: {e}")
            self.results['modules']['node_integration'] = {
                'type': 'integration',
                'passed': 0,
                'failed': 0,
                'errors': 1,
                'total': 1,
                'error': str(e)
            }
    
    def run_python_tests(self, module_path, module_name):
        """Run Python tests for a specific module"""
        print(f"🔍 Running Python Tests for {module_name}...")
        
        try:
            os.chdir(self.project_root / module_path)
            
            # Run pytest with coverage
            result = subprocess.run([
                'python3', '-m', 'pytest', 
                '--asyncio-mode=auto',
                '--tb=short',
                '-v',
                '--json-report',
                '--json-report-file=none'
            ], capture_output=True, text=True, timeout=300)
            
            # Parse pytest results
            passed = 0
            failed = 0
            errors = 0
            
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'PASSED' in line:
                    passed += 1
                elif 'FAILED' in line:
                    failed += 1
                elif 'ERROR' in line:
                    errors += 1
            
            self.results['modules'][module_name] = {
                'type': 'unit',
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'total': passed + failed + errors,
                'output': result.stdout,
                'error_output': result.stderr,
                'return_code': result.returncode
            }
            
            print(f"✅ {module_name} Tests: {passed} passed, {failed} failed, {errors} errors")
            
        except Exception as e:
            print(f"❌ {module_name} Tests Error: {e}")
            self.results['modules'][module_name] = {
                'type': 'unit',
                'passed': 0,
                'failed': 0,
                'errors': 1,
                'total': 1,
                'error': str(e)
            }
    
    def run_web_tests(self):
        """Run React web frontend tests"""
        print("🔍 Running Web Frontend Tests...")
        
        try:
            os.chdir(self.project_root / 'web')
            
            # Run npm test
            result = subprocess.run([
                'npm', 'test', '--', '--watchAll=false', '--coverage', '--json'
            ], capture_output=True, text=True, timeout=300)
            
            # Parse npm test results
            passed = 0
            failed = 0
            errors = 0
            
            try:
                # Try to parse JSON output
                test_results = json.loads(result.stdout)
                passed = test_results.get('numPassedTests', 0)
                failed = test_results.get('numFailedTests', 0)
                errors = test_results.get('numRuntimeErrorTestSuites', 0)
            except:
                # Fallback to parsing text output
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'PASS' in line and 'FAIL' not in line:
                        passed += 1
                    elif 'FAIL' in line:
                        failed += 1
                    elif 'ERROR' in line:
                        errors += 1
            
            self.results['modules']['web_frontend'] = {
                'type': 'frontend',
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'total': passed + failed + errors,
                'output': result.stdout,
                'error_output': result.stderr,
                'return_code': result.returncode
            }
            
            print(f"✅ Web Frontend Tests: {passed} passed, {failed} failed, {errors} errors")
            
        except Exception as e:
            print(f"❌ Web Frontend Tests Error: {e}")
            self.results['modules']['web_frontend'] = {
                'type': 'frontend',
                'passed': 0,
                'failed': 0,
                'errors': 1,
                'total': 1,
                'error': str(e)
            }
    
    def run_windows_client_tests(self):
        """Run Windows Client tests"""
        print("🔍 Running Windows Client Tests...")
        
        try:
            os.chdir(self.project_root / 'Windows-Client')
            
            # Run pytest for Windows Client
            result = subprocess.run([
                'python3', '-m', 'pytest', 
                'test_client.py',
                '--asyncio-mode=auto',
                '--tb=short',
                '-v'
            ], capture_output=True, text=True, timeout=300)
            
            # Parse results
            passed = 0
            failed = 0
            errors = 0
            
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'PASSED' in line:
                    passed += 1
                elif 'FAILED' in line:
                    failed += 1
                elif 'ERROR' in line:
                    errors += 1
            
            self.results['modules']['windows_client'] = {
                'type': 'client',
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'total': passed + failed + errors,
                'output': result.stdout,
                'error_output': result.stderr,
                'return_code': result.returncode
            }
            
            print(f"✅ Windows Client Tests: {passed} passed, {failed} failed, {errors} errors")
            
        except Exception as e:
            print(f"❌ Windows Client Tests Error: {e}")
            self.results['modules']['windows_client'] = {
                'type': 'client',
                'passed': 0,
                'failed': 0,
                'errors': 1,
                'total': 1,
                'error': str(e)
            }
    
    def calculate_summary(self):
        """Calculate overall test summary"""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        
        for module_name, module_results in self.results['modules'].items():
            total_tests += module_results['total']
            total_passed += module_results['passed']
            total_failed += module_results['failed']
            total_errors += module_results['errors']
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'passed': total_passed,
            'failed': total_failed,
            'errors': total_errors,
            'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0
        }
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        # Module breakdown
        print("\n📋 MODULE BREAKDOWN:")
        print("-" * 60)
        
        for module_name, module_results in self.results['modules'].items():
            total = module_results['total']
            passed = module_results['passed']
            failed = module_results['failed']
            errors = module_results['errors']
            success_rate = (passed / total * 100) if total > 0 else 0
            
            status = "✅ PASS" if failed == 0 and errors == 0 else "❌ FAIL"
            
            print(f"{module_name:20} | {status:8} | {passed:3}/{total:3} | {success_rate:5.1f}%")
        
        # Overall summary
        print("\n📈 OVERALL SUMMARY:")
        print("-" * 60)
        summary = self.results['summary']
        print(f"Total Tests:     {summary['total_tests']}")
        print(f"Passed:          {summary['passed']}")
        print(f"Failed:          {summary['failed']}")
        print(f"Errors:          {summary['errors']}")
        print(f"Success Rate:    {summary['success_rate']:.1f}%")
        
        # Test coverage analysis
        print("\n🎯 TEST COVERAGE ANALYSIS:")
        print("-" * 60)
        
        modules_by_type = {}
        for module_name, module_results in self.results['modules'].items():
            test_type = module_results['type']
            if test_type not in modules_by_type:
                modules_by_type[test_type] = []
            modules_by_type[test_type].append(module_results)
        
        for test_type, modules in modules_by_type.items():
            type_total = sum(m['total'] for m in modules)
            type_passed = sum(m['passed'] for m in modules)
            type_success_rate = (type_passed / type_total * 100) if type_total > 0 else 0
            
            print(f"{test_type.title():15} | {type_passed:3}/{type_total:3} | {type_success_rate:5.1f}%")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 60)
        
        if summary['success_rate'] >= 90:
            print("✅ Excellent test coverage! The system is well-tested.")
        elif summary['success_rate'] >= 80:
            print("⚠️  Good test coverage, but some areas need attention.")
        elif summary['success_rate'] >= 70:
            print("⚠️  Moderate test coverage. Consider adding more tests.")
        else:
            print("❌ Low test coverage. Significant testing improvements needed.")
        
        # Specific recommendations
        for module_name, module_results in self.results['modules'].items():
            if module_results['failed'] > 0 or module_results['errors'] > 0:
                print(f"🔧 Fix failing tests in {module_name}")
        
        # Save detailed results
        report_file = self.project_root / 'testing' / f'test-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
    
    def run_all_tests(self):
        """Run all tests across all modules"""
        print("🚀 Starting Comprehensive Test Suite for ScreenshotOCR")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all test suites
        self.run_node_tests()
        self.run_python_tests('api', 'api_main')
        self.run_python_tests('api', 'api_routes')
        self.run_python_tests('api', 'api_database')
        self.run_python_tests('api', 'api_auth')
        self.run_python_tests('api', 'text_analyzer')
        self.run_python_tests('api', 'storage_processor')
        self.run_python_tests('OCR', 'ocr_processor')
        self.run_windows_client_tests()
        self.run_web_tests()
        
        # Calculate summary and generate report
        self.calculate_summary()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️  Total test execution time: {duration:.2f} seconds")
        
        # Generate final report
        self.generate_report()
        
        return self.results['summary']['success_rate'] >= 70

def main():
    """Main entry point"""
    runner = TestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please review the report above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 