import React from 'react';

export const Input = ({ 
  type = 'text', 
  className = '', 
  error = false,
  ...props 
}) => {
  const baseClasses = 'block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-1 sm:text-sm';
  
  const normalClasses = 'border-gray-300 focus:ring-blue-500 focus:border-blue-500';
  const errorClasses = 'border-red-300 focus:ring-red-500 focus:border-red-500';
  
  const classes = `${baseClasses} ${error ? errorClasses : normalClasses} ${className}`;
  
  return (
    <input 
      type={type}
      className={classes}
      {...props}
    />
  );
};
