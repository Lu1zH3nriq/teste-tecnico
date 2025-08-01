import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Modal from '../common/Modal';
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
    const [showModal, setShowModal] = useState(false);
    const [modalConfig, setModalConfig] = useState({
        type: 'error',
        title: '',
        message: '',
    });
    
    const { register, isLoading, clearError, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated) {
            navigate('/dashboard');
        }
    }, [isAuthenticated, navigate]);

    useEffect(() => {
        clearError();
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

    useEffect(() => {
        setValidationErrors({});
    }, [formData]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value,
        }));
    };

    const validateForm = () => {
        const errors = {};
        if (!formData.firstName.trim()) {
            errors.firstName = 'Nome é obrigatório';
        }
        if (!formData.lastName.trim()) {
            errors.lastName = 'Sobrenome é obrigatório';
        }
        if (!formData.email) {
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

    const handleCloseModal = () => {
        setShowModal(false);
        if (modalConfig.type === 'success') {
            navigate('/login');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        const errors = validateForm();
        if (Object.keys(errors).length > 0) {
            setValidationErrors(errors);
            setIsSubmitting(false);
            return;
        }
        try {
            const { firstName, lastName, email, password, confirmPassword } = formData;
            const result = await register({
                first_name: firstName,
                last_name: lastName,
                email,
                password,
                confirm_password: confirmPassword,
            });
            if (result.success) {
                setModalConfig({
                    type: 'success',
                    title: 'Cadastro Realizado!',
                    message: `Olá ${firstName}! Sua conta foi criada com sucesso. Clique em OK para ir para a página de login e acessar sua conta com o email: ${email}`,
                });
                setShowModal(true);
            } else {
                let errorMessage = 'Ocorreu um erro inesperado durante o cadastro.';
                if (result.errors && Object.keys(result.errors).length > 0) {
                    const errorKeys = Object.keys(result.errors);
                    const firstErrorKey = errorKeys[0];
                    const errorValue = result.errors[firstErrorKey];
                    errorMessage = Array.isArray(errorValue) 
                        ? errorValue.join(', ')
                        : errorValue;
                }
                else if (result.error) {
                    if (typeof result.error === 'string') {
                        errorMessage = result.error;
                    } else if (result.error.email) {
                        errorMessage = Array.isArray(result.error.email) 
                            ? result.error.email.join(', ')
                            : result.error.email;
                    } else if (result.error.non_field_errors) {
                        errorMessage = Array.isArray(result.error.non_field_errors) 
                            ? result.error.non_field_errors.join(', ')
                            : result.error.non_field_errors;
                    } else {
                        const firstErrorKey = Object.keys(result.error)[0];
                        if (firstErrorKey) {
                            const errorValue = result.error[firstErrorKey];
                            errorMessage = Array.isArray(errorValue) ? errorValue.join(', ') : errorValue;
                        }
                    }
                }
                setModalConfig({
                    type: 'error',
                    title: 'Erro no Cadastro',
                    message: errorMessage,
                });
                setShowModal(true);
                if (result.errors) {
                    setValidationErrors(result.errors);
                }
            }
        } catch (err) {
            setModalConfig({
                type: 'error',
                title: 'Erro no Cadastro',
                message: 'Ocorreu um erro inesperado. Tente novamente em alguns instantes.',
            });
            setShowModal(true);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <h1>Cadastro</h1>
                    <p>Crie sua conta para começar a usar o sistema</p>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
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
                                aria-label={showConfirmPassword ? "Ocultar confirmação" : "Mostrar confirmação"}
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
                                Criando conta...
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
                            Faça login aqui
                        </Link>
                    </p>
                </div>
            </div>

            <Modal
                isOpen={showModal}
                onClose={handleCloseModal}
                type={modalConfig.type}
                title={modalConfig.title}
                message={modalConfig.message}
            />
        </div>
    );
}

export default RegisterForm;
