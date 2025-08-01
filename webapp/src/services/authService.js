import api from './api';

export const authService = {
    async login(email, password) {
        try {
            const response = await api.post('/api/auth/login/', {
                email,
                password,
            });

            const { access, refresh, user } = response.data;

            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);
            localStorage.setItem('user', JSON.stringify(user));

            return {
                success: true,
                data: { access, refresh, user },
            };
        } catch (error) {
            console.log('Login error response:', error.response?.data);
            
            const serverResponse = error.response?.data || {};
            
            return {
                success: false,
                error: serverResponse.message || 'Erro no login. Verifique suas credenciais.',
                errors: serverResponse.errors || {},
                serverData: serverResponse,
            };
        }
    },

    async register(userData) {
        try {
            const response = await api.post('/api/auth/register/', userData);

            const { user } = response.data;

            return {
                success: true,
                data: { user },
            };
        } catch (error) {
            console.log('Register error response:', error.response?.data);
            
            const serverResponse = error.response?.data || {};
            
            return {
                success: false,
                error: serverResponse.message || 'Erro no cadastro. Tente novamente.',
                errors: serverResponse.errors || {},
                serverData: serverResponse,
            };
        }
    },

    async logout() {
        try {
            const refreshToken = localStorage.getItem('refresh_token');
            
            if (refreshToken) {
                await api.post('/api/auth/logout/', {
                    refresh: refreshToken,
                });
            }

            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');

            return { success: true };
        } catch (error) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');

            return { success: true };
        }
    },

    getCurrentUser() {
        try {
            const user = localStorage.getItem('user');
            return user ? JSON.parse(user) : null;
        } catch {
            return null;
        }
    },

    isAuthenticated() {
        const token = localStorage.getItem('access_token');
        const user = this.getCurrentUser();
        return !!(token && user);
    },

    getAccessToken() {
        return localStorage.getItem('access_token');
    },

    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },
};
