import authService from './web_auth_service';

// Export the same interface that tests expect
export const getAuthToken = () => localStorage.getItem('token');
export const logout = () => authService.logout();
export const getCurrentUser = () => authService.getCurrentUser();

export default authService; 