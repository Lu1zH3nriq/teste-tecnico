import React, { useEffect } from 'react';
import './Modal.css';

function Modal({ 
    isOpen, 
    onClose, 
    title, 
    message, 
    type = 'info', 
    showCloseButton = true,
    children 
}) {
    useEffect(() => {
        const handleEscape = (e) => {
            if (e.key === 'Escape' && isOpen) {
                onClose();
            }
        };

        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }

        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.body.style.overflow = 'unset';
        };
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    const getIcon = () => {
        switch (type) {
            case 'success':
                return '✓';
            case 'error':
                return '✕';
            case 'warning':
                return '⚠';
            default:
                return 'ℹ';
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div 
                className={`modal-content modal-${type}`} 
                onClick={(e) => e.stopPropagation()}
            >
                <div className="modal-header">
                    <div className="modal-icon">
                        {getIcon()}
                    </div>
                    {title && <h3 className="modal-title">{title}</h3>}
                    {showCloseButton && (
                        <button 
                            className="modal-close" 
                            onClick={onClose}
                            aria-label="Fechar modal"
                        >
                            ×
                        </button>
                    )}
                </div>
                
                <div className="modal-body">
                    {message && <p className="modal-message">{message}</p>}
                    {children}
                </div>
                
                <div className="modal-footer">
                    <button 
                        className={`modal-button modal-button-${type}`} 
                        onClick={onClose}
                    >
                        OK
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Modal;
