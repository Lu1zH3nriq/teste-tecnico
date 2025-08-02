import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './AuthForms.css';

function RegisterForm() {
    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        confirmPassword: '',
    });
    const [validationErrors, setValidationErrors] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    
    const { register, isLoading, clearError, isAuthenticated, error } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated) {
            navigate('/dashboard');
        }
    }, [isAuthenticated, navigate]);

    useEffect(() => {
        clearError();
    }, []);

    useEffect(() => {
        if (error) {
            setErrorMessage(error);
        }
    }, [error]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value,
        }));
        if (errorMessage) {
            setErrorMessage('');
            clearError();
        }
        if (successMessage) {
            setSuccessMessage('');
        }
        if (validationErrors[name]) {
            setValidationErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const validateForm = () => {
        const errors = {};
        if (!formData.firstName.trim()) {
            errors.firstName = 'Nome é obrigatório';
        }
        if (!formData.lastName.trim()) {
            errors.lastName = 'Sobrenome é obrigatório';
        }
        if (!formData.email.trim()) {
            errors.email = 'Email é obrigatório';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            errors.email = 'Email inválido';
        }
        if (!formData.password) {
            errors.password = 'Senha é obrigatória';
        } else if (formData.password.length < 6) {
            errors.password = 'Senha deve ter pelo menos 6 caracteres';
        }
        if (!formData.confirmPassword) {
            errors.confirmPassword = 'Confirmação de senha é obrigatória';
        } else if (formData.password !== formData.confirmPassword) {
            errors.confirmPassword = 'Senhas não coincidem';
        }
        return errors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        setErrorMessage('');
        setSuccessMessage('');
        setValidationErrors({});
        const errors = validateForm();
        if (Object.keys(errors).length > 0) {
            setValidationErrors(errors);
            setIsSubmitting(false);
            return;
        }
        try {
            const userData = {
                first_name: formData.firstName,
                last_name: formData.lastName,
                email: formData.email,
                password: formData.password,
                confirm_password: formData.confirmPassword,
            };
            const result = await register(userData);
            if (result.success) {
                setSuccessMessage('Conta criada com sucesso! Você pode fazer login agora.');
                setFormData({
                    firstName: '',
                    lastName: '',
                    email: '',
                    password: '',
                    confirmPassword: '',
                });
                setTimeout(() => {
                    navigate('/login');
                }, 200);
            } else {
                if (result.errors && typeof result.errors === 'object') {
                    const serverErrors = {};
                    if (result.errors.email) {
                        serverErrors.email = Array.isArray(result.errors.email) 
                            ? result.errors.email[0] 
                            : result.errors.email;
                    }
                    if (result.errors.first_name) {
                        serverErrors.firstName = Array.isArray(result.errors.first_name) 
                            ? result.errors.first_name[0] 
                            : result.errors.first_name;
                    }
                    if (result.errors.last_name) {
                        serverErrors.lastName = Array.isArray(result.errors.last_name) 
                            ? result.errors.last_name[0] 
                            : result.errors.last_name;
                    }
                    if (result.errors.password) {
                        serverErrors.password = Array.isArray(result.errors.password) 
                            ? result.errors.password[0] 
                            : result.errors.password;
                    }
                    if (result.errors.confirm_password) {
                        serverErrors.confirmPassword = Array.isArray(result.errors.confirm_password) 
                            ? result.errors.confirm_password[0] 
                            : result.errors.confirm_password;
                    }
                    setValidationErrors(serverErrors);
                    const fieldErrors = ['email', 'first_name', 'last_name', 'password'];
                    const hasOnlyFieldErrors = Object.keys(result.errors).every(key => fieldErrors.includes(key));
                    if (!hasOnlyFieldErrors) {
                        const errorMsg = result.error || result.message || 'Erro ao criar conta. Verifique os dados informados.';
                        setErrorMessage(errorMsg);
                    }
                } else {
                    const errorMsg = result.error || result.message || 'Erro ao criar conta. Tente novamente.';
                    setErrorMessage(errorMsg);
                }
            }
        } catch (err) {
            setErrorMessage('Erro inesperado. Tente novamente.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <h1>Criar Conta</h1>
                    <p>Preencha os dados para criar sua conta</p>
                </div>
                <form onSubmit={handleSubmit} className="auth-form">
                    {errorMessage && (
                        <div className="error-message">
                            <span className="error-icon">⚠️</span>
                            <span>{errorMessage}</span>
                        </div>
                    )}
                    {successMessage && (
                        <div className="success-message">
                            <span className="success-icon">✅</span>
                            <span>{successMessage}</span>
                        </div>
                    )}
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="firstName">Nome</label>
                            <input
                                type="text"
                                id="firstName"
                                name="firstName"
                                value={formData.firstName}
                                onChange={handleChange}
                                placeholder="Digite seu nome"
                                required
                                className={`form-input ${validationErrors.firstName ? 'error' : ''}`}
                                disabled={isLoading || isSubmitting}
                            />
                            {validationErrors.firstName && (
                                <span className="field-error">{validationErrors.firstName}</span>
                            )}
                        </div>
                        <div className="form-group">
                            <label htmlFor="lastName">Sobrenome</label>
                            <input
                                type="text"
                                id="lastName"
                                name="lastName"
                                value={formData.lastName}
                                onChange={handleChange}
                                placeholder="Digite seu sobrenome"
                                required
                                className={`form-input ${validationErrors.lastName ? 'error' : ''}`}
                                disabled={isLoading || isSubmitting}
                            />
                            {validationErrors.lastName && (
                                <span className="field-error">{validationErrors.lastName}</span>
                            )}
                        </div>
                    </div>
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="Digite seu email"
                            required
                            className={`form-input ${validationErrors.email ? 'error' : ''}`}
                            disabled={isLoading || isSubmitting}
                        />
                        {validationErrors.email && (
                            <span className="field-error">{validationErrors.email}</span>
                        )}
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Senha</label>
                        <div className="password-input-container">
                            <input
                                type={showPassword ? "text" : "password"}
                                id="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="Digite sua senha (mín. 6 caracteres)"
                                required
                                className={`form-input ${validationErrors.password ? 'error' : ''}`}
                                disabled={isLoading || isSubmitting}
                            />
                            <button
                                type="button"
                                className="password-toggle-btn"
                                onClick={() => setShowPassword(!showPassword)}
                                disabled={isLoading || isSubmitting}
                                aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
                            >
                                {showPassword ? (
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                                        <line x1="1" y1="1" x2="23" y2="23"/>
                                    </svg>
                                ) : (
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                                        <circle cx="12" cy="12" r="3"/>
                                    </svg>
                                )}
                            </button>
                        </div>
                        {validationErrors.password && (
                            <span className="field-error">{validationErrors.password}</span>
                        )}
                    </div>
                    <div className="form-group">
                        <label htmlFor="confirmPassword">Confirmar Senha</label>
                        <div className="password-input-container">
                            <input
                                type={showConfirmPassword ? "text" : "password"}
                                id="confirmPassword"
                                name="confirmPassword"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                placeholder="Confirme sua senha"
                                required
                                className={`form-input ${validationErrors.confirmPassword ? 'error' : ''}`}
                                disabled={isLoading || isSubmitting}
                            />
                            <button
                                type="button"
                                className="password-toggle-btn"
                                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                disabled={isLoading || isSubmitting}
                                aria-label={showConfirmPassword ? "Ocultar senha" : "Mostrar senha"}
                            >
                                {showConfirmPassword ? (
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                                        <line x1="1" y1="1" x2="23" y2="23"/>
                                    </svg>
                                ) : (
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                                        <circle cx="12" cy="12" r="3"/>
                                    </svg>
                                )}
                            </button>
                        </div>
                        {validationErrors.confirmPassword && (
                            <span className="field-error">{validationErrors.confirmPassword}</span>
                        )}
                    </div>
                    <button
                        type="submit"
                        className="auth-button"
                        disabled={isLoading || isSubmitting}
                    >
                        {isLoading || isSubmitting ? (
                            <span className="loading-spinner">
                                <span className="spinner"></span>
                            </span>
                        ) : (
                            'Criar Conta'
                        )}
                    </button>
                </form>
                <div className="auth-footer">
                    <p>
                        Já tem uma conta?{' '}
                        <Link to="/login" className="auth-link">
                            Entre aqui
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default RegisterForm;
