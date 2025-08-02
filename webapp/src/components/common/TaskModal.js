import React, { useState, useEffect } from 'react';
import { FiX, FiSave, FiLoader } from 'react-icons/fi';
import './TaskModal.css';

const TaskModal = ({
    isOpen,
    onClose,
    onSave,
    task = null,
    loading = false
}) => {
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        priority: 'medium',
        status: 'pending',
        due_date: '',
        tags: ''
    });

    const [errors, setErrors] = useState({});

    useEffect(() => {
        if (task) {
            setFormData({
                title: task.title || '',
                description: task.description || '',
                priority: task.priority || 'medium',
                status: task.status || 'pending',
                due_date: task.due_date ? task.due_date.split('T')[0] : '',
                tags: task.tags || ''
            });
        } else {
            setFormData({
                title: '',
                description: '',
                priority: 'medium',
                status: 'pending',
                due_date: '',
                tags: ''
            });
        }
        setErrors({});
    }, [task, isOpen]);

    const handleInputChange = (field, value) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));

        if (errors[field]) {
            setErrors(prev => ({
                ...prev,
                [field]: ''
            }));
        }
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.title.trim()) {
            newErrors.title = 'O título é obrigatório';
        }

        if (formData.title.length > 200) {
            newErrors.title = 'O título deve ter no máximo 200 caracteres';
        }

        if (formData.due_date) {
            const dueDate = new Date(formData.due_date);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            if (dueDate < today) {
                newErrors.due_date = 'A data de vencimento não pode ser no passado';
            }
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }

        const dataToSave = {
            ...formData,
            due_date: formData.due_date ? `${formData.due_date}T23:59:59` : null
        };

        onSave(dataToSave);
    };

    const handleClose = () => {
        if (!loading) {
            onClose();
        }
    };

    const handleBackdropClick = (e) => {
        if (e.target === e.currentTarget) {
            handleClose();
        }
    };

    if (!isOpen) return null;

    const priorityOptions = [
        { value: 'low', label: 'Baixa', color: '#6c757d' },
        { value: 'medium', label: 'Média', color: '#ffc107' },
        { value: 'high', label: 'Alta', color: '#fd7e14' },
        { value: 'urgent', label: 'Urgente', color: '#dc3545' }
    ];

    const statusOptions = [
        { value: 'pending', label: 'Pendente' },
        { value: 'in_progress', label: 'Em Progresso' },
        { value: 'completed', label: 'Concluído' },
        { value: 'cancelled', label: 'Cancelado' }
    ];

    return (
        <div className="modal-backdrop" onClick={handleBackdropClick}>
            <div className="modal-container">
                <div className="modal-header">
                    <h2>{task ? 'Editar Tarefa' : 'Nova Tarefa'}</h2>
                    <button 
                        className="modal-close-btn"
                        onClick={handleClose}
                        disabled={loading}
                    >
                        <FiX />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="modal-form">
                    <div className="form-grid">
                        <div className="form-group full-width">
                            <label htmlFor="title">
                                Título <span className="required">*</span>
                            </label>
                            <input
                                id="title"
                                type="text"
                                value={formData.title}
                                onChange={(e) => handleInputChange('title', e.target.value)}
                                placeholder="Digite o título da tarefa"
                                className={errors.title ? 'error' : ''}
                                disabled={loading}
                                maxLength={200}
                            />
                            {errors.title && <span className="error-message">{errors.title}</span>}
                        </div>

                        <div className="form-group full-width">
                            <label htmlFor="description">Descrição</label>
                            <textarea
                                id="description"
                                value={formData.description}
                                onChange={(e) => handleInputChange('description', e.target.value)}
                                placeholder="Descreva os detalhes da tarefa (opcional)"
                                rows={4}
                                disabled={loading}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="priority">Prioridade</label>
                            <select
                                id="priority"
                                value={formData.priority}
                                onChange={(e) => handleInputChange('priority', e.target.value)}
                                disabled={loading}
                            >
                                {priorityOptions.map(option => (
                                    <option key={option.value} value={option.value}>
                                        {option.label}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {task && (
                            <div className="form-group">
                                <label htmlFor="status">Status</label>
                                <select
                                    id="status"
                                    value={formData.status}
                                    onChange={(e) => handleInputChange('status', e.target.value)}
                                    disabled={loading}
                                >
                                    {statusOptions.map(option => (
                                        <option key={option.value} value={option.value}>
                                            {option.label}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        )}

                        <div className="form-group">
                            <label htmlFor="due_date">Data de Vencimento</label>
                            <input
                                id="due_date"
                                type="date"
                                value={formData.due_date}
                                onChange={(e) => handleInputChange('due_date', e.target.value)}
                                className={errors.due_date ? 'error' : ''}
                                disabled={loading}
                                min={new Date().toISOString().split('T')[0]}
                            />
                            {errors.due_date && <span className="error-message">{errors.due_date}</span>}
                        </div>

                        <div className="form-group full-width">
                            <label htmlFor="tags">Tags</label>
                            <input
                                id="tags"
                                type="text"
                                value={formData.tags}
                                onChange={(e) => handleInputChange('tags', e.target.value)}
                                placeholder="Digite as tags separadas por vírgula (ex: trabalho, urgente, projeto)"
                                disabled={loading}
                            />
                            <small className="help-text">
                                Use vírgulas para separar múltiplas tags
                            </small>
                        </div>
                    </div>

                    <div className="modal-actions">
                        <button
                            type="button"
                            onClick={handleClose}
                            className="btn btn-secondary"
                            disabled={loading}
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <FiLoader className="spinning" />
                                    Salvando...
                                </>
                            ) : (
                                <>
                                    <FiSave />
                                    {task ? 'Atualizar' : 'Criar'} Tarefa
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default TaskModal;
