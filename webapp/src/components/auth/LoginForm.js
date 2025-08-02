import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './AuthForms.css';

function LoginForm() {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
    });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    
    const { login, isLoading, isAuthenticated, error, clearError } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated) {
            navigate('/dashboard');
        }
    }, [isAuthenticated, navigate]);

    useEffect(() => {
        clearError();
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

    // Sync error from context
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
        // Limpa erros quando o usuário digita
        if (errorMessage) {
            setErrorMessage('');
            clearError();
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        setErrorMessage(''); // Limpa erros anteriores

        const { email, password } = formData;

        try {
            const result = await login(email, password);
            
            if (result.success) {
                navigate('/dashboard');
            } else {
                // Exibe erro específico do servidor ou mensagem padrão
                const errorMsg = result.error || 'Erro no login. Verifique suas credenciais.';
                setErrorMessage(errorMsg);
            }
        } catch (err) {
            console.error('Erro no login:', err);
            setErrorMessage('Erro inesperado. Tente novamente.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <h1>Login</h1>
                    <p>Entre com suas credenciais para acessar o sistema</p>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                    {errorMessage && (
                        <div className="error-message">
                            <span className="error-icon">⚠️</span>
                            <span>{errorMessage}</span>
                        </div>
                    )}

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
                            className="form-input"
                            disabled={isLoading || isSubmitting}
                        />
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
                                placeholder="Digite sua senha"
                                required
                                className="form-input"
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
                            'Entrar'
                        )}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>
                        Não tem uma conta?{' '}
                        <Link to="/register" className="auth-link">
                            Cadastre-se aqui
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default LoginForm;
