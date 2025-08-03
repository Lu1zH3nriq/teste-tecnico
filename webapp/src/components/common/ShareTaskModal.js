import React from 'react';
import { FiX, FiUserPlus, FiUserMinus, FiMail, FiUser, FiStar } from 'react-icons/fi';
import './ShareTaskModal.css';

const ShareTaskModal = ({
    isOpen,
    onClose,
    task,
    sharedUsers = [],
    newUserEmail,
    onNewUserEmailChange,
    onAddUser,
    onRemoveUser,
    loading = false,
    user
}) => {
    if (!isOpen) return null;

    const handleSubmit = (e) => {
        e.preventDefault();
        onAddUser();
    };

    
    const taskOwner = task?.owner_info || user;
    const isCurrentUserOwner = task?.current_user_is_owner !== undefined ? task.current_user_is_owner : true;

    return (
        <div className="modal-overlay">
            <div className="modal-content share-modal">
                <div className="modal-header">
                    <h2>
                        <FiUser className="modal-icon" />
                        Compartilhar Tarefa
                    </h2>
                    <button onClick={onClose} className="modal-close-btn">
                        <FiX />
                    </button>
                </div>

                <div className="modal-body">
                    {task && (
                        <div className="task-info">
                            <h3 className="task-title">{task.title}</h3>
                            {task.description && (
                                <p className="task-description">{task.description}</p>
                            )}
                        </div>
                    )}

                    <div className="owner-section">
                        <h4 className="section-title">
                            <FiStar className="owner-icon" />
                            Proprietário da Tarefa
                        </h4>
                        <div className="owner-info">
                            <div className="user-item owner-item">
                                <div className="user-avatar">
                                    <FiUser />
                                </div>
                                <div className="user-details">
                                    <span className="user-name">
                                        {taskOwner?.first_name} {taskOwner?.last_name}
                                    </span>
                                    <span className="user-email">{taskOwner?.email}</span>
                                </div>
                                <span className="owner-badge">Proprietário</span>
                            </div>
                        </div>
                    </div>

                    {isCurrentUserOwner && (
                        <div className="add-user-section">
                            <h4 className="section-title">
                                <FiUserPlus className="add-icon" />
                                Compartilhar com Novo Usuário
                            </h4>
                            <form onSubmit={handleSubmit} className="add-user-form">
                                <div className="input-group">
                                    <FiMail className="input-icon" />
                                    <input
                                        type="email"
                                        placeholder="Digite o email do usuário..."
                                        value={newUserEmail}
                                        onChange={(e) => onNewUserEmailChange(e.target.value)}
                                        className="email-input"
                                        disabled={loading}
                                    />
                                    <button
                                        type="submit"
                                        className="add-user-btn"
                                        disabled={loading || !newUserEmail.trim()}
                                    >
                                        {loading ? (
                                            <div className="loading-spinner small"></div>
                                        ) : (
                                            <>
                                                <FiUserPlus />
                                                Adicionar
                                            </>
                                        )}
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}

                    <div className="shared-users-section">
                        <h4 className="section-title">
                            <FiUser className="users-icon" />
                            Usuários com Acesso ({sharedUsers.length})
                        </h4>
                        
                        {sharedUsers.length === 0 ? (
                            <div className="no-shared-users">
                                <FiUser className="empty-icon" />
                                <p>Esta tarefa ainda não foi compartilhada com outros usuários.</p>
                                <small>Use o campo acima para adicionar usuários.</small>
                            </div>
                        ) : (
                            <div className="shared-users-list">
                                {sharedUsers.map((sharedUser) => (
                                    <div key={sharedUser.id} className="user-item shared-item">
                                        <div className="user-avatar">
                                            <FiUser />
                                        </div>
                                        <div className="user-details">
                                            <span className="user-name">
                                                {sharedUser.first_name} {sharedUser.last_name}
                                            </span>
                                            <span className="user-email">{sharedUser.email}</span>
                                        </div>
                                        {isCurrentUserOwner && (
                                            <button
                                                onClick={() => onRemoveUser(sharedUser.id, `${sharedUser.first_name} ${sharedUser.last_name}`)}
                                                className="remove-user-btn"
                                                title="Remover acesso"
                                                disabled={loading}
                                            >
                                                <FiUserMinus />
                                            </button>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                <div className="modal-footer">
                    <button onClick={onClose} className="btn secondary">
                        Fechar
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ShareTaskModal;
