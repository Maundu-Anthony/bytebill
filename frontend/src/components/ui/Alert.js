import React from 'react';

export const Alert = ({ 
  children, 
  type = 'info', 
  className = '', 
  ...props 
}) => {
  const baseClasses = 'px-4 py-3 rounded-md border';
  
  const types = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  };
  
  const classes = `${baseClasses} ${types[type]} ${className}`;
  
  return (
    <div 
      className={classes}
      role="alert"
      {...props}
    >
      {children}
    </div>
  );
};
