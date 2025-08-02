import React from 'react';
import { FiCheck, FiX, FiAlertTriangle, FiInfo } from 'react-icons/fi';
import './ConfirmationModal.css';

const ConfirmationModal = ({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title, 
  message, 
  type = 'confirm',
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  showCancel = true,
  loading = false
}) => {
  if (!isOpen) return null;

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <FiCheck className="modal-icon success" />;
      case 'error':
        return <FiX className="modal-icon error" />;
      case 'confirm':
        return <FiAlertTriangle className="modal-icon warning" />;
      case 'info':
        return <FiInfo className="modal-icon info" />;
      default:
        return <FiInfo className="modal-icon info" />;
    }
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="confirmation-modal-overlay" onClick={handleBackdropClick}>
      <div className={`confirmation-modal ${type}`}>
        <div className="confirmation-modal-header">
          {getIcon()}
          <h3>{title}</h3>
        </div>
        
        <div className="confirmation-modal-body">
          <p>{message}</p>
        </div>
        
        <div className="confirmation-modal-footer">
          {showCancel && (
            <button 
              className="confirmation-modal-btn cancel" 
              onClick={onClose}
              disabled={loading}
            >
              {cancelText}
            </button>
          )}
          <button 
            className="confirmation-modal-btn confirm" 
            onClick={onConfirm || onClose}
            disabled={loading}
          >
            {loading ? (
              <div className="confirmation-modal-loading">
                <div className="confirmation-modal-spinner"></div>
                Processando...
              </div>
            ) : (
              confirmText
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
