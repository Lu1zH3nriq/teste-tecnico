import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';

const initialState = {
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
};

const AUTH_ACTIONS = {
    LOGIN_SUCCESS: 'LOGIN_SUCCESS',
    LOGOUT: 'LOGOUT',
    SET_LOADING: 'SET_LOADING',
    SET_ERROR: 'SET_ERROR',
    CLEAR_ERROR: 'CLEAR_ERROR',
};

function authReducer(state, action) {
    switch (action.type) {
        case AUTH_ACTIONS.LOGIN_SUCCESS:
            return {
                ...state,
                user: action.payload.user,
                isAuthenticated: true,
                isLoading: false,
                error: null,
            };
        case AUTH_ACTIONS.LOGOUT:
            return {
                ...state,
                user: null,
                isAuthenticated: false,
                isLoading: false,
                error: null,
            };
        case AUTH_ACTIONS.SET_LOADING:
            return {
                ...state,
                isLoading: action.payload,
            };
        case AUTH_ACTIONS.SET_ERROR:
            return {
                ...state,
                error: action.payload,
                isLoading: false,
            };
        case AUTH_ACTIONS.CLEAR_ERROR:
            return {
                ...state,
                error: null,
            };
        default:
            return state;
    }
}

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [state, dispatch] = useReducer(authReducer, initialState);

    useEffect(() => {
        const initAuth = () => {
            dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: true });

            if (authService.isAuthenticated()) {
                const user = authService.getCurrentUser();
                dispatch({
                    type: AUTH_ACTIONS.LOGIN_SUCCESS,
                    payload: { user },
                });
            } else {
                dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
            }
        };

        initAuth();
    }, []);

    const login = useCallback(async (email, password) => {
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: true });
        dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });

        const result = await authService.login(email, password);

        if (result.success) {
            dispatch({
                type: AUTH_ACTIONS.LOGIN_SUCCESS,
                payload: { user: result.data.user },
            });
            return { success: true };
        } else {
            dispatch({
                type: AUTH_ACTIONS.SET_ERROR,
                payload: result.error,
            });
            return { 
                success: false, 
                error: result.error, 
                errors: result.errors,
                serverData: result.serverData
            };
        }
    }, []);

    const register = useCallback(async (userData) => {
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: true });
        dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });

        const result = await authService.register(userData);

        if (result.success) {
            dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
            return { success: true };
        } else {
            dispatch({
                type: AUTH_ACTIONS.SET_ERROR,
                payload: result.error,
            });
            return { 
                success: false, 
                error: result.error, 
                errors: result.errors,
                serverData: result.serverData
            };
        }
    }, []);

    const logout = useCallback(async () => {
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: true });

        await authService.logout();
        dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }, []);

    const clearError = useCallback(() => {
        dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
    }, []);

    const value = {
        ...state,
        login,
        register,
        logout,
        clearError,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    
    return context;
}
